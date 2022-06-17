import serial

class h2s:
    def __init__(self, port):
        self.ser = serial.Serial(port, baudrate=115200,parity=serial.PARITY_NONE, timeout=3)
        self.txCmd = []
        self.rxCmd = []

    def send(self, hdr, ad, lg, id_list, data_list = []):
        if not isinstance(id_list, list):
            id_list = [id_list]
        if not isinstance(data_list, list):
            data_list = [data_list]
        
        self.txCmd = [hdr & 0xff]
        self.txCmd.append(ad & 0xff)
        self.txCmd.append((ad >> 8) & 0xff)
        self.txCmd.append(lg & 0xff)
        self.txCmd.append(len(id_list) & 0xff)
        for id in id_list:
            self.txCmd.append(id & 0xff)
            for data in data_list:
                for n in range(lg):
                    self.txCmd.append((data >> 8 * n) & 0xff)
        sum = 0
        for i in self.txCmd:
            sum += i
        csm = (~sum + 1) & 0xff
        self.txCmd.append(csm)
        self.ser.write(self.txCmd)

        self.rxCmd = self.k3.readall()
        self.ser.close()
        if len(self.rxCmd) == 0:
            return False
        else:
            return True
    
    def print_cmd(self, cmd):
        for b in cmd:
            print(format(b, '#04x'), end=' ')


