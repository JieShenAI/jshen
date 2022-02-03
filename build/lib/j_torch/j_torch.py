# _*_coding     : UTF_8_*_
# Author        :Jie Shen
# CreatTime     :2022/2/2 15:34
# code from     :https://github.com/d2l-ai/d2l-zh/blob/master/d2l/torch.py

import torch
from matplotlib import pyplot as plt
from IPython import display

argmax = lambda x, *args, **kwargs: x.argmax(*args, **kwargs)
astype = lambda x, *args, **kwargs: x.type(*args, **kwargs)
reduce_sum = lambda x, *args, **kwargs: x.sum(*args, **kwargs)
size = lambda x, *args, **kwargs: x.numel(*args, **kwargs)


def shuffle(features):
    idx = torch.randperm(features.shape[0])
    return features[idx].view(features.size())


def synthetic_data(w, b, num_examples):
    """
    根据真实w,真实b,生成对应的label
    num_examples为生成的数量
      y = Xw + b + noise
    """
    x = torch.randn(num_examples, len(w))
    y = torch.matmul(x, w) + b
    # noise
    noise = torch.normal(0, 0.01, y.shape)
    y += noise
    return x, y.reshape(-1, 1)


def load_array(features, label, batch_size, shuffle):
    """
    data,label -> iter
    测试集，没必要shuffle，所以这里没有给shuffle指定默认值
    """
    dataset = torch.utils.data.TensorDataset(features, label)
    return torch.utils.data.DataLoader(dataset, batch_size, shuffle)


def train_epoch(net, trainer, loss, data_load, epochs):
    """
    通过dataload训练epochs次
    :param net:
    :param trainer:
    :param loss:
    :param data_load:
    :param epochs:
    :return:
    """
    for _ in range(epochs):
        for fea, lab in data_load:
            l = loss(net(fea), lab)
            trainer.zero_grad()
            l.backward()
            trainer.step()
            print('batch loss: {}'.format(l))


def train_one_epoch_loss_acc(net, train_iter, loss, updater):
    """训练模型一个迭代周期（定义见第3章）
    Defined in :numref:`sec_softmax_scratch`"""
    # 将模型设置为训练模式
    if isinstance(net, torch.nn.Module):
        net.train()
    # 训练损失总和、训练准确度总和、样本数
    metric = Accumulator(3)
    for X, y in train_iter:
        # 计算梯度并更新参数
        y_hat = net(X)
        l = loss(y_hat, y)
        if isinstance(updater, torch.optim.Optimizer):
            # 使用PyTorch内置的优化器和损失函数
            updater.zero_grad()
            l.mean().backward()
            updater.step()
        else:
            # 使用定制的优化器和损失函数
            l.sum().backward()
            updater(X.shape[0])
        metric.add(float(l.sum()), accuracy(y_hat, y), y.numel())
    # 返回训练损失和训练精度
    return metric[0] / metric[2], metric[1] / metric[2]


def draw_train_loss_acc_and_test_acc(net, train_iter, test_iter, updater, loss, num_epochs, ylim):
    """训练模型（定义见第3章）
    Defined in :numref:`sec_softmax_scratch`"""
    animator = Animator(xlabel='epoch', xlim=[1, num_epochs], ylim=ylim,
                        legend=['train loss', 'train acc', 'test acc'])
    for epoch in range(num_epochs):
        # 返回训练损失和训练精度
        train_metrics = train_one_epoch_loss_acc(net, train_iter, loss, updater)
        test_acc = evaluate_accuracy(net, test_iter)  # 计算在指定数据集上模型的精度
        animator.add(epoch + 1, train_metrics + (test_acc,))
    train_loss, train_acc = train_metrics
    assert train_loss < 0.5, train_loss
    assert 1 >= train_acc > 0.7, train_acc
    assert 1 >= test_acc > 0.7, test_acc


class Accumulator:
    """在n个变量上累加"""

    def __init__(self, n):
        """Defined in :numref:`sec_softmax_scratch`"""
        self.data = [0.0] * n

    def add(self, *args):
        self.data = [a + float(b) for a, b in zip(self.data, args)]

    def reset(self):
        self.data = [0.0] * len(self.data)

    def __getitem__(self, idx):
        return self.data[idx]


def accuracy(y_hat, y):
    """计算预测正确的数量
    Defined in :numref:`sec_softmax_scratch`"""
    if len(y_hat.shape) > 1 and y_hat.shape[1] > 1:
        y_hat = argmax(y_hat, axis=1)
    cmp = astype(y_hat, y.dtype) == y
    return float(reduce_sum(astype(cmp, y.dtype)))


def evaluate_accuracy(net, data_iter):
    """计算在指定数据集上模型的精度
    Defined in :numref:`sec_softmax_scratch`"""
    if isinstance(net, torch.nn.Module):
        net.eval()  # 将模型设置为评估模式
    metric = Accumulator(2)  # 正确预测数、预测总数
    with torch.no_grad():
        for X, y in data_iter:
            metric.add(accuracy(net(X), y), size(y))
    return metric[0] / metric[1]


class Animator:
    """在动画中绘制数据"""

    def __init__(self, xlabel=None, ylabel=None, legend=None, xlim=None,
                 ylim=None, xscale='linear', yscale='linear',
                 fmts=('-', 'm--', 'g-.', 'r:'), nrows=1, ncols=1,
                 figsize=(3.5, 2.5)):
        """Defined in :numref:`sec_softmax_scratch`"""
        # 增量地绘制多条线
        if legend is None:
            legend = []
        use_svg_display()
        self.fig, self.axes = plt.subplots(nrows, ncols, figsize=figsize)
        if nrows * ncols == 1:
            self.axes = [self.axes, ]
        # 使用lambda函数捕获参数
        self.config_axes = lambda: set_axes(
            self.axes[0], xlabel, ylabel, xlim, ylim, xscale, yscale, legend)
        self.X, self.Y, self.fmts = None, None, fmts

    def add(self, x, y):
        """
        训练损失，训练精度，测试精度
        :param x:
        :param y:
        :return:
        """

        # 向图表中添加多个数据点
        if not hasattr(y, "__len__"):
            y = [y]
        n = len(y)
        if not hasattr(x, "__len__"):
            x = [x] * n
        if not self.X:
            self.X = [[] for _ in range(n)]
        if not self.Y:
            self.Y = [[] for _ in range(n)]
        for i, (a, b) in enumerate(zip(x, y)):
            if a is not None and b is not None:
                self.X[i].append(a)
                self.Y[i].append(b)

        self.axes[0].cla()
        for x, y, fmt in zip(self.X, self.Y, self.fmts):
            self.axes[0].plot(x, y, fmt)
        self.config_axes()
        display.display(self.fig)
        display.clear_output(wait=True)


def use_svg_display():
    """使用svg格式在Jupyter中显示绘图
    Defined in :numref:`sec_calculus`"""
    display.set_matplotlib_formats('svg')


def set_axes(axes, xlabel, ylabel, xlim, ylim, xscale, yscale, legend):
    """设置matplotlib的轴
    Defined in :numref:`sec_calculus`"""
    axes.set_xlabel(xlabel)
    axes.set_ylabel(ylabel)
    axes.set_xscale(xscale)
    axes.set_yscale(yscale)
    axes.set_xlim(xlim)
    axes.set_ylim(ylim)
    if legend:
        axes.legend(legend)
    axes.grid()


def train_one_epoch_loss_acc(net, train_iter, loss, updater):
    """训练模型一个迭代周期（定义见第3章）
    Defined in :numref:`sec_softmax_scratch`
    返回 train loss 和 train acc
    """
    # 将模型设置为训练模式
    if isinstance(net, torch.nn.Module):
        net.train()
    # 训练损失总和、训练准确度总和、样本数
    metric = Accumulator(3)
    for X, y in train_iter:
        # 计算梯度并更新参数
        y_hat = net(X)
        l = loss(y_hat, y)
        if isinstance(updater, torch.optim.Optimizer):
            # 使用PyTorch内置的优化器和损失函数
            updater.zero_grad()
            l.mean().backward()
            updater.step()
        else:
            # 使用定制的优化器和损失函数
            l.sum().backward()
            updater(X.shape[0])
        metric.add(float(l.sum()), accuracy(y_hat, y), y.numel())
    # 返回训练损失和训练精度
    return metric[0] / metric[2], metric[1] / metric[2]
