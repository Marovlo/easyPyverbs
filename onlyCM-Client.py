#!/usr/bin/python3.8

from easyRDMACM import easyRDMACM
from tensorTools import TENSORTOOLS
conn=easyRDMACM()
conn.connect(dst_ip='192.168.1.10',dst_port=12345)
tool=TENSORTOOLS()

# # 验证recv & send
# data=tool.rand_tensor_byte((3,3))
# conn.handshake(data_size=len(data))
# conn.send(data)
#
# # 验证write，使用同步write即sync_write_send
# data=tool.rand_tensor_byte((3,3))
# conn.sync_write_send(data)
#
# # 验证对端read
# data=tool.rand_tensor_byte((3,3))
# conn.sync_read_recv(data)



# 验证write，完全使用原版cmid代码
data_size=conn.handshake()['data_size']
print("data_size:",data_size)
mr=conn.cmid.reg_write(size=data_size)
conn.handshake(addr=mr.buf,rkey=mr.rkey)
conn.handshake()
data=mr.read(data_size,0)
print(data)