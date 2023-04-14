#!/usr/bin/python3.8

from easyRDMACM import easyRDMACM
from tensorTools import TENSORTOOLS
conn=easyRDMACM()
conn.listen(src_ip='192.168.1.10',src_port=12345)
tool=TENSORTOOLS()
data_size=conn.handshake()['data_size']
print(data_size)



