import torch
from torch import Tensor
import io


class TENSORTOOLS():

    def tensor_to_byte(self,tensor:Tensor=not None):
        buf=io.BytesIO
        buf.flush()
        torch.save(obj=tensor,f=buf)
        return buf.getvalue()

    def byte_to_tensor(self,data:bytes=not None):
        buf = io.BytesIO
        buf.flush()
        buf.write(data)
        buf.seek(0)
        #print(buf.getvalue())
        return torch.load(buf)
