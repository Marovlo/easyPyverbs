#!/usr/bin/python3.8
from easyRDMACM import easyRDMACM
from tensorTools import TENSORTOOLS
conn=easyRDMACM()
conn.listen(src_ip='192.168.1.10',src_port=12345)
tool=TENSORTOOLS()


# for i in range(100):
#     # 验证recv & send
#     print(i)
#     if i%2==0:
#         data_size=conn.handshake()['data_size']
#         tensor=tool.byte_to_tensor(conn.recv(data_size))
#         print(data_size/1000/1000)
#     else:
#         data = tool.rand_tensor_byte((10, 10, 10, 10, 10, 10, 10, i))
#         conn.handshake(data_size=len(data))
#         conn.send(data)
#     #print(tensor)


# 验证write，完全使用原版cmid代码
a=dict()
a['addr']=10000
a['rkey']=123
conn.send_infos(addr=100,rkey=1234)







