import plc_comm.connection as conn


# ================= WRITE BIT =================
def write_bit(device, value):
    client = conn.get_client()
    if client is None:
        return False

    with conn.lock:
        try:
            client.batchwrite_bitunits(device, [value])
            return True

        except Exception as e:
            print("WRITE BIT ERROR:", e)
            return False


# ================= WRITE PULSE =================
def write_pulse(device):
    client = conn.get_client()
    if client is None:
        return False

    with conn.lock:
        try:
            client.batchwrite_bitunits(device, [1])
            client.batchwrite_bitunits(device, [0])
            return True

        except Exception as e:
            print("WRITE PULSE ERROR:", e)
            return False