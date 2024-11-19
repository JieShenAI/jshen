import time
import datetime


def time_delta(
    days=0,
    seconds=0,
    microseconds=0,
    milliseconds=0,
    minutes=0,
    hours=0,
    weeks=0,
    print_=True,
):
    """
    从当前时间，往前或往后推移指定时间
    :return:
    """
    now = datetime.datetime.now()
    t = now + datetime.timedelta(
        days=days,
        seconds=seconds,
        microseconds=microseconds,
        milliseconds=milliseconds,
        minutes=minutes,
        hours=hours,
        weeks=weeks,
    )

    if not print_:
        return t
    else:
        print(t)


def calculate_time_difference(start_time, end_time):
    """
    打印输出，end-start的时间差
    time.time()  # 记录开始与结束时间
    """
    elapsed_time = end_time - start_time
    hours, rem = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(rem, 60)
    milliseconds = (elapsed_time - int(elapsed_time)) * 1000

    print(
        f"executed in {int(hours):02}:{int(minutes):02}:{int(seconds):02}.{int(milliseconds):03} (h:m:s.ms)"
    )


def time_use(func):
    """
    修饰器：计算某个函数运行多长时间的
    """

    def wrapper(*args, **kwargs):
        start_time = time.time()  # 记录开始时间
        result = func(*args, **kwargs)  # 执行目标函数
        end_time = time.time()  # 记录结束时间

        elapsed_time = end_time - start_time
        hours, rem = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(rem, 60)
        milliseconds = (elapsed_time - int(elapsed_time)) * 1000

        print(
            f"Function '{func.__name__}' executed in {int(hours):02}:{int(minutes):02}:{int(seconds):02}.{int(milliseconds):03} (h:m:s.ms)"
        )
        return result

    return wrapper


if __name__ == "__main__":
    time_delta(hours=-1)
