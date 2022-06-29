from host_to_servo import host2servo
from common import *

class k3:
    def __init__(self, port):
        self.h2s = host2servo(port)
        self.angles = [None]*8
        self.servo_st = [False]*8
        self.get_servos_stat()
        self.get_angles()

    def disconnect(self):
        self.disable_all()
        self.h2s.close()

    def get_angle(self, id):
        if self.h2s.send(Header.READ, Address.M_POS, 2, id):
            i = DataProcessor._decode_int16(self.h2s.rxCmd[1:3])
            self.angles[id] = DataProcessor._int2angle(i)
            return self.angles[id]
    
    def get_angles(self, id_list=list(range(8))):
        if self.h2s.send(Header.READ, Address.M_POS, 2, id_list):
            for i in range(len(id_list)):
                self.angles[id_list[i]] = DataProcessor._int2angle(DataProcessor._decode_int16(self.h2s.rxCmd[4*i+1:4*i+3]))
            return [self.angles[id] for id in id_list] 

    def send_angle(self, id, angle):
        if self.servo_st[id]:
            if self.h2s.send(Header.WRITE, Address.FB_TPOS, 2, id, DataProcessor._angle2int(angle)):
                self.angles[id] = angle
        else:
            print("Error: The servo id %d is not enabled." %id)

    def send_angles(self, angles, id_list=list(range(8))):
        if all(self.servo_st):
            if self.h2s.send(Header.WRITE, Address.FB_TPOS, 2, id_list, list(map(DataProcessor._angle2int, angles))):
                for i in range(len(id_list)):
                    self.angles[id_list[i]] = angles[i]
        else:
            dis_list = [s for s in range(8) if not self.servo_st[s]]
            if len(dis_list) == 1:
                print("Error: The servo id%d is not enabled!" %dis_list[0])
            else:
                print("Error: The servo id", end=" ")
                print(*dis_list, sep=",",end="")
                print(" are not enabled!")
    
    def get_servo_stat(self, id):
        return self.servo_st[id]

    def get_servos_stat(self, id_list=list(range(8))):
        if len(self.servo_st) == 0:
            if self.h2s.send(Header.READ, Address.FB_EN, 1, list(range(8))):
                self.servo_st = [None]*8
                for id in id_list:
                    if self.h2s.rxCmd[id * 3 + 1] == Command.ENABLE:
                        self.servo_st[id] = True
                    else:
                        self.servo_st[id] = False
        else:
            return [self.servo_st[id] for id in id_list]
    

    def enable_servo(self, id):
        if self.h2s.send(Header.WRITE, Address.FB_EN, 1, id, Command.ENABLE):
            print("The servo id %d is enabled" %id)
            self.servo_st[id] = True
    
    def disable_servo(self, id):
        if self.h2s.send(Header.WRITE, Address.FB_EN, 1, id, Command.DISABLE):
            print("The servo id %d is disabled" %id)
            self.servo_st[id] = False

    def enable_all(self):
        if self.h2s.send(Header.WRITE, Address.FB_EN, 1, list(range(8)), [Command.ENABLE]*8):
            self.servo_st = [True]*8

    def disable_all(self):
        if self.h2s.send(Header.WRITE, Address.FB_EN, 1, list(range(8)), [Command.DISABLE]*8):
            self.servo_st = [False]*8
'''
k = k3("COM5")
a = k.get_angles()
print(a)
print(k.get_servos_stat())
k.send_angles([0, 0, 0, 0, 0, 0, 0, 0])
k.disconnect()
'''
