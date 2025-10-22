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
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from PyQt5.QtGui import QTextCursor

# Define the serial port and baudrate
jpylink = pylink.JLink()

def testing_event(ui):
    thr = threading.Thread(target=ReadSerial_Controller, args=[ui])
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
def ReadSerial_Controller(ui):
    # message = "Inspection In Progress, PRESS S1"
    # comperator.alert_helper.show_alert_signal.emit(message)
    # Actuator Variable ====================================
    act_stack = []
    curr_stack = []
    # Actuator Variable ====================================
    scd_stack = []
    pm_stack = []
    device_type = 'Incomming Controlller Board'
    DEVICE = 'nRF52840_xxAA'
    flag_model3=True

    print("Connecting to target via SWD...")
    jpylink.open()
    if not jpylink.connected():
        jpylink.close()
        time.sleep(1)
        jpylink.open()
        if not jpylink.connected():
            raise RuntimeError("Failed to connect to J-Link")
    if(jpylink.tif != pylink.enums.JLinkInterfaces.SWD):  # 2 = SWD
        jpylink.set_tif(pylink.enums.JLinkInterfaces.SWD)
    jpylink.connect(DEVICE, speed=4000)  # 4 MHz SWD
    print("target reset")
    print(jpylink.reset(ms=100,halt=False))

    # Start RTT
    jpylink.rtt_start()
    print("Waiting for RTT to start...")
    for _ in range(100):  # ~10 seconds timeout
        try:
            num_up_bufs = jpylink.rtt_get_num_up_buffers()
            if num_up_bufs > 0:
                break
        except pylink.JLinkRTTException:
            pass
        time.sleep(0.1)
    else:
        raise RuntimeError("RTT not found! Make sure firmware enables SEGGER_RTT_Init()")

    print("RTT connected! Reading logs...\n")
    try:
        while True:
            ser = jpylink.rtt_read(0, 1024)
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

                        if flag_model3:
                            print(f"Raw Data PM {raw_data}")
                            pm_array = raw_data.split(',')
                            #print(pm_array)
                            pm_array = pm_array[1:]
                            for pm in pm_array :
                                #print(pm)  
                                pm_pack = struct.pack('I', int(pm))
                                print(pm_pack)
                                pm_float = struct.unpack('f', pm_pack)[0]
                                pm_float = int(pm_float)
                                pm_stack.append(pm_float)
                            flag_model3 = False
                            #print("PM========================")
                            #print(pm_stack)

                        if not flag_model3 :
                            print(f"Raw Data scd {raw_data}")
                            scd_array = raw_data.split(',')
                            #print(scd_array)
                            scd_array = scd_array[1:]
                            #print("SCD========================")
                            #print(scd_array)
                            for scd in scd_array :
                                #print(scd)  
                                scd_pack = struct.pack('I', int(scd))
                                print(scd_pack)
                                scd_float = struct.unpack('f', scd_pack)[0]
                                scd_float = int(scd_float)
                                scd_stack.append(scd_float)
                            #print(scd_stack)
                            flag_model3 = True
                            print("End Sensor")
                            end_process_(ui,device_type,pm_stack,scd_stack)
                            
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
                    end_process_act = len(curr_stack)
                # Actuator Controller End Message ================================
                    #if device_type.startswith('Actuator Controller 3CH') :
                    if end_process_act == 5 :
                        print("End Level")
                        end_process_(ui,device_type,act_stack,curr_stack)
                        break
    except pylink.JLinkRTTException as e:
        print("Error opening or reading serial port:", e)
        if jpylink.connected():
            jpylink.close()

    finally:
        # Close the serial port
        if jpylink.connected():
            jpylink.close()

def readline(data):
    while True:
        if data:
            buf += data
            if b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                return line.decode('utf-8', errors='ignore').strip()
        else:
            time.sleep(0.01)
            
def end_process_(ui,controller_type,first_stack,second_stack):
        mac_id = jlink.get_mac_id()
        print(controller_type)
        for first in first_stack :
            print(first)
        for second in second_stack :
            print(second)
        #-------------------------------------------------------------------------------
        comperator.Comparator(ui,mac_id,controller_type,first_stack,second_stack)
        status = comperator.return_status()
        #-------------------------------------------------------------------------------
        if status.startswith("GOOD") :
            uif.afterLife_event(ui)
            ui.flashStatusLabel.setText(
                    "Status : <span style=\"color:ORANGE\">Production Process Inprogress</span></p>")
        elif status.startswith("NG") :
            jlink.protection()
            jlink.recover()
            ui.flashStatusLabel.setText(
                    "Status : <span style=\"color:green\">Process Complete </span></p>")
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
        jpylink = pylink.JLink()
    
        jpylink.open()
        if not jpylink.connected():
            time.sleep(1)
            jpylink.open()
            if not jpylink.connected():
                raise RuntimeError("Failed to connect to J-Link")
        if(jpylink.tif != pylink.enums.JLinkInterfaces.SWD):  # 2 = SWD
            jpylink.set_tif(pylink.enums.JLinkInterfaces.SWD)
        jpylink.connect(DEVICE, speed=4000)  # 4 MHz SWD


    # Start RTT
        jpylink.rtt_start()
        print("Waiting for RTT to start...")
        for _ in range(100):  # ~10 seconds timeout
            try:
                num_up_bufs = jpylink.rtt_get_num_up_buffers()
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

    def read_from_port(self):
        try:
            ser = jpylink.rtt_read(0, 1024)
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

        jpylink.close()

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