#　type()

我想要type(stu())，返回`com.jshen.stu`,How to make it?

```python
class stu:
    def __init__(self):
        pass

    __module__ = 'jshen'

if __name__ == '__main__':
    s = stu()
    print(type(s))
```
type(s): <class 'jshen.stu'>