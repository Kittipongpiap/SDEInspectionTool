'''
 JLink Function Command 
 (c) All Right Reserved SDE Inspection Software 2024
'''

import subprocess
import time

mac_id = "" 
_mac_id_cache = None
_mac_id_cache_time = 0
_MAC_ID_CACHE_DURATION = 2.0  # Cache for 2 seconds

def recover() :
    recover = "nrfjprog --recover --family NRF52  \n"
    try:
    # Execute the command
        subprocess.run(recover, shell=True, check=True)
        print("Command executed successfully.")
    except subprocess.CalledProcessError as e:
        print("Error executing command:", e)

def reset() :
    reset = "nrfjprog --reset --family NRF52  \n"
    try:
    # Execute the command
        subprocess.run(reset, shell=True, check=True)
        print("Command executed successfully.")
    except subprocess.CalledProcessError as e:
        print("Error executing command:", e)

def eraseall() :
    eraseall = "nrfjprog -f NRF52 --eraseall \n"
    try:
    # Execute the command
        subprocess.run(eraseall, shell=True, check=True)
        print("Command executed successfully.")
    except subprocess.CalledProcessError as e:
        print("Error executing command:", e)
        pass


def protection() :
    protection = "nrfjprog -f NRF52 --rbp ALL  \n"
    try:
    # Execute the command
        subprocess.run(protection, shell=True, check=True)
        print("Command executed successfully.")
    except subprocess.CalledProcessError as e:
        print("Error executing command:", e)
    pass

def mac_id_check(force_refresh=False):
    """
    Read MAC ID from device with smart caching.
    
    Args:
        force_refresh: If True, bypass cache and read from device
        
    Returns:
        MAC ID string (e.g., "F4CE36XXXXXX")
    """
    global _mac_id_cache, _mac_id_cache_time, mac_id
    
    # Check cache if not forcing refresh
    current_time = time.time()
    if not force_refresh and _mac_id_cache and (current_time - _mac_id_cache_time) < _MAC_ID_CACHE_DURATION:
        print(f"[mac_id_check] Using cached MAC ID: {_mac_id_cache} (age: {current_time - _mac_id_cache_time:.2f}s)")
        return _mac_id_cache
    
    # Read from device
    command = "nrfjprog --memrd 0x10000060 --n 8 --family nrf52"
    mac_id_local = ""

    try:
        result = subprocess.run(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result)
        mac_id_local = "F4CE36" + \
            result.stdout.split(" ")[1][6:] + result.stdout.split(" ")[2]
        print(f"[mac_id_check] Read MAC ID from device: {mac_id_local}")
        
        # Update cache
        _mac_id_cache = mac_id_local
        _mac_id_cache_time = current_time
        mac_id = mac_id_local
    except Exception as e:
        print("Cant Read macID with nrfjprog")
        print("An error occurred:", e)
        # Return cached value if available, even if stale
        if _mac_id_cache:
            print(f"[mac_id_check] Using stale cache due to error: {_mac_id_cache}")
            return _mac_id_cache
            
    return mac_id_local

def get_mac_id():
    """Return the last read MAC ID (may be from cache)"""
    return mac_id

def clear_mac_id_cache():
    """Force next mac_id_check() to read from device"""
    global _mac_id_cache, _mac_id_cache_time
    _mac_id_cache = None
    _mac_id_cache_time = 0
    print("[mac_id_check] Cache cleared")


def power_on():
    """Attempt to power on using available J-Link executables.

    Tries common executables ('JLinkExe', 'JLink', 'jlink') and sends a small
    commander script via stdin. Returns True on success, False otherwise.
    """
    executables = ["JLinkExe", "JLink", "jlink"]
    command = "power on\nexit\n"
    for exe in executables:
        try:
            proc = subprocess.run([exe], input=command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
            print(f"{exe} returncode={proc.returncode}")
            if proc.stdout:
                print(proc.stdout)
            if proc.stderr:
                print(proc.stderr)
            if proc.returncode == 0:
                return True
        except FileNotFoundError:
            # executable not found, try next
            continue
        except subprocess.TimeoutExpired:
            print(f"{exe} timed out while powering on")
            continue
        except Exception as e:
            print(f"Error running {exe}: {e}")
            continue
    print("Failed to power on: no J-Link executable succeeded")
    return False


def power_off():
    """Attempt to power off using available J-Link executables.

    Similar approach to power_on(); returns True on success.
    """
    executables = ["JLinkExe", "JLink", "jlink"]
    command = "power off\nexit\n"
    for exe in executables:
        try:
            proc = subprocess.run([exe], input=command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
            print(f"{exe} returncode={proc.returncode}")
            if proc.stdout:
                print(proc.stdout)
            if proc.stderr:
                print(proc.stderr)
            if proc.returncode == 0:
                return True
        except FileNotFoundError:
            continue
        except subprocess.TimeoutExpired:
            print(f"{exe} timed out while powering off")
            continue
        except Exception as e:
            print(f"Error running {exe}: {e}")
            continue
    print("Failed to power off: no J-Link executable succeeded")
    return False


def flash_program(hex_name):
    recover()
    eraseall()
    erase_command = 'nrfjprog -e'
    result = subprocess.run(
        erase_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print(result)
    # Define the nrfjprog command you want to run
    command = f"nrfjprog -f nrf52 --program ./{hex_name} --verify --reset"
    #command = f"nrfjprog -f nrf52 --program ./{hex_name} --sectorerase"
    print(command)

    is_ok = 0

    # Run the command and capture the return code
    try:
        result = subprocess.run(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result.stdout)
        if "Verify file - Done verifying" in result.stdout:
            is_ok = 1
        else:
            is_ok = 0

    except Exception as e:
        print("Cant Read macID with jprog")
        print("An error occurred:", e)
    return is_ok


if __name__ == "__main__":
    mac_id_check()
    pass

