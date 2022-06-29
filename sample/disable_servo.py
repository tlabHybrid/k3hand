import serial

def enable():
    k3 = serial.Serial('COM5', baudrate=115200,parity=serial.PARITY_NONE, timeout=1)
    txCmd = [0x58, 0x82, 0x00, 0x01, 0x01, 0x00, 0xFF]
    sum = 0
    for i in txCmd:
        sum += i
    
    csm = (~sum + 1) & 0xff

    txCmd.append(csm)
    print(txCmd)

    k3.write(txCmd)
    rxCmd = k3.readall()

    if len(rxCmd) == 0:
        k3.close()
        print("Error")
        return False
    else:
        k3.close()
        print("reply")
        print(rxCmd)
        return True

enable()