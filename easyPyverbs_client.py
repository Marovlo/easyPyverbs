from easyPyverbs.easyCM import cmClient
from easyPyverbs.easyQP import easyQP,baseQP
from easyPyverbs.easyContext import easyContext


conn=cmClient(src_ip='0.0.0.0',dst_ip='192.168.1.10',dst_port=12345)
ctx=easyContext(dev_name='mlx5_1',port_num=1,index=3)
bqp=baseQP(context=ctx)
remote_info=conn.handshake(gid=ctx.local_gid,qpn=bqp.qpn)
qp=easyQP(context=ctx,baseqp=bqp,remote_gid=remote_info['gid'],remote_qpn=remote_info['qpn'])
qp.to_rts()
print(qp.qp.qp_state)
