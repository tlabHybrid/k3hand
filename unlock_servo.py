import serial

def unlock_servo():
    k3 = serial.Serial('COM5', baudrate=115200,parity=serial.PARITY_NONE, timeout=1)
    txCmd = [0x58, 0x1B, 0x00, 0x01, 0x01, 0x00, 0x75, 0x16]

    print(txCmd)

    k3.write(txCmd)
    rxCmd = k3.readline()

    if len(rxCmd) == 0:
        k3.close()
        print("Error")
        return False
    else:
        k3.close()
        print("reply")
        print(rxCmd)
        return True

unlock_servo()