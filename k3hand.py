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
        self.debug = True    
        self.unlock_all()
        self.send_ang_maxs(self.ang_max)
        self.send_ang_mins(self.ang_min)
        self.lock_all()

    def disconnect(self):
        """Disconnect the serial port."""
        self.disable_all()
        self.close()

    def unlock_servo(self, id):
        """Unlock the servo with the given id.

        Args:
            id (int): The id of the servo to be unlocked.
        """
        if self.send(Header.WRITE, Address.SYS_ULK, 1, id, Command.UNLOCK):            
            self.servo_lock[id] = False
            if self.debug:
                print("The servo %d is unlocked" %id)
    
    def lock_servo(self, id):
        """Lock the servo with the given id.
        
        Args:
            id (int): The id of the servo to be locked.
        """
        if self.send(Header.WRITE, Address.SYS_ULK, 1, id, Command.LOCK):
            self.servo_lock[id] = True
            if self.debug:
                print("The servo %d is locked" %id)

    def unlock_all(self):
        """Unlock all the servos.
        """
        if self.send(Header.WRITE, Address.SYS_ULK, 1, list(range(8)), [Command.UNLOCK]*8):
            self.servo_lock = [False] * 8

    def lock_all(self):
        """Lock all the servos.
        """
        if self.send(Header.WRITE, Address.SYS_ULK, 1, list(range(8)), [Command.LOCK]*8):
            self.servo_lock = [True] * 8           

    def get_angle(self, id):
        """Get the current angle of the servo with the given id.

        Args:
            id (int): The id of the servo to be read.

        Returns:
            int: The current angle of the servo.
        """
        if self.send(Header.READ, Address.M_POS, 2, id):
            self.cur_angles[id] = self._int2angle(self.rv[0])            
            return self.cur_angles[id]
    
    def get_angles(self, id_list=list(range(8))):
        """Get the current angles of the servos with the given ids.

        Args:
            id_list (list, optional): The ids of the servos to be read. Defaults to list(range(8)).

        Returns:
            list: The current angles of the servos.
        """
        if self.send(Header.READ, Address.M_POS, 2, id_list):
            for i, id in enumerate(id_list):
                self.cur_angles[id] = self._int2angle(self.rv[i])
            return self.list_extraction(self.cur_angles, id_list)

    def get_radians(self, id_list=list(range(8))):
        return list(map(self._ang2rad, self.get_angles(id_list)))

    def send_angle(self, id, angle, speed=None):        
        if speed is None:
            self.send(Header.WRITE, Address.FB_SC, 1, id, self._speed2int(self.speeds[id]))
        else:
            if self.send(Header.WRITE, Address.FB_SC, 1, id, self._speed2int(speed)):
                self.speeds[id] = speed
        if self.send(Header.WRITE, Address.FB_TPOS, 2, id, self._angle2int(angle)):
            self.tar_angles[id] = angle

        if self.debug and (not self.servo_en[id]):
             print("Warning: The servo id %d is not enabled." %id)
        
            
    def send_angles(self, angles, speeds=None, id_list=list(range(8))):
        if speeds is None:
            self.send(Header.WRITE, Address.FB_SC, 1, id_list, list(map(self._speed2int,self.list_extraction(self.speeds, id_list))))
        else:
            if isinstance(speeds, list):
                if self.send(Header.WRITE, Address.FB_SC, 1, id_list, list(map(self._speed2int, speeds))):
                    for i, id in enumerate(id_list):
                        self.speeds[id] = speeds[i]                
            elif isinstance(speeds, int):
                if self.send(Header.WRITE, Address.FB_SC, 1, id_list, [self._speed2int(speeds)]*len(id_list)):
                    for id in id_list:
                        self.speeds[id] = speeds
                

        if self.send(Header.WRITE, Address.FB_TPOS, 2, id_list, list(map(self._angle2int, angles))):
            for i, id in enumerate(id_list):
                self.tar_angles[id] = angles[i]      
               
        if not all(self.servo_en):
            if self.debug:
                dis_list = [s for s in range(8) if not self.servo_en[s]]            
                if len(dis_list) == 1:
                    print("Warning: The servo id%d is not enabled!" %dis_list[0])
                else:
                    print("Warning: The servo id", end=" ")
                    print(*dis_list, sep=",",end="")
                    print(" are not enabled!")

    def send_radians(self, radians, speeds=None, id_list=list(range(8))):
        self.send_angles(list(map(self._rad2ang, radians)), speeds, id_list)

    def send_radian(self, id, radian):
        self.send_angle(id, self._rad2ang(radian))

    def send_speeds(self, speeds, id_list=list(range(8))):
        if isinstance(speeds, int):
            if self.send(Header.WRITE, Address.FB_SC, 1, id_list, [self._speed2int(speeds)]*len(id_list)):
                for i, id in enumerate(id_list):
                    self.speeds[id] = speeds
        elif isinstance(speeds, list):
            if self.send(Header.WRITE, Address.FB_SC, 1, id_list, list(map(self._speed2int,speeds))):
                for i, id in enumerate(id_list):
                    self.speeds[id] = speeds[i]

    def get_speeds(self, id_list=list(range(8))):
        if self.send(Header.READ, Address.FB_SC, 1, list(range(8))):
            for i, id in enumerate(id_list):
                self.speeds[id] = self._int2speed(self.rv[i])
            return self.list_extraction(self.speeds, id_list)

    def get_speed(self, id):
        if self.send(Header.READ, Address.FB_SC, 1, id):
            self.speeds[id] = self._int2speed(self.rv[0])
            return self.speeds[id]
    
    def send_speed(self, id, speed):
        if self.send(Header.WRITE, Address.FB_SC, 1, id, self._speed2int(speed)):
            self.speeds[id] = speed

    def get_temp(self, id):
        if self.send(Header.READ, Address.M_TEMP, 2, id):
            return self._data2temp(self.rv[0])
    
    def get_ang_min(self, id):
        if self.send(Header.READ, Address.FB_POSL, 2, id):
            return self._int2angle(self.rv[0])
    
    def get_ang_max(self, id):
        if self.send(Header.READ, Address.FB_POSH, 2, id):
            return self._int2angle(self.rv[0])

    def send_ang_mins(self, angles, id_list=list(range(8))):
        if self.send(Header.WRITE, Address.FB_POSL, 2, id_list, list(map(self._angle2int, angles))):
            for i in range(len(id_list)):
                self.ang_min[id_list[i]] = angles[i]

    def send_ang_maxs(self, angles, id_list=list(range(8))):
        if self.send(Header.WRITE, Address.FB_POSH, 2, id_list, list(map(self._angle2int, angles))):
            for i in range(len(id_list)):
                self.ang_max[id_list[i]] = angles[i]

    def get_servos_stat(self, id_list=list(range(8))):
        if self.send(Header.READ, Address.FB_EN, 1, id_list):
            for i, id in enumerate(id_list):
                if self.rv[i] == Command.ENABLE:
                    self.servo_en[id] = True
                else:
                    self.servo_en[id] = False
            
        if self.send(Header.READ, Address.SYS_ULK, 1, id_list):
            for i, id in enumerate(id_list):
                if self.rv[i] == Command.LOCK:
                    self.servo_lock[id] = True
                else:
                    self.servo_lock[id] = False
            
        if self.send(Header.READ, Address.FB_TPOS, 2, id_list):
            for i, id in enumerate(id_list):
                self.tar_angles[id] = self._int2angle(self.rv[i])
       
    def enable_servo(self, id):
        if self.send(Header.WRITE, Address.FB_EN, 1, id, Command.ENABLE):
            if self.debug:
                print("The servo id %d is enabled" %id)
            self.servo_en[id] = True
    
    def disable_servo(self, id):
        if self.send(Header.WRITE, Address.FB_EN, 1, id, Command.DISABLE):
            if self.debug:
                print("The servo id %d is disabled" %id)
            self.servo_en[id] = False

    def enable_all(self):
        if self.send(Header.WRITE, Address.FB_EN, 1, list(range(8)), [Command.ENABLE]*8):
            self.servo_en = [True]*8

    def disable_all(self):
        if self.send(Header.WRITE, Address.FB_EN, 1, list(range(8)), [Command.DISABLE]*8):
            self.servo_en = [False]*8
