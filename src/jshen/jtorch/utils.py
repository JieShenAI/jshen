import torch
from torch import nn


def search_from_tensor(tensor, v: int):
    """
    Search for a value in a tensor and return the indices of the value.

    :param tensor: The tensor to search in.
    :param v: The value to search for.
    :return: The indices of the value in the tensor.
    """
    return torch.nonzero(tensor == v, as_tuple=True)


def set_seed(seed):
    """
    Set the seed for all the random number generators.
    :param seed:
    :return:
    """
    import numpy as np
    import random
    import os
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True


class demo(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(3, 1)

    def forward(self, x):
        return self.linear(x)


if __name__ == '__main__':
    set_seed(2023)
    a = torch.tensor([1., 2., 3.])
    d = demo()
    print(demo()(a))
    print(demo()(a))
