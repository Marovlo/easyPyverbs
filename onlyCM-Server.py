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
data=tool.rand_tensor_byte((3,3))
data_size= len(data)
conn.handshake(data_size=data_size)
remote_info=conn.handshake()
mr=conn.cmid.reg_write(data_size)
mr.write(data,data_size)
conn.cmid.post_write(mr,data_size,remote_addr=remote_info['addr'],rkey=remote_info['rkey'])
conn.handshake()







