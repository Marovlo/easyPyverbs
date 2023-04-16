import time
import socket
from tensorTools import TENSORTOOLS

start=time.time()
tool=TENSORTOOLS()
skt=socket.socket(family=socket.AF_INET,type=socket.SOCK_STREAM)
skt.bind(('10.112.241.161',12344))
skt.listen()
conn,addr=skt.accept()
data=conn.recv()
print(len(data))
data=conn.recv()
print(len(data))
end=time.time()
print('time used:',end-start)