from pymcprotocol import Type3E
import threading

plc = Type3E()
connected = False
lock = threading.Lock()

def connect_plc(ip="192.168.1.10", port=5011):
    global connected
    try:
        plc.setaccessopt(commtype="binary")
        plc.connect(ip, port)
        connected = True
        return True
    except:
        connected = False
        return False

def read_words():
    if not connected:
        return None

    with lock:
        try:
            return {
                "cycle": plc.batchread_wordunits("D6", 1)[0],
                "in": plc.batchread_wordunits("D10", 1)[0],
                "ok": plc.batchread_wordunits("D14", 1)[0],
                "ng": plc.batchread_wordunits("D16", 1)[0],
                "out": plc.batchread_wordunits("D12", 1)[0],
                "rate": plc.batchread_wordunits("D20", 1)[0],  # 👈 Lỗi đã gom
            }
        except:
            return None

def read_fault():
    if not connected:
        return False, False

    with lock:
        try:
            plc_fault = plc.batchread_bitunits("Y10", 1)[0]
            servo_fault = plc.batchread_bitunits("Y11", 1)[0]
            return plc_fault, servo_fault
        except:
            return False, False

def set_auto():
    if not connected: 
        return
    with lock:
        plc.batchwrite_bitunits("X0300", [1])

def set_manual():
    if not connected: 
        return
    with lock:
        plc.batchwrite_bitunits("X0301", [1])

def rotate_table():
    if not connected: 
        return
    with lock:
        plc.batchwrite_bitunits("M5001", [1])

def read_device(dev_name, size=1):
    if not connected:
        return None
    with lock:
        try:
            if dev_name.startswith('D'):
                return plc.batchread_wordunits(dev_name, size)
            else:
                return plc.batchread_bitunits(dev_name, size)
        except Exception as e:
            print(f"Error reading {dev_name}: {e}")
            return None

def write_device(dev_name, values):
    if not connected:
        return False
    with lock:
        try:
            if dev_name.startswith('D'):
                plc.batchwrite_wordunits(dev_name, values)
            else:
                plc.batchwrite_bitunits(dev_name, values)
            return True
        except Exception as e:
            print(f"Error writing to {dev_name}: {e}")
            return False