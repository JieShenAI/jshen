# from jspider import get_delta_time
# from jshen.spider import get_delta_time
import pickle


class Stu:
    def __init__(self, age=10):
        self.age = age

    def __str__(self):
        return "Stu age: {}".format(self.age)


if __name__ == '__main__':
    stu = Stu(age=102)
    # pickle.dump(stu, open("stu.pkl", "wb"))
    d = pickle.load(open("stu.pkl", "rb"))
    print(d)
