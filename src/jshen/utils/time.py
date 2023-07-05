import datetime


def time_delta(days=0, seconds=0, microseconds=0,
               milliseconds=0, minutes=0, hours=0, weeks=0, print_=True):
    """
    从当前时间，往前或往后推移指定时间
    :return:
    """
    now = datetime.datetime.now()
    t = now + datetime.timedelta(days=days, seconds=seconds, microseconds=microseconds,
                                 milliseconds=milliseconds, minutes=minutes, hours=hours, weeks=weeks)

    if not print_:
        return t
    else:
        print(t)


if __name__ == '__main__':
    time_delta(hours=-1)
