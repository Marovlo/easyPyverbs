# 在其他所有import之前执行这一步，让找寻pyverb的顺序正确
import sys
sys.path.insert(0, '/home/bupt/rdma-core/build/python/')

from pyverbs.device import Context

class easyContext():
    # 由于要先和对端交换gid，所以要先初始化context用于获取本端gid用于交换，
    # 所以将context从easyQP中独立出来，作为先导完成任务，与cm配合
    def __init__(self,dev_name:str=not None,port_num:int=1,index:int=1):
        # 设备信息，告知qp所使用的设备，用于初始化qp,cq等队列
        self.dev_name=dev_name
        self.port_num=port_num
        self.index=index
        self.context = Context(name=dev_name)
        # 获取当前设备的gid，相当于tcpip中的IP地址，端口默认都是1，这里使用的设备是mlx5_1的rocev2的配置了ipv4的，其对应index为3
        self.local_gid = self.context.query_gid(port_num=port_num, index=index)