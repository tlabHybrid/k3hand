from __future__ import print_function
from common import *
from host_to_servo import host2servo
import time

class k3hand(host2servo):
    def __init__(self, port):
        super(k3hand, self).__init__(port)
        self.cur_angles = [None]*8
        self.tar_angles = [0]*8
        self.servo_en = [False]*8
        self.servo_lock = [True]*8
        self.speeds = [100] * 8
        self.ang_min = [-90, -90, -30, -90, -90, -50, -90, -90]
        self.ang_max = [30, 90, 90, 90, 90, 130, 90, 90]
        self.get_servos_stat()
        self.start = time.time()
        
        self.unlock_all()
        self.send_ang_maxs(self.ang_max)
        self.send_ang_mins(self.ang_min)
        self.lock_all()

    def disconnect(self):
        self.disable_all()
        self.close()

    def unlock_servo(self, id):
        if self.send(Header.WRITE, Address.SYS_ULK, 1, id, Command.UNLOCK):            
            self.servo_lock[id] = False
            print("The servo %d is unlocked" %id)
    
    def lock_servo(self, id):
        if self.send(Header.WRITE, Address.SYS_ULK, 1, id, Command.LOCK):
            self.servo_lock[id] = True
            print("The servo %d is locked" %id)

    def unlock_all(self):
        if self.send(Header.WRITE, Address.SYS_ULK, 1, list(range(8)), [Command.UNLOCK]*8):
            self.servo_lock = [False] * 8

    def lock_all(self):
        if self.send(Header.WRITE, Address.SYS_ULK, 1, list(range(8)), [Command.LOCK]*8):
            self.servo_lock = [True] * 8           

    def get_angle(self, id):
        if self.send(Header.READ, Address.M_POS, 2, id):
            i = self._decode_int16(self.rtn)
            self.cur_angles[id] = self._int2angle(i)            
            return self.cur_angles[id]
        
    def get_angles(self, id_list=list(range(8))):
        if self.send(Header.READ, Address.M_POS, 2, id_list):
            for i in range(len(id_list)):
                self.cur_angles[id_list[i]] = self._int2angle(self._decode_int16(self.rtn[2*i:2*(i+1)]))
            return [self.cur_angles[id] for id in id_list]
    def get_radians(self, id_list=list(range(8))):
        if self.send(Header.READ, Address.M_POS, 2, id_list):
            for i in range(len(id_list)):
                self.cur_angles[id_list[i]] = self._int2angle(self._decode_int16(self.rtn[2*i:2*(i+1)]))
            return [self._ang2rad(self.cur_angles[id]) for id in id_list]
    
    def time_check(self):
        tmp = time.time()
        print("function called at %lf" %(tmp-self.start))
        self.send(Header.WRITE, Address.FB_TPOS, 2, 0, self._angle2int(10))
        tmp = time.time()
        print("function finished at %lf" %(tmp-self.start))

    def send_angle(self, id, angle):
        tmp = time.time()        
        if self.servo_en[id]:
            if self.send(Header.WRITE, Address.FB_TPOS, 2, id, self._angle2int(angle)):
                self.tar_angles[id] = angle
        else:
            print("Warning: The servo id %d is not enabled." %id)
        tmp = time.time()
            
    def send_angles(self, angles, id_list=list(range(8))):
        if self.send(Header.WRITE, Address.FB_TPOS, 2, id_list, list(map(self._angle2int, angles))):
            for i in range(len(id_list)):
                self.tar_angles[id_list[i]] = angles[i]      
               
        if not all(self.servo_en):
            dis_list = [s for s in range(8) if not self.servo_en[s]]
            if len(dis_list) == 1:
                print("Warning: The servo id%d is not enabled!" %dis_list[0])
            else:
                print("Warning: The servo id", end=" ")
                print(*dis_list, sep=",",end="")
                print(" are not enabled!")
                
    def send_radians(self, radians, id_list=list(range(8))):
        self.send_angles(list(map(self._rad2ang, radians)), id_list)

    def send_radian(self, id, radian):
        self.send_angle(id, self._rad2ang(radian))

    def set_speed(self, speed):
        if self.send(Header.WRITE, Address.FB_SC, 1, list(range(8)), [self._speed2int(speed)]*8):
            self.speeds = [speed]*8

    
    def get_speed(self, id):
        if self.send(Header.READ, Address.FB_SC, 1, id):
            self.speeds[id] = self._int2speed(self._decode_uint8(self.rtn))
            return self.speeds[id]
    
    def send_speed(self, id, speed):
        if self.send(Header.WRITE, Address.FB_SC, 1, id, self._speed2int(speed)):
            self.speeds[id] = speed

    def get_temp(self, id):
        if self.send(Header.READ, Address.M_TEMP, 2, id):
            return self._decode_int16(self.rtn)
    
    def get_ang_min(self, id):
        if self.send(Header.READ, Address.FB_POSL, 2, id):
            return self._int2angle(self._decode_int16(self.rtn))
    
    def get_ang_max(self, id):
        if self.send(Header.READ, Address.FB_POSH, 2, id):
            return self._int2angle(self._decode_int16(self.rtn))

    def send_ang_mins(self, angles, id_list=list(range(8))):
        if self.send(Header.WRITE, Address.FB_POSL, 2, id_list, list(map(self._angle2int, angles))):
            for i in range(len(id_list)):
                self.ang_min[id_list[i]] = angles[i]

    def send_ang_maxs(self, angles, id_list=list(range(8))):
        if self.send(Header.WRITE, Address.FB_POSH, 2, id_list, list(map(self._angle2int, angles))):
            for i in range(len(id_list)):
                self.ang_max[id_list[i]] = angles[i]
    """            
    def get_servo_stat(self, id):
        if self.send(Header.READ, Address.SYS_ULK, 1, id):
            if self.rtn == Command.LOCK:
                self.servo_lock[id] = True
            else:
                self.servo_lock[id] = False
        return self.servo_en[id], self.servo_lock[id]
    """
    def get_servos_stat(self, id_list=list(range(8))):
        if self.send(Header.READ, Address.FB_EN, 1, id_list):
            for id in id_list:
                if self._decode_uint8(self.rtn[id]) == Command.ENABLE:
                    self.servo_en[id] = True
                else:
                    self.servo_en[id] = False
            
        if self.send(Header.READ, Address.SYS_ULK, 1, id_list):
            for id in id_list:
                if self._decode_uint8(self.rtn[id]) == Command.LOCK:
                    self.servo_lock[id] = True
                else:
                    self.servo_lock[id] = False
        if self.send(Header.READ, Address.FB_TPOS, 2, id_list):
            for i in range(len(id_list)):
                self.tar_angles[id_list[i]] = self._int2angle(self._decode_int16(self.rxCmd[4*i+1:4*i+3]))
       

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
