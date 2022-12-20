from k3hand import k3hand

k = k3hand("/dev/ttyUSB1")
k.enable_all()
k.send_angle(0, 10)
k.send_angle(0,0)
k.disconnect()