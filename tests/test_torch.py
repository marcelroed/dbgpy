import torch
from dbgpy import dbg

def test_torch_tensor():
    print()
    a = torch.randn((3, 3))
    dbg(a)
    print(a)
