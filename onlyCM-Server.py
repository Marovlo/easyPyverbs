#!/usr/bin/python3.8
from easyRDMACM import easyRDMACM
from tensorTools import TENSORTOOLS
info_conn=easyRDMACM()
info_conn.listen(src_ip='192.168.1.10',src_port=12345)
data_conn=easyRDMACM()
data_conn.listen(src_ip='192.168.1.10',src_port=12346)
tool=TENSORTOOLS()

data_size=info_conn.recv_infos()['data_size']
mr=data_conn.reg_write(data_size)
info_conn.send_infos(addr=mr.buf,rkey=mr.rkey)
send_finished=info_conn.recv_infos()['send_finished']
data=mr.read(data_size,0)
print(tool.byte_to_tensor(data))

remote_info=info_conn.recv_infos()
data_size=remote_info['data_size']
mr=data_conn.reg_read(data_size)
data_conn.post_read(mr,data_size,remote_info['addr'],remote_info['rkey'])
info_conn.send_infos(read_finished=1)
data=mr.read(data_size,0)
print(tool.byte_to_tensor(data))








