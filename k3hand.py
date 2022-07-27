from __future__ import print_function
from common import *
from host_to_servo import host2servo


class k3hand(host2servo):
    def __init__(self, port):
        #self.h2s = host2servo(port)
        super(k3hand, self).__init__(port)
        self.angles = [None]*8
        self.servo_en = [False]*8
        self.servo_lock = [True]*8
        self.speeds = [100] * 8
        self.ang_min = [-90, -25, -30, -90, -90, -50, -90, -90]
        self.ang_max = [30, 90, 90, 25, 90, 130, 90, 90]
        self.get_servos_stat()
        self.get_angles()
        #self.send_ang_max(self.ang_max)
        #self.send_ang_min(self.ang_min)

    def disconnect(self):
        self.disable_all()
        self.close()
#        self.h2s.close()


    def unlock_servo(self, id):
        #if self.h2s.send(Header.WRITE, Address.SYS_ULK, 1, id, Command.UNLOCK):
        if self.send(Header.WRITE, Address.SYS_ULK, 1, id, Command.UNLOCK):            
            self.servo_lock[id] = False
            print("The servo %d is unlocked" %id)
    
    def lock_servo(self, id):
        if self.send(Header.WRITE, Address.SYS_ULK, 1, id, Command.LOCK):
            self.servo_lock[id] = True
            print("The servo %d is locked" %id)

    def get_angle(self, id):
        if self.send(Header.READ, Address.M_POS, 2, id):
            i = self._decode_int16(self.rtn)
            self.angles[id] = self._int2angle(i)
            return self.angles[id]
    
    def get_angles(self, id_list=list(range(8))):
        if self.send(Header.READ, Address.M_POS, 2, id_list):
            for i in range(len(id_list)):
                #self.angles[id_list[i]] = DataProcessor._int2angle(DataProcessor._decode_int16(self.h2s.rtn[4*i:4*i+2]))
                self.angles[id_list[i]] = self._int2angle(self._decode_int16(self.rxCmd[4*i+1:4*i+3]))
            return [self.angles[id] for id in id_list] 

    def send_angle(self, id, angle):
        if self.servo_en[id]:
            if self.send(Header.WRITE, Address.FB_TPOS, 2, id, self._angle2int(angle)):
                self.angles[id] = angle
        else:
            print("Error: The servo id %d is not enabled." %id)

    def send_angles(self, angles, id_list=list(range(8))):
        if all(self.servo_en):
            if self.send(Header.WRITE, Address.FB_TPOS, 2, id_list, list(map(self._angle2int, angles))):
                for i in range(len(id_list)):
                    self.angles[id_list[i]] = angles[i]
        else:
            dis_list = [s for s in range(8) if not self.servo_en[s]]
            if len(dis_list) == 1:
                print("Error: The servo id%d is not enabled!" %dis_list[0])
            else:
                print("Error: The servo id", end=" ")
                print(*dis_list, sep=",",end="")
                print(" are not enabled!")
    
    def get_speed(self, id):
        if self.send(Header.READ, Address.FB_SC, 1, id):
            self.speeds[id] = self._int2speed(self.rxCmd[1])
            return self.speeds[id]
    
    def send_speed(self, id, speed):
        if self.send(Header.WRITE, Address.FB_SC, 1, id, self._speed2int(speed)):
            self.speeds[id] = speed

    def get_temp(self, id):
        if self.send(Header.READ, Address.M_TEMP, 2, id):
            return DataProcessor._decode_int16(self.rxCmd[1:3])
    
    def get_ang_min(self, id):
        if self.send(Header.READ, Address.FB_POSL, 2, id):
            return self._int2angle(self._decode_int16(self.rxCmd[1:3]))
    
    def get_ang_max(self, id):
        if self.send(Header.READ, Address.FB_POSH, 2, id):
            return self._int2angle(self._decode_int16(self.rxCmd[1:3]))

    def send_ang_max(self, id, angle):
        if self.send(Header.WRITE, Address.FB_POSH, 2, id, self._angle2int(angle)):
            return angle #DataProcessor._int2angle(DataProcessor._decode_int16(self.h2s.rxCmd[1:3]))

    def send_ang_mins(self, angles, id_list=list(range(8))):
        if self.send(Header.WRITE, Address.FB_POSL, 2, id_list, list(map(self._angle2int, angles))):
            for i in range(len(id_list)):
                self.ang_min[id_list[i]] = angles[i]

    def send_ang_maxs(self, angles, id_list=list(range(8))):
        if self.send(Header.WRITE, Address.FB_POSH, 2, id_list, list(map(self._angle2int, angles))):
            for i in range(len(id_list)):
                self.ang_max[id_list[i]] = angles[i]

    def get_servo_stat(self, id):
        if self.send(Header.READ, Address.SYS_ULK, 1, id):
            if self.rxCmd[1] == Command.LOCK:
                self.servo_lock[id] = True
            else:
                self.servo_lock[id] = False
        return self.servo_en[id], self.servo_lock[id]

    def get_servos_stat(self, id_list=list(range(8))):
        if len(self.servo_en) == 0:
            if self.send(Header.READ, Address.FB_EN, 1, list(range(8))):
                self.servo_en = [None]*8
                for id in id_list:
                    if self.rxCmd[id * 3 + 1] == Command.ENABLE:
                        self.servo_en[id] = True
                    else:
                        self.servo_en[id] = False
        else:
            return [self.servo_en[id] for id in id_list]
    

    def enable_servo(self, id):
        if self.send(Header.WRITE, Address.FB_EN, 1, id, Command.ENABLE):
            print("The servo id %d is enabled" %id)
            self.servo_en[id] = True
    
    def disable_servo(self, id):
        if self.send(Header.WRITE, Address.FB_EN, 1, id, Command.DISABLE):
            print("The servo id %d is disabled" %id)
            self.servo_en[id] = False

    def enable_all(self):
        if self.send(Header.WRITE, Address.FB_EN, 1, list(range(8)), [Command.ENABLE]*8):
            self.servo_en = [True]*8

    def disable_all(self):
        if self.send(Header.WRITE, Address.FB_EN, 1, list(range(8)), [Command.DISABLE]*8):
            self.servo_en = [False]*8

'''
k = k3("/dev/ttyUSB0")
a = k.get_angles()
print(a)
print(k.get_servos_stat())
#k.send_angles([0, 0, 0, 0, 0, 0, 0, 0])
k.disconnect()
'''
