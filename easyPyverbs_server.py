#!/usr/bin/python3.8

from easyCM import cmServer
from easyQP import easyQP,baseQP
from easyContext import easyContext
from tensorTools import TENSORTOOLS
conn=cmServer(src_ip='0.0.0.0',src_port=12345)
ctx=easyContext(dev_name='mlx5_1',port_num=1,index=3)
bqp=baseQP(ctx)
remote_info=conn.handshake(gid=ctx.local_gid,qpn=bqp.qpn)
print("local gid:",ctx.local_gid)
print("local qpn:",bqp.qpn)
print("remote gid:",remote_info['gid'])
print("remote qpn:",remote_info['qpn'])
qp=easyQP(context=ctx,baseqp=bqp,remote_gid=remote_info['gid'],remote_qpn=remote_info['qpn'])
qp.to_rtr()
print(qp.qp.qp_state)

tool=TENSORTOOLS()

# 准备接受对端的write
# 对端告知本端即将进行的write_size
write_size=conn.handshake()['write_size']
# 根据write_size申请内存
mr,_=bqp.easyMR(write_size)
# 告知对端本端的内存地址和rkey
conn.handshake(addr=mr.buf,rkey=mr.rkey)
# 对端告知本端写入完成
conn.handshake()

print("read from remote:",tool.byte_to_tensor(mr.read(write_size,0)))

# 准备接受对端的send
print("recv from remote:",qp.recv())