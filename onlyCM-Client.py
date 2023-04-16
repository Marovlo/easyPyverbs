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
# data=tool.rand_tensor_byte((3,3))
# data_size= len(data)
# conn.send_infos(data_size=data_size)
# mr=conn.cmid.reg_write(data_size)
# mr.write(data,data_size)
# remote_info=conn.recv_infos()
# conn.cmid.post_write(mr,data_size,remote_info['addr'],remote_info['rkey'])
# wc=conn.cmid.get_send_comp()
# conn.send_infos(send_finished=1)
conn.send_infos(data='abcd')
data=conn.recv_infos()['size']
data=conn.recv_infos()['data']
conn.send_infos(size=100)
conn.send_infos(data='abcd')
data=conn.recv_infos()['size']
data=conn.recv_infos()['data']
conn.send_infos(size=100)