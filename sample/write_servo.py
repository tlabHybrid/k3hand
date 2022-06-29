import serial

def Write_Servo_ang(servo_id, ang1, ang2):
    txCmd = [0x58, 0x80, 0x00, 0x02, 0x01, servo_id, ang1, ang2]
    k3 = serial.Serial('COM5', baudrate=115200,parity=serial.PARITY_NONE, timeout=1)
    sum = 0
    for i in txCmd:
        sum += i
    
    csm = (~sum + 1) & 0xff

    txCmd.append(csm)
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

Write_Servo_ang(0x00, 0x00, 0x00)