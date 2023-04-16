#!/usr/bin/python3.8
import time
import socket
import struct
from tensorTools import TENSORTOOLS

start=time.time()
tool=TENSORTOOLS()
skt=socket.socket(family=socket.AF_INET,type=socket.SOCK_STREAM)
skt.bind(('10.112.241.161',12344))
skt.listen()
conn,addr=skt.accept()
data_size=struct.unpack('i',conn.recv(struct.calcsize("i")))[0]
print(data_size)
recv_size=0
data=b''
while recv_size<data_size:
    data+=conn.recv(1024)
    recv_size+=1024
# data=conn.recv(400000811)
# print(len(data))
end=time.time()
print('time used:',end-start)

