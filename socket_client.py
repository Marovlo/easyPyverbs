#!/usr/bin/python3.8
import time
import socket
from tensorTools import TENSORTOOLS

start=time.time()
tool=TENSORTOOLS()
conn=socket.socket(family=socket.AF_INET,type=socket.SOCK_STREAM)
conn.connect(('10.112.241.161',12344))
data=tool.rand_tensor_byte((10,10,10,10,10,10,10,10))
conn.send(data)
data=tool.rand_tensor_byte((10,10,10,10,10,10,10,10))
conn.send(data)
print(len(data))
conn.send(data)
print(len(data))
end=time.time()
print('time used:',end-start)