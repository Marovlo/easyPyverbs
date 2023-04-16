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
data_size=conn.recv_infos()['data_size'] # 接受对端要发送的data_size
print('data_size:',data_size)
mr=conn.cmid.reg_msgs(data_size)
conn.send_infos(addr=mr.buf,rkey=mr.rkey)
print("addr:",mr.buf,"rkey:",mr.rkey)

send_finished=conn.recv_infos()['send_finished']
print('send_finished:',send_finished)

# data=conn.recv_infos()['data']
# conn.send_infos(size=100)
# conn.send_infos(data='abcd')
# data=conn.recv_infos()['size']
# data=conn.recv_infos()['data']
# conn.send_infos(size=100)
# conn.send_infos(data='abcd')
# data=conn.recv_infos()['size']







