#!/usr/bin/python3.8

from easyRDMACM import easyRDMACM
from tensorTools import TENSORTOOLS
conn=easyRDMACM()
conn.listen(src_ip='192.168.1.10',src_port=12345)
tool=TENSORTOOLS()


# 验证recv & send
data_size=conn.handshake()['data_size']
tensor=tool.byte_to_tensor(conn.recv(data_size))
print(tensor)

# 验证对端write，使用同步write即sync_write_recv
tensor=tool.byte_to_tensor(conn.sync_write_recv())
print(tensor)
