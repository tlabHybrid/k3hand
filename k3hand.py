from host_to_servo import host2servo
from common import *

class k3:
    def __init__(self, port):
        self.h2s = host2servo(port)
        self.angles = []

    def get_angle(self, id):
        self.h2s.send(header.READ, address.M_POS, 2, id)
        self.h2s.receive()
        self.h2s.print_cmd(self.h2s.rxCmd)
        i = (self.h2s.rxCmd[1]) +( self.h2s.rxCmd[2] << 8)
        angle = DataProcessor._int2angle(i)
        print(angle) 
    
    def disconnect(self):
        self.h2s.close()

k = k3("COM5")
k.get_angle(0)
k.disconnect()