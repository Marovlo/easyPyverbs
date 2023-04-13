#!/usr/bin/python3.8
#后面要用的globals()函数返回的类型转换函数
from builtins import str,int
from pyverbs.addr import GID

# 无参同步消息msy
sync_msg="msy"

class commonBase:
    def __init__(self):
        self.cmid:CMID=None

    @staticmethod
    def prepare_send_msg(self, **kwargs):
        send_message = ''
        for key, value in kwargs.items():
            # 将需要握手的信息转换成str，并记录value的类型
            send_message += key + '-' + \
                            type(value).__name__ + '-' + str(value) + ';'
        return send_message

    @staticmethod
    def prase_recv_msg(self, recv_message: str):
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
        reserved_size = 1024
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

    def synchronize(self):
        '''
        这个函数需要双边同时执行，和handshake功能流程相同，只不过不能传输指定参数
        这个函数的作用是同步服务器和客户端的进程，特别是在建立qp时，如果服务器先收到握手信息，
        而客户端还没收到，此时服务器开始建立qp会报错，因为客户端还没准备好
        报错为Failed to modify QP state to RTR. Errno: 22, Invalid argument
        这里argument就是指qa，而qa包含对方的qpn，对方的qp此时还没准备好
        上面都是我猜的，反正没这个同步函数就会报错，我觉得应该还有更好的解决办法
        '''
        print("synchronizing with client...",end=' ')

        send_msg=sync_msg.encode('utf-8')
        reserve_size=10
        size=len(send_msg)

        # 接收同步信息
        recv_mr=self.cmid.reg_msgs(size+reserve_size)
        self.cmid.post_recv(recv_mr,size)

        # 发送同步信息
        send_mr=self.cmid.reg_msgs(size)
        send_mr.write(send_msg,size)
        self.cmid.post_send(send_mr,0,size)

        # 接受队列完成，表示接收到数据，且接收到的数据长度存储在完成队列wc中
        recv_wc = self.cmid.get_recv_comp()
        recv_msg = recv_mr.read(recv_wc.byte_len, 0).decode('utf-8')
        if recv_msg!=sync_msg:
            print('synchronization failed!')
            exit(-1)

        # 发送队列完成，表示数据成功发送
        send_wc = self.cmid.get_send_comp()

        print("synchronized!")








