import serial
from struct import *
from common import *
byte = 8
class host2servo:
    def __init__(self, port):
        self.ser = serial.Serial(port, baudrate=115200,parity=serial.PARITY_NONE, timeout=1)
        self.txCmd = []
        self.rxCmd = []
        self.hdr = None
        self.cnt = None

    def make_txCmd(self, hdr, ad, lg, id_list, data_list = []):
        if not isinstance(id_list, list):
            id_list = [id_list]
        if not isinstance(data_list, list):
            data_list = [data_list]
        self.hdr = hdr
        self.cnt = len(id_list)
        self.txCmd += DataProcessor._encode_int8(hdr)
        #self.txCmd.append(ad & 0xff)
        #self.txCmd.append((ad >> byte) & 0xff)
        self.txCmd += DataProcessor._encode_int16(ad)
        self.txCmd += DataProcessor._encode_int8(lg)
        self.txCmd += DataProcessor._encode_int8(self.cnt)
        for i in range(self.cnt):
            self.txCmd += DataProcessor._encode_int8(id_list[i])
            if hdr != header.READ:
                data = data_list[i]
                if lg == 1:
                    self.txCmd += DataProcessor._encode_int8(data)
                if lg == 2:
                    self.txCmd += DataProcessor._encode_int16(data)
        self.txCmd += DataProcessor._encode_int8(self.make_csm(self.txCmd))

    def make_csm(self, blist):
        sum = 0
        for i in blist:
            sum += i
        c = (~sum + 1) & 0xff
        return c

    def check_csm(self, cmd):
        if self.make_csm(cmd[:-1]) == cmd[-1]:
            return True
        else:
            return False

    def send(self, hdr, ad, lg, id_list, data_list = []):
        self.make_txCmd(hdr, ad, lg, id_list, data_list)
        self.ser.write(self.txCmd)
        #self.receive()
    
    def receive(self):
        if self.hdr == header.READ:
            r_len = self.cnt * 4 * byte
        if self.hdr == header.WRITE:
            r_len = self.cnt * byte
        r = self.ser.read(len(self.txCmd)*byte + r_len)
        self.rxCmd = r[len(self.txCmd):]
        if len(self.rxCmd) == 0:
            return False
        else:
            return True
    
    def close(self):
        self.ser.close()
    
    def print_cmd(self, cmd):
        for b in cmd:
            print(format(b, '#04x'), end=' ')


k3 = host2servo("COM5")
k3.send(0x59, 0x40, 2, (0,1))
k3.receive()
k3.print_cmd(k3.rxCmd)
k3.close()