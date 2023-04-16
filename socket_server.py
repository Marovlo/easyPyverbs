#!/usr/bin/python3.8
import time
import socket
from tensorTools import TENSORTOOLS

start=time.time()
tool=TENSORTOOLS()
skt=socket.socket(family=socket.AF_INET,type=socket.SOCK_STREAM)
skt.bind(('10.112.241.161',12344))
skt.listen()
conn,addr=skt.accept()
data_size=conn.recv(100).decode('utf-8')
data_size=int(data_size)
data=conn.recv(data_size)
print(len(data))
data_size=conn.recv(100).decode('utf-8')
data_size=int(data_size)
data=conn.recv(data_size)
print(len(data))
end=time.time()
print('time used:',end-start)