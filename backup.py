import pylink
import time

DEVICE = 'nRF52840_xxAA'

jlink = pylink.JLink()
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

print("Connecting to target via SWD...")
jlink.open()
if not jlink.connected():
    time.sleep(1)
    jlink.open()
    if not jlink.connected():
        raise RuntimeError("Failed to connect to J-Link")
if(jlink.tif != pylink.enums.JLinkInterfaces.SWD):  # 2 = SWD
    jlink.set_tif(pylink.enums.JLinkInterfaces.SWD)
jlink.connect(DEVICE, speed=4000)  # 4 MHz SWD

# Start RTT
jlink.rtt_start()

# Wait for RTT control block to be found
print("Waiting for RTT to start...")
for _ in range(100):  # ~10 seconds timeout
    try:
        num_up_bufs = jlink.rtt_get_num_up_buffers()
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
        # Try reading from channel 0 (up-buffer 0)
        try:
            data = jlink.rtt_read(0, 1024)
            if data:


                s = _normalize_rtt_data(data)
                if s:
                    print(s, end='', flush=True)
        except pylink.JLinkRTTException:
            # Happens if RTT stops or target resets
            time.sleep(0.5)
        time.sleep(0.01)
except KeyboardInterrupt:
    print("\nStopping RTT.")
finally:
    jlink.rtt_stop()
    jlink.close()


