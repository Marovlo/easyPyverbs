from easyPyverbs.cmServer import cmServer
from easyPyverbs.easyQP import easyQP,baseQP
from easyPyverbs.easyContext import easyContext

conn=cmServer(src_ip='0.0.0.0',src_port=12345)
ctx=easyContext(dev_name='mlx5_1',port_num=1,index=3)
bqp=baseQP(ctx)
remote_info=conn.handshake(gid=ctx.local_gid,qpn=bqp.qpn)
qp=easyQP(context=ctx,baseqp=bqp,remote_gid=remote_info['gid'],remote_qpn=remote_info['qpn'])
qp.to_rtr()
print(qp.qp.qp_state)
