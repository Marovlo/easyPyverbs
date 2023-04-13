import torch
from torch import Tensor
import io


class TENSORTOOLS():
    # 工具类，用于tensor和byte在内存里（不经过文件系统）的相互转换
    def __init__(self):
        self.buf=io.BytesIO()

    def tensor_to_byte(self,tensor:Tensor=not None):
        self.buf.flush()
        torch.save(obj=tensor,f=self.buf)
        return self.buf.getvalue()

    def byte_to_tensor(self,data:bytes=not None):
        self.buf.flush()
        self.buf.write(data)
        self.buf.seek(0)
        print(self.buf.getvalue())
        return torch.load(self.buf)
