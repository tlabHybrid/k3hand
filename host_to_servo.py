import serial
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
        self.txCmd = [hdr & 0xff]
        self.txCmd.append(ad & 0xff)
        self.txCmd.append((ad >> byte) & 0xff)
        self.txCmd.append(lg & 0xff)
        self.txCmd.append(self.cnt & 0xff)
        for id in id_list:
            self.txCmd.append(id & 0xff)
            for data in data_list:
                for n in range(lg):
                    self.txCmd.append((data >> byte * n) & 0xff)
        self.txCmd.append(self.csm(self.txCmd))

    def csm(self, blist):
        sum = 0
        for i in blist:
            sum += i
        c = (~sum + 1) & 0xff
        return c

    def send(self, hdr, ad, lg, id_list, data_list = []):
        self.make_txCmd(hdr, ad, lg, id_list, data_list)
        self.ser.write(self.txCmd)
    
    def receive(self):
        if self.hdr == 0x59:
            r_len = self.cnt * 4 * byte
        if self.hdr == 0x58:
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
k3.send(0x58, 0x82, 1, 0, 0xff)
k3.receive()
k3.print_cmd(k3.rxCmd)
k3.close()

