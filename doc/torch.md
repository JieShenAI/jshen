# 索引和切片
a = torch.arange(12).reshape(2,3,4)
a[:] = -1 等价于 a[::,::] = -1

.numel() torch的长度

对某个维度求和
a.sum(axis = 1)
对某个维度求均值
a.mean(axis = 1)

对某个维度求和后，该维度的轴会消失，若想保留该轴，设置keepdim = True
```python
J = torch.arange(12).view(2,3,2)
J_sum1 = J.sum(axis = 1, keepdim = True)
print(J_sum1)
print(J_sum1.shape)
```
累加求和
A.cumsum(axis=1)，逐步逐步地加

## 乘积

向量点积
torch.dot(a,b)

矩阵乘向量,torch.mv
> torch.Size([5, 4]), torch.Size([4]), tensor([ 14.,  38.,  62.,  86., 110.]))

矩阵乘矩阵
a@b,torch.mm(a,b)

范数
torch.norm(a)

若对向量求范数，则是p=2的范数||x||<sub>2</sub>

L1范数
torch.abs(a).sum()

矩阵的弗罗贝尼范乌斯范数，Frobenius norm ,||X||<sub>2</sub>
torch.norm(torch.ones(4,9))

在求下一个梯度时，对上一个梯度清0
x.grad.zero_()

对某个变量不求梯度,移记录的计算图之外
```python
y = x * x
u = y.detach()
z = u * x
z.sum().backward()
```
x.grad 等于 u

