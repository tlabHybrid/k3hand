import serial
import time
def print_cmd(cmd):
        for b in cmd:
            print(format(b, '#04x'), end=' ')
        print()

def Read_Servo_ang(servo_id):
    txCmd = [0x59, 0x40, 0x00, 0x02, 0x01, servo_id]
    k3 = serial.Serial('/dev/ttyUSB0', baudrate=115200,parity=serial.PARITY_NONE, timeout=1)
    sum = 0
    for i in txCmd:
        sum += i
    
    csm = (~sum + 1) & 0xff

    txCmd.append(csm)
    print(txCmd)

    start = time.time()

    k3.write(txCmd)
    rxCmd = k3.read(11)
    end = time.time()

    print(end - start)
    if len(rxCmd) == 0:
        k3.close()
        print("Error")
        return False
    else:
        k3.close()
        print("reply")
        print(type(rxCmd))
        print_cmd(txCmd)
        print_cmd(rxCmd)
        return True

Read_Servo_ang(0x01)