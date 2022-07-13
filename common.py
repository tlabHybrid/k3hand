import struct

class Address:
    SYS_PN = 0x00 #product name
    SYS_VER = 0x02 #version
    SYS_SID = 0x04 #servo id
    SYS_ULK = 0x1B #unlock by 0x75
    SYS_STS = 0x3F #status b0:temp. anomaly, b1:abnormal current, b2:reservation, b3:abnormal voltage, b4~b6:reservation, b7:reset detection
    M_POS = 0x40 #current angle
    M_TEMP = 0x42 #temp. sensor average
    M_CUR = 0x44 #current sensor average
    M_VI = 0x46 #voltage sensor average
    M_ERR = 0x48 #control deviation
    FB_TPOS = 0x80 #target angle
    FB_EN = 0x82 #output ENABLE 0x80:100%, 0xFF:Free, 0x00:3 phase H, 0xFE:3 phase L
    FB_SC = 0x83 #output scaling 0x80:100%
    FB_POSL = 0x94 #angle lower limit(initial value:0x8000)
    FB_POSH = 0x96 #angle upper limit(initial value:0x7FFF)
    AL_TEMP = 0xC0 #alarm temp. (initial value:0x0000)
    SD_TEMP = 0xC2 #shut down temp. (initial value:0x0000)    
    AL_CUR = 0xC4 #alarm current (initial value:0x0000)
    SD_CUR = 0xC6 #shut down current (initial value:0x0000)  
    AL_VI = 0xC8 #alarm voltage (initial value:0x0000)
    SD_VI = 0xCA #shut down voltage (initial value:0x0000)      

class Header:
    WRITE = 0x58
    READ = 0x59
    WRITE_WITHOUT_RESPONSE = 0x78

class Command:
    ENABLE = 0x80
    DISABLE = 0xFF
    PHASE_HIGH = 0x00
    PHASE_LOW = 0xFE
    LOCK = 0x00
    UNLOCK = 0x75
    OK = 0x30
    NG = 0x31

class DataProcessor:
    def _int2angle(i):
        if(i < 0):
            return round(i / 32768.0 * 180.0, 1)
        else:
            return round(i / 32767.0 * 180.0, 1)
    
    def _angle2int(a):
        if(a < 0):
            return int(a / 180.0 * 32768.0)
        else:
            return int(a / 180.0 * 32767.0)
    
    def _int2speed(i):
        return i / 128 * 100
    
    def _speed2int(s):
        return int(s / 100 * 128)
    
    def _decode_int8(data):
        return struct.unpack("b", data)[0]

    def _decode_uint8(data):
        return struct.unpack("B", data)[0]

    def _decode_int16(data):
        return struct.unpack("<h", data)[0]

    def _encode_int8(data):
        return struct.pack("b", data)
    
    def _encode_uint8(data):
        return struct.pack("B", data)

    def _encode_int16(data):
        return struct.pack("<h", data)

    def _make_list(datas):
        if isinstance(datas, tuple):
            return list(datas)
        elif not isinstance(datas, list):
            return [datas]
        else:
            return datas
    
    


