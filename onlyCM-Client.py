#!/usr/bin/python3.8

from easyRDMACM import easyRDMACM
from tensorTools import TENSORTOOLS
info_conn=easyRDMACM()
info_conn.connect(dst_ip='192.168.1.10',dst_port=12345)
data_conn=easyRDMACM()
data_conn.connect(dst_ip='192.168.1.10',dst_port=12346)
tool=TENSORTOOLS()

data=tool.rand_tensor_byte((10,10,10,10,10,10))
data_size=len(data)
mr=data_conn.reg_write(data_size)
mr.write(data,data_size)
info_conn.send_infos(data_size=data_size)
remote_info=info_conn.recv_infos()
data_conn.post_write(mr,data_size,remote_info['addr'],remote_info['rkey'])
wc=data_conn.get_send_comp()
info_conn.send_infos(send_finished=1)

data=tool.rand_tensor_byte((10,10,10,10,10,10))
data_size=len(data)
mr=data_conn.reg_read(data_size)
mr.write(data,data_size)
info_conn.send_infos(data_size=data_size,addr=mr.buf,rkey=mr.rkey)
read_finished=info_conn.recv_infos()['read_finished']

data_size=info_conn.recv_infos()['data_size']
mr=data_conn.reg_write(data_size)
info_conn.send_infos(addr=mr.buf,rkey=mr.rkey)
send_finished=info_conn.recv_infos()['send_finished']
data=mr.read(data_size,0)
print(len(data))

remote_info=info_conn.recv_infos()
data_size=remote_info['data_size']
mr=data_conn.reg_read(data_size)
data_conn.post_read(mr,data_size,remote_info['addr'],remote_info['rkey'])
info_conn.send_infos(read_finished=1)
data=mr.read(data_size,0)
print(len(data))
