# 在其他所有import之前执行这一步，让找寻pyverb的顺序正确
import sys
sys.path.insert(0, '/home/bupt/rdma-core/build/python/')

from connection import commonBase

from pyverbs.cmid import AddrInfo, CMID
from pyverbs.qp import QPCap, QPInitAttr
from pyverbs.cm_enums import *
from pyverbs.mr import MR
import enum


class easyRDMACM():
    def __init__(self):
        self.qpcap=QPCap()
        self.qp_init_attr=QPInitAttr(cap=self.qpcap)

    def listen(self,src_ip: str = not None,src_port:int=not None):
        '''
        该函数会阻塞，然后监听给出的ip和port，直到连接成功
        :param src_port:
        :param src_ip:
        :return: 无返回值
        '''
        self.cai=AddrInfo(src=src_ip, src_service=str(src_port),
                       port_space=RDMA_PS_TCP, flags=RAI_PASSIVE)
        cmid=CMID(creator=self.cai, qp_init_attr=self.qp_init_attr)
        cmid.listen()  # cmid有点类似qt中的qsocketserver，listen会阻塞进程
        # 这个函数类似qt中qsocketserver的nextPendingConnection，只不过返回的类型也是一个cmid
        mycmid = cmid.get_request()
        mycmid.accept()
        cmid.close()  # 只需要一个cmid就够了
        self.cmid = mycmid

    def connect(self,dst_ip: str, dst_port: int = 12345, src_ip: str = '0.0.0.0'):
        '''
        该函数会阻塞，然后尝试连接所给出的ip和port，直到连接成功
        :param dst_ip:
        :param dst_port:
        :param src_ip:
        :return: 无返回值
        '''
        self.cai=AddrInfo(src=src_ip, dst=dst_ip,
                       dst_service=str(dst_port), port_space=RDMA_PS_TCP)
        self.cmid = CMID(creator=self.cai, qp_init_attr=self.qp_init_attr)
        self.cmid.connect()

    def disconnect(self):
        self.cmid.disconnect()

    def reg_msgs(self,size:int=not None):
        '''
        该函数注册用于send和recv双向操作（控制信息）的内存mr
        :param size: 需要的内存大小
        :return: 注册成功的mr
        '''
        return self.cmid.reg_msgs(size)

    def reg_write(self,size:int=not None):
        '''
        该函数注册用于存储write到对端之前先存储在本地的数据的内存mr
        :param size: 需要的内存大小
        :return: 注册成功的mr
        '''
        return self.cmid.reg_write(size)

    def reg_read(self,size:int=not None):
        '''
        该函数注册用于存储read对端内存之后要存储在本地的数据的内存mr
        :param size: 需要的内存大小
        :return: 注册成功的mr
        '''
        return self.cmid.reg_read(size)

    def recv(self,data_size:int=not None):
        '''
        post一个接收wr请求，由于是接收，所以size就是本地接收内存的大小，但是涉及到对方要传多大，所以还是要填data大小
        :param mr:
        :return: 返回接受到的byte
        '''
        mr = self.cmid.reg_msgs(data_size)
        self.cmid.post_recv(mr,mr.length)
        wc=self.cmid.get_recv_comp()
        return mr.read(wc.byte_len,0)

    def send(self,data:bytes=not None):
        '''
        post一个发送wr请求，由于是发送，参数需要所发送的数据的长度，这和请求存储的长度可以不同
        :param mr:
        :return: 无返回值，请用get_send_comp查询发送是否成功
        '''
        data_size=len(data)
        mr=self.cmid.reg_msgs(data_size)
        mr.write(data,data_size)
        self.cmid.post_send(mr,data_size)

    def read(self,data_size:int=not None,
                  remote_addr=not None,remote_key=not None):
        '''
        读对端内存的请，data_size是要读的大小
        （这里存疑，不清楚到底是对面mr有多大读多大还是这里写一个参数可以限制读多大，倾向于有多大读多大
        因为qp里read也没有写大小：def wr_rdma_read(self, rkey, remote_addr):
        ）
        :param mr:
        :param data_size:
        :param remote_addr:
        :param remote_key:
        :return: 返回值为读到的byte
        '''
        mr=self.reg_read(data_size)
        self.cmid.post_read(mr,data_size,remote_addr,remote_key)
        return mr.read(data_size,0)

    def write(self,data:bytes=not None,
              remote_addr=not None,remote_key=not None):
        '''
        写对端的内存，data是要写入的大小
        :param data:
        :param remote_addr:
        :param remote_key:
        :return: 无返回值
        '''
        data_size= len(data)
        mr=self.reg_write(data_size)
        self.cmid.post_write(mr,data_size,remote_addr,remote_key)

    def post_recv(self,mr:MR=not None):
        '''
        post一个接收wr请求，由于是接收，所以size就是本地接收内存的大小，就不用再填了
        :param mr:
        :return: 无返回值，请用get_recv_comp查询接收是否成功
        '''
        self.cmid.post_recv(mr,mr.length)

    def post_send(self,mr:MR=not None,data_size:int=not None):
        '''
        post一个发送wr请求，由于是发送，参数需要所发送的数据的长度，这和请求存储的长度可以不同
        :param mr:
        :return: 无返回值，请用get_send_comp查询发送是否成功
        '''
        self.cmid.post_send(mr,data_size)

    def post_read(self,mr:MR=not None,
                  remote_addr=not None,remote_key=not None):
        '''
        post一个读对端内存的请求，mr是用于存储read到的数据的内存，
        由于是单端操作read，所以读到的数据大小又对端存储的mr的大小决定
        （这里存疑，不清楚到底是对面mr有多大读多大还是这里写一个参数可以限制读多大，倾向于有多大读多大
        因为qp里read也没有写大小：def wr_rdma_read(self, rkey, remote_addr):
        ）
        :param mr:
        :param data_size:
        :param remote_addr:
        :param remote_key:
        :return: 无返回值，请直接读取mr内存查看
        '''
        self.cmid.post_read(mr,mr.length,remote_addr,remote_key)

    def post_write(self,mr:MR=not None,
                  remote_addr=not None,remote_key=not None):
        '''
        post一个写对端内存的请求，mr是用于存储要write到对端的数据的内存，
        由于是单端操作write，所以对端根本不知道，我们也不需要知道写了多少
        :param mr:
        :param remote_addr:
        :param remote_key:
        :return:
        '''
        self.post_write(mr,mr.length,remote_addr,remote_key)

    def get_recv_comp(self):
        '''
        获取recv操作的完成队列，从中可以看到一共接收到多少数据
        :return: 返回完成队列
        '''
        return self.cmid.get_recv_comp()

    def get_send_comp(self):
        '''
        获取send操作的完成队列，从而得知send是否完成
        :return: 返回完成队列
        '''
        return self.cmid.get_send_comp()

    def prepare_send_msg(self,**kwargs):
        send_message = ''
        for key, value in kwargs.items():
            # 将需要握手的信息转换成str，并记录value的类型
            send_message += key + '-' + \
                            type(value).__name__ + '-' + str(value) + ';'
        return send_message

    def prase_recv_msg(self,recv_message: str):
        info = dict()
        for amsg in recv_message.split(';'):
            item = amsg.split('-')
            if len(item) == 3:
                key, value_type, value = item
                # globals函数返回所有导入的全局变量的dict，用对应key返回对应函数
                info[key] = globals()[value_type](value)
        return info

    def handshake(self, **kwargs):
        '''
        该函数必须双向调用，不然会阻塞，最好只用于qpn等同步消息的发送，当handshake不传入参数时，为同步
        :param kwargs:
        :return:
        '''
        print("handshaking infos...", end=' ')
        # 给接受数据的内存稍微大一点的空间防止出问题，但实际上感觉得提前沟通大小，不然再大的空间都有可能出问题
        reserved_size = 100
        send_msg:bytes
        # 如果不传参，则为单纯同步，即sycn
        if len(kwargs) == 0:
            send_msg='msy'.encode('utf-8')
        # 由于utf编码后中文为3字节而不是1字节，所以len得放在encode编码后计算
        else:
            send_msg = self.prepare_send_msg(**kwargs).encode('utf-8')
        size = len(send_msg)

        # todo：handshake size limit

        # 准备接受数据，有点不清楚这个post_recv函数是阻塞还是不阻塞
        # 感觉是阻塞的话有点说不通
        # 是不是一个cmid在同一时间只能有一个注册的用于存放msgs的内存，不然怎么管理呢
        # 为什么post_recv的时候又只需要size的大小呢？万一对方发送的数据不止size大小呢（这一个问题在后面几行代码中解答）
        recv_mr = self.cmid.reg_msgs(size + reserved_size)
        self.cmid.post_recv(recv_mr, size + reserved_size)

        # 准备发送数据
        send_mr = self.cmid.reg_msgs(size)
        send_mr.write(send_msg, size)
        self.cmid.post_send(send_mr, 0, size)

        # 接受队列完成，表示接收到数据，且接收到的数据长度存储在完成队列wc中
        recv_wc = self.cmid.get_recv_comp()
        recv_msg = recv_mr.read(recv_wc.byte_len, 0).decode('utf-8')

        # 发送队列完成，表示数据成功发送
        send_wc = self.cmid.get_send_comp()
        print("handshaked!")

        if recv_msg=='msy':
            return
        else:
            return self.prase_recv_msg(recv_msg)
