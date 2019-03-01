# !/usr/bin/python3
# coding=utf-8
# @Time   : 2019/2/28/0028 10:51:33
# Author  : little star
# Func: 定时任务
"""
# 1. cron风格
    (int|str) 表示参数既可以是int类型，也可以是str类型
    (datetime | str) 表示参数既可以是datetime类型，也可以是str类型
    year (int|str) – 4-digit year -（表示四位数的年份，如2008年）
    month (int|str) – month (1-12) -（表示取值范围为1-12月）
    day (int|str) – day of the (1-31) -（表示取值范围为1-31日）
    week (int|str) – ISO week (1-53) -（格里历2006年12月31日可以写成2006年-W52-7（扩展形式）或2006W527（紧凑形式））
    day_of_week (int|str) – number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun) - （表示一周中的第几天，既可以用0-6表示也可以用其英语缩写表示）
    hour (int|str) – hour (0-23) - （表示取值范围为0-23时）
    minute (int|str) – minute (0-59) - （表示取值范围为0-59分）
    second (int|str) – second (0-59) - （表示取值范围为0-59秒）
    start_date (datetime|str) – earliest possible date/time to trigger on (inclusive) - （表示开始时间）
    end_date (datetime|str) – latest possible date/time to trigger on (inclusive) - （表示结束时间）
    timezone (datetime.tzinfo|str) – time zone to use for the date/time calculations (defaults to scheduler timezone) -（表示时区取值）
    # 如:在6,7,8,11,12月份的第三个星期五的00:00,01:00,02:00,03:00 执行该程序
    sched.add_job(my_job, 'cron', month='6-8,11-12', day='3rd fri', hour='0-3')
# 2.interval风格
    weeks (int) – number of weeks to wait
    days (int) – number of days to wait
    hours (int) – number of hours to wait
    minutes (int) – number of minutes to wait
    seconds (int) – number of seconds to wait
    start_date (datetime|str) – starting point for the interval calculation
    end_date (datetime|str) – latest possible date/time to trigger on
    timezone (datetime.tzinfo|str) – time zone to use for the date/time calculations
    #如:每隔2分钟执行一次
    scheduler.add_job(myfunc, 'interval', minutes=2)
# 3.date风格
    run_date (datetime|str) – the date/time to run the job at  -（任务开始的时间）
    timezone (datetime.tzinfo|str) – time zone for run_date if it doesn’t have one already
    # 如:在2009年11月6号16时30分5秒时执行
    sched.add_job(my_job, 'date', run_date=datetime(2009, 11, 6, 16, 30, 5), args=['text'])
"""
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_MAX_INSTANCES, EVENT_JOB_ERROR
scheduler = BackgroundScheduler()


def add(x, y):
    a = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    print("add: ", a)
    time.sleep(3)
    print(x + y)
    return x + y


def ppint():
    a = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    print("pprint: ", a)
    print("test...")


def listener(event):
    """
    event类其实继承了class apscheduler.events.JobExecutionEvent类,主要有以下属性:
    code, 状态码,详见这里
    job_id,
    jobstore,
    scheduled_run_time,计划运行时间
    retval=None, 执行成功时的返回值
    exception=None, 是否发生异常,上述代码就是判断了这个值是否为None,正常执行的话这里为None
    traceback=None
    """
    # 是否成功执行
    if event.code == EVENT_JOB_EXECUTED:
        print(event.scheduled_run_time)
        # 作业返回值
        print("return: ", event.retval)
    # 执行程序不接受提交给其执行程序的作业，因为该作业已达到其最大并发执行实例
    elif event.code == EVENT_JOB_MAX_INSTANCES:
        print("miss: ", event.job_id)


scheduler.add_job(ppint, "interval", seconds=5)
scheduler.start()
# add会每隔两秒执行一次，但add方法执行的时间是3秒，会将add执行的次数减少
# max_instances的用法：默认情况下同一个job，只允许一个job实例运行。
# 这在某个job在下次运行时间到达之后仍未执行完毕时，能达到控制的目的。
# 你也可以该变这一行为，在你调用add_job时可以传递max_instances=5来运行同时运行同一个job的5个job实例。
"""
apscheduler有默认的线程池数量和进程池数量，
如果定时任务过多，大于默认的数量，可能会导致有些任务在有些时间点被丢弃的情况

max_instances: 每个job在同一时刻能够运行的最大实例数,默认情况下为1个,可以指定为更大值,
这样即使上个job还没运行完同一个job又被调度的话也能够再开一个线程执行
coalesce:当由于某种原因导致某个job积攒了好几次没有实际运行（比如说系统挂了5分钟后恢复，
有一个任务是每分钟跑一次的，按道理说这5分钟内本来是“计划”运行5次的，但实际没有执行），
如果coalesce为True，下次这个job被submit给executor时，只会执行1次，也就是最后这次，
如果为False，那么会执行5次（不一定，因为还有其他条件，看下面的misfire_grace_time的解释）
misfire_grace_time:单位为秒,假设有这么一种情况,当某一job被调度时刚好线程池都被占满,
调度器会选择将该job排队不运行,misfire_grace_time参数则是在线程池有可用线程时会比对
该job的应调度时间跟当前时间的差值,如果差值<misfire_grace_time时,调度器会再次调度该job.
反之该job的执行状态为EVENT_JOB_MISSED了,即错过运行.
"""
scheduler.add_listener(listener, EVENT_JOB_MAX_INSTANCES | EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
scheduler.add_job(add, "interval", seconds=2, args=(1, 2), id="123", max_instances=2)

