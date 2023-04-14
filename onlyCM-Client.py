#!/usr/bin/python3.8

from easyRDMACM import easyRDMACM
from tensorTools import TENSORTOOLS
conn=easyRDMACM()
conn.connect(dst_ip='192.168.1.10',dst_port=12345)
tool=TENSORTOOLS()

# 验证recv & send
data=tool.rand_tensor_byte((3,3))
conn.handshake(data_size=len(data))
conn.send(data)

# # 验证write，使用同步write即sync_write_send
# data_size=len(data)
# conn.handshake(data_size=data_size) # 告知对端即将写入的大小
# remote_info=conn.handshake() # 等待对端告知内存的地址和key
# mr = conn.reg_write(data_size)
# conn.cmid.post_write(mr, data_size, remote_info['remote_addr'], remote_info['remote_key'])
# conn.handshake() # 告知对端写入完成、

# 验证对端read
data=tool.rand_tensor_byte(())
data_size=len(data)
mr=conn.reg_read(data_size)
mr.write(data,data_size)
