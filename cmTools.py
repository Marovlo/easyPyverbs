# 在其他所有import之前执行这一步，让找寻pyverb的顺序正确
import sys
sys.path.insert(0, '/home/bupt/rdma-core/build/python/')

from connection import commonBase

from pyverbs.cmid import AddrInfo, CMID
from pyverbs.qp import QPCap, QPInitAttr
from pyverbs.cm_enums import *

def create_CM_server(src_ip:str=not None,src_port:int=not None):
    '''
    该函数根据传入的srcip和port进行监听，等待client的连接，并返回连接成功的cmid
    该函数会阻塞，直到client连接成功
    :param src_ip:
    :param src_port:
    :return: 连接成功的cmid
    '''
    # 奇怪为什么不需要context和dev_name之类的信息，他怎么知道要在哪个设备上建立连接？
    # 初始化qp_init_attr需要使用的信息，并不用绑定到某个确定的qp上,cmid里有qp，最后应该是绑定到cmid中的qp中
    qpcap = QPCap()
    # 初始化qp所需要的信息，可以直接传到cmid中初始化qp，也可以等cmid连接上之后再自行新建qp
    qp_init_attr = QPInitAttr(cap=qpcap)
    # cmid的连接属性；其中port_space只支持TCP；
    # 其中flags=RAI_PASSIVE不知道有什么用，但是必须写，猜测是表示这是服务器，用于passive被动地等待client连接
    # 测试结果，如果是服务器，即有src和src_service，则必须声明flags=passive
    # 如果是客户端，则创建CMID时必须指定qp_init_attr
    cai = AddrInfo(src=src_ip, src_service=str(src_port),
                   port_space=RDMA_PS_TCP, flags=RAI_PASSIVE)
    cmid = CMID(creator=cai, qp_init_attr=qp_init_attr)
    # cmid=CMID(creator=cai)
    cmid.listen()  # cmid有点类似qt中的qsocketserver，listen会阻塞进程
    # 这个函数类似qt中qsocketserver的nextPendingConnection，只不过返回的类型也是一个cmid
    mycmid = cmid.get_request()
    mycmid.accept()
    cmid.close()  # 只需要一个cmid就够了
    return mycmid

def create_cm_client(dst_ip:str=not None,dst_port:str=not None,src_ip: str = '0.0.0.0'):
    '''
    该函数会去尝试连接给出的地址，并返回连接成功的cmid
    :param dst_ip:
    :param dst_port:
    :param src_ip:
    :return: 连接成功的cmid
    '''
    # 初始化qp_init_attr需要使用的信息，并不用绑定到某个确定的qp上,cmid里有qp，最后应该是绑定到cmid中的qp中
    super().__init__()
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
    return cmid