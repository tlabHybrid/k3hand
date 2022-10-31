from __future__ import print_function
import serial
from struct import *
from common import *
byte = 8
class host2servo(DataProcessor):
    def __init__(self, port):
        self.ser = serial.Serial(port, baudrate=115200,parity=serial.PARITY_NONE, timeout=0.1)
        self.txCmd = None
        self.rxCmd = None   
        self.hdr = None
        self.cnt = None
        self.rtn = None

    def make_txCmd(self, hdr, ad, lg, id_list, data_list = []):
        '''
        if not isinstance(id_list, list):
            id_list = [id_list]
        if not isinstance(data_list, list):
            data_list = [data_list]
        '''
        id_list = self._make_list(id_list)
        data_list = self._make_list(data_list)
        if hdr == Header.READ and len(data_list) > 0:
            print("Error: READ command needs no datas!")
            return
        elif hdr == Header.WRITE and len(data_list) != len(id_list):
            print("Error: The length of id list and that of data list must be same!")
            return 
        self.hdr = hdr
        self.cnt = len(id_list)
        self.txCmd = self._encode_int8(hdr)
        #self.txCmd.append(ad & 0xff)
        #self.txCmd.append((ad >> byte) & 0xff)
        self.txCmd += self._encode_int16(ad)
        self.txCmd += self._encode_int8(lg)
        self.txCmd += self._encode_int8(self.cnt)
        for i in range(self.cnt):
            self.txCmd += self._encode_int8(id_list[i])
            if hdr != Header.READ:
                data = data_list[i]
                if lg == 1:
                    self.txCmd += self._encode_uint8(data)
                if lg == 2:
                    self.txCmd += self._encode_int16(data)
        self.txCmd += self._encode_uint8(self.make_csm(self.txCmd))

    def make_csm(self, blist):
        sum = 0
        for i in blist:
            i = self._decode_uint8(i)
            sum += i
        c = (~sum + 1) & 0xff
        return c

    def check_csm(self, cmd):
        if self.make_csm(cmd[:-1]) == self._decode_uint8(cmd[-1]):
            self.rtn += cmd[1:-1]
            return True
        else:
            print("Error: check sum is not correct!")
            return False

    def send(self, hdr, ad, lg, id_list, data_list = []):
        self.make_txCmd(hdr, ad, lg, id_list, data_list)
        self.ser.write(self.txCmd)
        return self.receive()
    
    def receive(self):
        if self.hdr == Header.READ:
            r_len = self.cnt * 4 
        if self.hdr == Header.WRITE:
            r_len = self.cnt
        r = self.ser.read(len(self.txCmd) + r_len)
        self.rxCmd = r[len(self.txCmd):]
        if len(self.rxCmd) == 0:
            print("Error: Servos send no messages!")
            return False
        else:
            if self.hdr == Header.READ:
                check = True
                block = int(len(self.rxCmd) / self.cnt)
                self.rtn = b''
                for i in range(self.cnt):
                    if not self.check_csm(self.rxCmd[block*i:block*(i+1)]):
                        check = False
                        break
                return check
            elif self.hdr == Header.WRITE:
                check = True
                for i in range(self.cnt):
                    if self.rxCmd[i] == Command.NG:
                        print("Error: Received NG command!")
                        check = False
                        break
                return check
    
    def close(self):
        self.ser.close()
    
    def print_cmd(self, cmd):
        for b in cmd:
            print(format(b, '#04x'), end=' ')
        print()

'''
k3 = host2servo("COM5")
k3.send(0x59, 0x40, 2, [0, 1])
k3.receive()
k3.print_cmd(k3.rxCmd)
k3.close()
'''
