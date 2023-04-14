#!/usr/bin/python3.8

from easyRDMACM import easyRDMACM
from tensorTools import TENSORTOOLS
conn=easyRDMACM()
conn.listen(src_ip='192.168.1.10',src_port=12345)
tool=TENSORTOOLS()


# 验证recv & send
data_size=conn.handshake()['data_size']
tensor=tool.byte_to_tensor(conn.recv(data_size))
print(tensor)

# 验证对端write，即本端建立mr供对端write
data_size=conn.handshake()['data_size'] # 获取对端要写入的大小
mr=conn.reg_mr(size=data_size) # 注册对应大小的内存
conn.handshake(remote_addr=mr.buf,remote_key=mr.rkey) # 告知对端内存的地址和key
conn.handshake() # 等待对端告知写入完成
tensor=tool.byte_to_tensor(mr.read(data_size,0))
print(tensor)

# 验证本端read，即对端建立mr供本端read
data_size=conn.handshake()['data_size']

