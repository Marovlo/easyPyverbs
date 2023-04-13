#!/usr/bin/python3.8
from easyCM import cmClient
from easyQP import easyQP,baseQP
from easyContext import easyContext
from tensorTools import TENSORTOOLS
import torch
import io


conn=cmClient(src_ip='0.0.0.0',dst_ip='192.168.1.10',dst_port=12345)
ctx=easyContext(dev_name='mlx5_1',port_num=1,index=3)
bqp=baseQP(context=ctx)
remote_info=conn.handshake(gid=ctx.local_gid,qpn=bqp.qpn)
print("server gid:",ctx.local_gid)
print("server qpn:",bqp.qpn)
print("client gid:",remote_info['gid'])
print("client qpn:",remote_info['qpn'])
qp=easyQP(context=ctx,baseqp=bqp,remote_gid=remote_info['gid'],remote_qpn=remote_info['qpn'])
qp.to_rts()

# 准备数据
tool=TENSORTOOLS()
data=tool.tensor_to_byte(tensor=torch.randn((3,3)))

# 准备使用write进行单向写入
# 使用write的一端需要提前获得对端的rkey和add，且不需要向对端同步本端的rkey和addr
# ps:应使用两次handshake，第一次本端告知对方将要写入多大内存，方便对端申请内存
# 第二次，应收到中write_size为告知对端本端将要写多大内存，而回收到的remote_info中
# 应该含有对端传来的rkey、addr，这需要在对端代码实现时按照要求编写
conn.handshake(write_size=len(data))
remote_info=conn.handshake()
qp.write(data=data,remote_key=remote_info['rkey'],remote_addr=remote_info['addr'])
# 告知对端写入完成
conn.handshake()

data=tool.tensor_to_byte(tensor=torch.randn((3,3)))
# 准备使用send进行双向同步写入
# 使用send的一端不需要获得rkey和addr，只需要对端同步进行recv操作即可
qp.send(data=data,conn=conn)