#!/usr/bin/python3.8
from easyRDMACM import easyRDMACM
from tensorTools import TENSORTOOLS
info_conn=easyRDMACM()
info_conn.listen(src_ip='192.168.1.10',src_port=12345)
data_conn=easyRDMACM()
data_conn.listen(src_ip='192.168.1.10',src_port=12346)
tool=TENSORTOOLS()









