#!/usr/bin/python3.8

from easyRDMACM import easyRDMACM
from tensorTools import TENSORTOOLS
info_conn=easyRDMACM()
info_conn.connect(dst_ip='192.168.1.10',dst_port=12345)
data_conn=easyRDMACM()
data_conn.connect(dst_ip='192.168.1.10',dst_port=12346)
tool=TENSORTOOLS()

data=tool.rand_tensor_byte((3,3))
data_size=len(data)
mr=data_conn.cmid.reg_write(data_size)
mr.write(data,data_size)
info_conn.send_infos(data_size=data_size)
remote_info=info_conn.recv_infos()
data_conn.cmid.post_write(mr,data_size,remote_info['addr'],remote_info['rkey'])
info_conn.send_infos(send_finished=1)