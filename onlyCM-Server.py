#!/usr/bin/python3.8
from easyRDMACM import easyRDMACM
from tensorTools import TENSORTOOLS
conn=easyRDMACM()
conn.listen(src_ip='192.168.1.10',src_port=12345)
tool=TENSORTOOLS()


# # 验证recv & send
# data_size=conn.handshake()['data_size']
# tensor=tool.byte_to_tensor(conn.recv(data_size))
# print(tensor)
#
# # # 验证对端write，即本端建立mr供对端write
# data=conn.sync_write_recv()
# print(tool.byte_to_tensor(data))

# 验证read对端，即本端read对端已建立的内存
data=conn.sync_read_send()
print(tool.byte_to_tensor(data))