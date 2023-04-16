#!/usr/bin/python3.8
import time
import socket
import struct
from tensorTools import TENSORTOOLS

start=time.time()
tool=TENSORTOOLS()
conn=socket.socket(family=socket.AF_INET,type=socket.SOCK_STREAM)
conn.connect(('10.112.241.161',12344))
data=tool.rand_tensor_byte((10,10,10,10,10,10,10,10))
data_size=len(data)
conn.send(struct.pack('i',data_size))
conn.sendall(data)
# data=tool.rand_tensor_byte((10,10,10,10,10,10,10,10))
# conn.send(data)
end=time.time()
print('time used:',end-start)