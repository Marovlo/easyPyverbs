# 在其他所有import之前执行这一步，让找寻pyverb的顺序正确
import sys
sys.path.insert(0, '/home/bupt/rdma-core/build/python/')

from builtins import str,int
from pyverbs.addr import GID
from pyverbs.cmid import AddrInfo, CMID
from pyverbs.wr import SGE, RecvWR, SendWR
from pyverbs.qp import QP, QPCap, QPInitAttr, QPAttr
from pyverbs.pd import PD
from pyverbs.mr import MR
from easyContext import easyContext
from pyverbs.cq import CQ
from pyverbs.addr import AH, AHAttr, GlobalRoute
from pyverbs.enums import *
from pyverbs.cm_enums import *
from easyCM import commonBase

import torch
import io
import time

class baseQP():
    # 由于要和对端交换qpn，所以本端需要先建立一个未初始化的qp，即将该未初始化的qp作为baseqp从原来的qp中分离出去
    # 作为先导任务，配合cm完成qpn的交换，方便后续使用easyQP进行连接建立
    def __init__(self,context:easyContext=not None):
        self.context=context.context
        self.index=context.index
        self.port_num=context.port_num
        # 好像是pyverbs里才有的，用于管理python里的垃圾回收顺序
        # A reference for the creating Context is kept so that Python's GC will destroy the objects in the right order.
        self.pd = PD(self.context)
        # completion queue，完成队列，用于告知send，write或read任务的完成情况，以及记录完成信息
        # cqe是cq的容量，
        self.cq = CQ(self.context, 100)
        # cap是一些基础信息，在context和cmid中都会用到
        # 参数很多，直接用默认的最简单
        # 官方定义缺省值：cap=QPCap(max_send_wr=1, max_recv_wr=10, max_send_sge=1,max_recv_sge=1, max_inline_data=0)
        # 教程定义缺省值：cap=QPCap(max_send_wr=16, max_recv_wr=16, max_send_sge=1,max_recv_sge=1, max_inline_data=0)
        self.cap = QPCap(max_send_wr=16, max_recv_wr=16, max_send_sge=1, max_recv_sge=1, max_inline_data=0)
        # qp_init_attr是初始化qp的参数,
        self.qp_init_attr = QPInitAttr(qp_type=IBV_QPT_RC, scq=self.cq, rcq=self.cq, cap=self.cap, sq_sig_all=True)
        self.qp = QP(self.pd, self.qp_init_attr)
        self.qpn=self.qp.qp_num

    # 使用baseqp创建一个简易mr，由于mr需要pd信息才能进行创建，而pd信息最早出现在baseqp中，所由baseqp来管理mr的创建
    def easyMR(self,mr_size:int=not None):
        mr=MR(self.pd,mr_size,IBV_ACCESS_LOCAL_WRITE | IBV_ACCESS_REMOTE_WRITE | IBV_ACCESS_REMOTE_READ)
        sgl = [SGE(mr.buf, mr.length, mr.lkey)]
        return mr,sgl

class easyQP():
    # 参数初始化
    def __init__(self,context:easyContext=not None,baseqp:baseQP=not None,
                 remote_gid:GID=not None,remote_qpn:int=not None):
        # 对端信息
        self.context=context.context
        self.index=baseqp.index
        self.port_num = context.port_num
        self.qp=baseqp.qp
        self.pd=baseqp.pd
        self.cq=baseqp.cq
        self.remote_gid=remote_gid
        self.remote_qpn=remote_qpn
        self.write_wr_id=1
        self.send_wr_id=2
        self.recv_wr_id=3
        # 可能是用于和gid配合进行route的组件,这里的index一定要和上面context中的index相同，不然就不能路由
        self.gr = GlobalRoute(dgid=self.remote_gid, sgid_index=self.index)
        # ah_attr是qa的基本参数，而qa是qp的attr，用于初始化qp和修改qp状态的
        self.ah_attr = AHAttr(gr=self.gr, is_global=1, port_num=self.port_num)
        # 初始化qa的属性，后续将绑定到qp上
        self.qa = QPAttr()
        self.qa.ah_attr = self.ah_attr
        self.qa.dest_qp_num = self.remote_qpn
        # 注意，mtu的设置不是直接写4096B，，填4096会errno 22，而是分级别
        # The Path MTU 0 ~ 4 (256/512/1024/2048/4096)（来自本项目教程-h）
        # 用ibv_devinfo enp1s0f1np1查看可以看到现在max_mtu是4096，并且后面有个小括号5，
        # 不知道小括号里写的5和教程里0-4哪个是对的
        # 经过测试，教程是错的！！！，没有0，填0会errno 22，所以其实是1-5，而5对应4096
        # 填6也会errno 22，所以正确值只有1-5
        self.qa.path_mtu = 5
        self.qa.max_rd_atomic = 1
        self.qa.max_dest_rd_atomic = 1
        # 设置qp的权限标志，这里是远程可读写，本地可写，没找到本地可读，可能默认就是本地可读
        self.qa.qp_access_flags = IBV_ACCESS_REMOTE_WRITE | IBV_ACCESS_REMOTE_READ | IBV_ACCESS_LOCAL_WRITE


    # 让上面创建的qp以qa中的参数进行一个状态的改变，从原本的init或者reset状态变成rtr状态，也就是ready to read
    # 感觉这是最重要且最容易出错的一步，这一步没报错感觉就是表示连接上了，后面的read和write应该都能运行
    # modify qp status
    def to_rtr(self):
        self.qp.to_rtr(self.qa)

    def to_rts(self):
        self.qp.to_rts(self.qa)

    # write函数是单向数据传输函数，需要配合cm进行控制信息的传输
    # easyQP中write相比于普通qp多出一个对方mr的可存储大小，在传输之前先请求对端注册足够大的内存，之后才能调用
    # 先使用cm获取对端所注册的内存的大小，作为一个必要参数填入，减少扩展性，提高可靠性(取消这个设定，如无必要，勿增需求)
    # write函数完成后，由于对端无法知道本端传输了多少以及是否传输完成，
    # 应视对端应用是否要取出该内存，选择是否使用sync通知对端应用传输已经完成
    def write(self,data:bytes=not None,remote_key:int=not None,
              remote_addr=not None):
        mr_size = len(data)
        mr=MR(self.pd,mr_size,IBV_ACCESS_LOCAL_WRITE | IBV_ACCESS_REMOTE_WRITE | IBV_ACCESS_REMOTE_READ)
        sgl=[SGE(mr.buf, mr.length, mr.lkey)]
        mr.write(data,mr_size)

        wr=SendWR(self.send_wr_id,opcode=IBV_WR_RDMA_WRITE,num_sge=1,sg=sgl)
        wr.set_wr_rdma(remote_key,remote_addr)
        self.qp.post_send(wr)
        print(f'write to remote gid:{self.remote_gid},qpn:{self.remote_qpn} '
              f'successfully.\nbyte_len:{mr_size}')

    # send函数是双向数据传输函数，在easyQP中需要配合cm进行控制信息的传输以及对端的recv函数进行数据的接收
    # 在easyQP中，send相比于普通qp多出一个对方mr可以存储的大小，在传输之前先请求对端注册足够大的内存，之后才能调用
    # 先使用cm获取对端所注册的内存的大小，作为一个必要参数填入，减少扩展性，提高可靠性(取消这个设定，如无必要，勿增需求)
    def send(self,data:bytes=not None,conn:commonBase=not None):
        mr_size=len(data)
        mr = MR(self.pd, mr_size, IBV_ACCESS_LOCAL_WRITE | IBV_ACCESS_REMOTE_WRITE | IBV_ACCESS_REMOTE_READ)
        sgl = [SGE(mr.buf, mr.length, mr.lkey)]
        mr.write(data, mr_size)
        wr=SendWR(self.send_wr_id,opcode=IBV_WR_SEND,num_sge=1,sg=sgl)


        wc_num, wc_list = 0,[]
        while wc_num==0:
            self.qp.post_send(wr)
            wc_num,wc_list=self.cq.poll()

        print(f'send to remote gid:{self.remote_gid},qpn:{self.remote_qpn} '
              f'successfully.\nbyte_len:{mr_size}')

    def recv(self,data_size:int=not None,conn:commonBase=not None):
        mr_size=data_size
        mr=MR(self.pd,mr_size,IBV_ACCESS_LOCAL_WRITE | IBV_ACCESS_REMOTE_WRITE | IBV_ACCESS_REMOTE_READ)
        sgl=[SGE(mr.buf,mr.length,mr.lkey)]
        wr=RecvWR(self.recv_wr_id,len(sgl),sgl)

        wc_num,wc_list=0,[]
        while wc_num==0:
            self.qp.post_recv(wr)
            wc_num, wc_list = self.cq.poll()

        print(f'receive from remote gid:{self.remote_gid},qpn:{self.remote_qpn} '
              f'successfully.\nbyte_len:{wc_list[0].byte_len}')
        return mr.read(wc_list[0].byte_len,0)







