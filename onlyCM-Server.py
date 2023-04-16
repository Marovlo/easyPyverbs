#!/usr/bin/python3.8
from easyRDMACM import easyRDMACM
from tensorTools import TENSORTOOLS
info_conn=easyRDMACM()
info_conn.listen(src_ip='192.168.1.10',src_port=12345)
data_conn=easyRDMACM()
data_conn.listen(src_ip='192.168.1.10',src_port=12346)
tool=TENSORTOOLS()

data_size=info_conn.recv_infos()['data_size']
mr=data_conn.cmid.reg_msgs(data_size)
info_conn.send_infos(addr=mr.buf,rkey=mr.rkey)
send_finished=info_conn.recv_infos()['send_finished']
data=mr.read(data_size,0)
print(tool.byte_to_tensor(data))








