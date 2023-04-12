from connection import commonBase

from pyverbs.cmid import AddrInfo, CMID
from pyverbs.qp import QPCap, QPInitAttr
from pyverbs.cm_enums import *

class cmClient(commonBase):
    def __init__(self,dst_ip:str,dst_port:int=12345,src_ip:str='0.0.0.0'):
        # 初始化qp_init_attr需要使用的信息，并不用绑定到某个确定的qp上,cmid里有qp，最后应该是绑定到cmid中的qp中
        qpcap = QPCap()
        # 初始化qp所需要的信息，可以直接传到cmid中初始化qp，也可以等cmid连接上之后再自行新建qp
        qp_init_attr = QPInitAttr(cap=qpcap)
        # cmid的连接属性；其中port_space只支持TCP；
        # 其中flags=RAI_PASSIVE不知道有什么用，但是必须写，猜测是表示这是服务器，用于passive被动地等待client连接
        # 测试结果，如果是服务器，即有src和src_service，则必须声明flags=passive
        # 如果是客户端，则创建CMID时必须指定qp_init_attr
        cai = AddrInfo(src=src_ip, dst=dst_ip,
                       dst_service=str(dst_port), port_space=RDMA_PS_TCP)
        cmid = CMID(creator=cai, qp_init_attr=qp_init_attr)
        # cmid=CMID(creator=cai)
        cmid.connect()
        self.cmid = cmid#
