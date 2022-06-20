from host_to_servo import host2servo
from common import *

class k3:
    def __init__(self, port):
        self.h2s = host2servo(port)
        self.angles = []
        self.enable = [False]*8

    def get_angle(self, id):
        self.h2s.send(header.READ, address.M_POS, 2, id)
        self.h2s.receive()
        self.h2s.print_cmd(self.h2s.rxCmd)
        i = DataProcessor._decode_int16(self.h2s.rxCmd[1:3])
        angle = DataProcessor._int2angle(i)
        return angle
    
    def disconnect(self):
        self.h2s.close()

    def send_angle(self, id, angle):
        if self.enable[id]:
            

        else:
            print("The servo is disable")
        

k = k3("COM5")
a = k.get_angle(0)
print(a)
k.disconnect()