'''
 Read Serial Port For Inspection Data From All Controller Board
 (c) All Right Reserved SDE Inspection Software 2024
'''

# Actuator can fix current tororent value 
# Sensor Controller Should be read form master board 

import serial
import struct
from utils import *
import threading
import JLink.jlink as jlink
import JLink.ui_function as uif
import JLink.db_controller as db_mcu
import JLink.limitter as comperator
import time
import pylink
from PyQt5.QtCore import QObject, pyqtSignal, QThread, QMetaObject, Qt
from PyQt5.QtGui import QTextCursor
from utils import get_logger

logger = get_logger(__name__)



# Main-thread helper for running Comparator and UI updates safely
class MainThreadHelper(QObject):
    process_complete = pyqtSignal(object, str, str, list, list)
    
    def __init__(self):
        super().__init__()
        # Use Qt.UniqueConnection to prevent duplicate connections if module reloads
        self.process_complete.connect(self._handle_process_complete, Qt.UniqueConnection)
    
    def _handle_process_complete(self, ui, mac_id, controller_type, first_stack, second_stack):
        """Runs in main thread via queued connection"""
        logger.debug(f"[MainThreadHelper] Processing {controller_type} with mac_id {mac_id}")
        comperator.Comparator(ui, mac_id, controller_type, first_stack, second_stack)
        status = comperator.return_status()
        if status.startswith("GOOD"):
            uif.afterLife_event(ui)
            ui.flashStatusLabel.setText(
                "Status : <span style=\"color:ORANGE\">Production Process Inprogress</span></p>")
        elif status.startswith("NG"):
            jlink.protection()
            jlink.recover()
            ui.flashStatusLabel.setText(
                "Status : <span style=\"color:green\">Process Complete </span></p>")

# Create a global instance in the main thread (when module loads)
_main_thread_helper = MainThreadHelper()


def _target_connect_and_verify(link: pylink.JLink, device: str, speed: int = 4000, retries: int = 5, wait_s: float = 0.5, speed_fallbacks=None) -> bool:
    """Connect to target over SWD and verify by reading CPUID.

    Tries the given speed and optional fallback speeds. Returns True when
    connected and verified; False after exhausting retries and speeds.
    """
    speeds = [speed]
    if isinstance(speed_fallbacks, (list, tuple)):
        speeds.extend([s for s in speed_fallbacks if s not in speeds])

    for spd in speeds:
        logger.info(f"[J-Link] Trying SWD speed {spd} kHz")
        for attempt in range(1, retries + 1):
            try:
                if not link.connected():
                    try:
                        link.open()
                    except Exception:
                        time.sleep(wait_s)
                        continue
                # Ensure SWD interface
                try:
                    if link.tif != pylink.enums.JLinkInterfaces.SWD:
                        link.set_tif(pylink.enums.JLinkInterfaces.SWD)
                except Exception:
                    pass

                # Attach to target
                try:
                    link.connect(device, speed=spd)
                except Exception:
                    time.sleep(wait_s)
                    continue

                # Verify by reading CPUID (SCB CPUID at 0xE000ED00)
                try:
                    vals = link.memory_read32(0xE000ED00, 1)
                    if isinstance(vals, (list, tuple)) and len(vals) == 1:
                        cpuid = int(vals[0]) & 0xFFFFFFFF
                        logger.info(f"[J-Link] Connected. CPUID=0x{cpuid:08X} @ {spd} kHz")
                        return True
                except Exception:
                    pass
            except Exception as e:
                logger.warning(f"[J-Link] Connect verify attempt {attempt}/{retries} at {spd} kHz failed: {e}")

            # Backoff and try again with a clean link
            try:
                if link.connected():
                    link.close()
            except Exception:
                pass
            time.sleep(wait_s)

    return False

def testing_event(ui, mac_id=None):
    """
    Start inspection with optional pre-read MAC ID to avoid duplicate reads.
    
    Args:
        ui: UI object
        mac_id: Optional MAC ID string (if already read by caller)
    """
    thr = threading.Thread(target=ReadSerial_Controller, args=[ui, mac_id])
    thr.start() 
    ui.flashStatusLabel.setText(
            "Status : <span style=\"color:orange\">Inspection In Progress, PRESS S1 </span></p>")
    
def _normalize_rtt_data(d):
# bytes-like
    try:
        if isinstance(d, (bytes, bytearray)):
            return d.decode('utf-8', errors='ignore')
        # list of ints or bytes
        if isinstance(d, list):
            # all ints
            if all(isinstance(x, int) for x in d):
                return bytes(d).decode('utf-8', errors='ignore')
            # mix of bytes/bytearray/ints/str
            parts = []
            for x in d:
                if isinstance(x, (bytes, bytearray)):
                    parts.append(bytes(x))
                elif isinstance(x, int):
                    parts.append(bytes([x]))
                elif isinstance(x, str):
                    parts.append(x.encode('utf-8'))
                else:
                    parts.append(str(x).encode('utf-8'))
            return b''.join(parts).decode('utf-8', errors='ignore')
        # str
        if isinstance(d, str):
            return d
        # fallback
        return str(d)
    except Exception:
        try:
            return str(d)
        except Exception:
            return ''

# Read Serial Port =====================================
def ReadSerial_Controller(ui, mac_id=None):
    """
    Read RTT data and process inspection results.
    
    Args:
        ui: UI object
        mac_id: Optional MAC ID (if already read by caller, avoids duplicate read)
    """
    # Actuator Variable ====================================
    act_stack = []
    curr_stack = []
    # Actuator Variable ====================================
    scd_stack = []
    pm_stack = []
    device_type = 'Incomming Controlller Board'
    DEVICE = 'nRF52840_xxAA'
    flag_model3=True
    
    # Get MAC ID - use provided one or read from device (with caching)
    if not mac_id:
        mac_id = jlink.mac_id_check()
    logger.info(f"Device MAC ID: {mac_id}")

    logger.info("Connecting to target via SWD...")
    # Create a local J-Link instance for this thread
    link = pylink.JLink()
    # Optional power on pulse via J-Link commander (best-effort)
    try:
        jlink.power_on()
    except Exception:
        pass

    ok = _target_connect_and_verify(
        link,
        DEVICE,
        speed=4000,
        retries=3,
        wait_s=0.5,
        speed_fallbacks=[2000, 1000, 400, 100]
    )
    if not ok:
        logger.error("Unable to connect to target after retries.")
        try:
            if link.connected():
                link.close()
        except Exception:
            pass
        # Update UI and exit gracefully instead of raising
        try:
            ui.flashStatusLabel.setText(
                "Status : <span style=\"color:RED\">Failed to connect to J-Link target. Check power, SWD, and try again.</span></p>")
        except Exception:
            pass
        return

    # Try a reset; if it fails due to target disconnect, attempt one reconnect and retry
    logger.debug("target reset")
    try:
        logger.debug(str(link.reset(ms=100, halt=False)))
    except Exception as e:
        logger.warning(f"Reset failed: {e}. Attempting reconnect...")
        ok2 = _target_connect_and_verify(link, DEVICE, speed=4000, retries=2, wait_s=0.5, speed_fallbacks=[2000, 1000, 400, 100])
        if ok2:
            logger.info("Reconnected. Retrying reset...")
            logger.debug(str(link.reset(ms=100, halt=False)))
        else:
            try:
                ui.flashStatusLabel.setText(
                    "Status : <span style=\"color:RED\">J-Link reset failed. Check target connection.</span></p>")
            except Exception:
                pass
            return

    # Start RTT
    link.rtt_start()
    logger.debug("Waiting for RTT to start...")
    for _ in range(100):  # ~10 seconds timeout
        try:
            num_up_bufs = link.rtt_get_num_up_buffers()
            if num_up_bufs > 0:
                break
        except pylink.JLinkRTTException:
            pass
        time.sleep(0.1)
    else:
        raise RuntimeError("RTT not found! Make sure firmware enables SEGGER_RTT_Init()")

    logger.info("RTT connected! Reading logs...")
    processing_complete = False
    try:
        while True:
            if processing_complete:
                logger.debug("Processing complete, stopping...")
                break
                
            ser = link.rtt_read(0, 1024)
            s = _normalize_rtt_data(ser)
            if s:
                lines = s.splitlines()
                for line in lines:
                    line = line.strip()
            
    # the received Sensor Data ================================================================================================
                    if "<info> app: sensor_type,data_1,data_2,data_3: 3" in line :
                        device_type = 'Sensor Controller'
                        sensor_data = line.strip()
                        raw_data = sensor_data[46:]
                        logger.debug("line sensor data: %s", line)

                        if flag_model3:
                            logger.debug(f"Raw Data PM {raw_data}")
                            pm_array = raw_data.split(',')
                            #print(pm_array)
                            pm_array = pm_array[1:]
                            for pm in pm_array :
                                #print(pm)  
                                pm_pack = struct.pack('I', int(pm))
                                logger.debug(str(pm_pack))
                                pm_float = struct.unpack('f', pm_pack)[0]
                                pm_float = int(pm_float)
                                pm_stack.append(pm_float)
                            flag_model3 = False
                            #print("PM========================")
                            #print(pm_stack)

                        elif not flag_model3 :
                            logger.debug(f"Raw Data scd {raw_data}")
                            scd_array = raw_data.split(',')
                            #print(scd_array)
                            scd_array = scd_array[1:]
                            #print("SCD========================")
                            #print(scd_array)
                            for scd in scd_array :
                                #print(scd)  
                                scd_pack = struct.pack('I', int(scd))
                                logger.debug(str(scd_pack))
                                scd_float = struct.unpack('f', scd_pack)[0]
                                scd_float = int(scd_float)
                                scd_stack.append(scd_float)
                            #print(scd_stack)
                            flag_model3 = True
                            logger.debug("End Sensor")
                            end_process_(ui, mac_id, device_type, pm_stack, scd_stack)
                            processing_complete = True
                            break

        # the received Actuator Data ================================================================================================
                    # Level Switch ================================
                    elif "<info> app: Relay output'" in line :
                        device_type = 'Actuator Controller 3CH'
                        act_data = line.strip()
                        act_stat = act_data[25:]
                        act_cn_lv = len(act_stack)
                        if act_cn_lv < 5 :
                            act_stack.append(act_stat)

                    # Current ======================================= 
                    elif "<info> app: Current output'" in line :
                        device_type = 'Actuator Controller 3CH'
                        act_curr = line.strip()
                        act_amp = act_curr[27:]
                        act_cn = len(curr_stack)
                        if act_cn < 5 :
                            curr_stack.append(act_amp)

                #====================================================
                # Actuator Controller End Message ================================
                # Check AFTER all line processing is done, not inside the elif block
                end_process_act = len(curr_stack)
                if end_process_act == 5 :
                    logger.debug("End Level")
                    end_process_(ui, mac_id, device_type, act_stack, curr_stack)
                    processing_complete = True
                    break
    except pylink.JLinkRTTException as e:
        logger.exception("Error opening or reading serial port: %s", e)
        if link.connected():
            link.close()

    finally:
        # Close the serial port
        if link.connected():
            link.close()

def readline(data):
    while True:
        if data:
            buf += data
            if b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                return line.decode('utf-8', errors='ignore').strip()
        else:
            time.sleep(0.01)
            
def end_process_(ui, mac_id, controller_type, first_stack, second_stack):
    logger.debug(
        f"[end_process_] Called for {controller_type} with MAC ID: {mac_id}; "
        f"first_stack_len={len(first_stack)}, second_stack_len={len(second_stack)}"
    )
    #-------------------------------------------------------------------------------
    # Emit signal to run Comparator and UI updates in main thread
    logger.debug("[end_process_] Emitting process_complete signal")
    _main_thread_helper.process_complete.emit(ui, mac_id, controller_type, first_stack, second_stack)
#==================================================================================================================================================================================
# Flag to control the reading process
reading = False
# Create a QObject class to handle signals
class SerialReader(QObject):
    new_data = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, port, baud_rate):
        DEVICE = 'nRF52840_xxAA'
        super().__init__()
        self.jlink = pylink.JLink()
    
        self.jlink.open()
        if not self.jlink.connected():
            time.sleep(1)
            self.jlink.open()
            if not self.jlink.connected():
                raise RuntimeError("Failed to connect to J-Link")
        if(self.jlink.tif != pylink.enums.JLinkInterfaces.SWD):  # 2 = SWD
            self.jlink.set_tif(pylink.enums.JLinkInterfaces.SWD)
        self.jlink.connect(DEVICE, speed=4000)  # 4 MHz SWD


    # Start RTT
        self.jlink.rtt_start()
        logger.debug("Waiting for RTT to start...")
        for _ in range(100):  # ~10 seconds timeout
            try:
                num_up_bufs = self.jlink.rtt_get_num_up_buffers()
                if num_up_bufs > 0:
                    break
            except pylink.JLinkRTTException:
                pass
            time.sleep(0.1)
        else:
            raise RuntimeError("RTT not found! Make sure firmware enables SEGGER_RTT_Init()")

    def start_reading(self):
        self.reading = True
        self.thread = QThread()
        self.moveToThread(self.thread)
        self.thread.started.connect(self.read_from_port)
        self.thread.start()

    def stop_reading(self):
        self.reading = False
        if self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
        try:
            if self.jlink and self.jlink.connected():
                self.jlink.close()
        except Exception:
            pass

    def read_from_port(self):
        try:
            ser = self.jlink.rtt_read(0, 1024)
            s = _normalize_rtt_data(ser)
        except Exception as e:
            self.error_occurred.emit(f"Error opening serial port: {e}")
            return
        
        while self.reading:
            try:
                self.new_data.emit(s)
                time.sleep(0.005)  # Sleep for 50 milliseconds
            except Exception as e:
                self.error_occurred.emit(f"Error reading from serial port: {e}")
                break

        try:
            if self.jlink and self.jlink.connected():
                self.jlink.close()
        except Exception:
            pass

# Function to start reading
def start_reading(ui):
    global serial_reader
    serial_port = ui.uart_portBox.currentText()
    # Determine baud rate from UI if available, otherwise default to 115200
    try:
        if hasattr(ui, 'uart_baudBox'):
            baud_rate = int(ui.uart_baudBox.currentText())
        elif hasattr(ui, 'uart_baud'):
            baud_rate = int(ui.uart_baud)
        else:
            baud_rate = 115200
    except Exception:
        baud_rate = 115200

    serial_reader = SerialReader(serial_port, baud_rate)
    # Connect directly to the QTextEdit.append slot so PyQt will queue the
    # calls into the GUI thread. Avoid lambdas which would run in the
    # worker thread.
    try:
        serial_reader.new_data.connect(ui.serial_monitor.append)
        serial_reader.error_occurred.connect(ui.serial_monitor.append)
    except Exception:
        # Fallback to previous behavior
        serial_reader.new_data.connect(lambda line: update_ui(ui, line))
        serial_reader.error_occurred.connect(lambda error: ui.serial_monitor.append(error))
    serial_reader.start_reading()
    ui.serial_monitor.clear()
    ui.serial_monitor.append("Started reading from the serial port.")

# Function to stop reading
def stop_reading(ui):
    global serial_reader
    if serial_reader.reading:
        serial_reader.stop_reading()
        ui.serial_monitor.append("Stopped reading from the serial port.")

# Function to update the UI
def update_ui(ui, line):
    ui.serial_monitor.append(line)
    ui.serial_monitor.moveCursor(QTextCursor.End)
    ui.serial_monitor.ensureCursorVisible()
#=============================================================================================================================================================================================================================================================================================================================================================================================