# coding=utf-8
# @Time   : 2019/2/28/0028 15:34:49
# Author  : little star
# Func : python解析Cron表达式
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
from apscheduler.schedulers.background import BackgroundScheduler


class Cron(object):

    FIELD_NAMES = ('year', 'month', 'day', 'week', 'day_of_week', 'hour', 'minute', 'second')

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

    def from_cron_expr(self, expr):
        """
        解析cron表达式
        :param expr: cron表达式
        :type expr: str
        :return:
        :rtype: dict
        """
        # cron表达式不可有 ？字段，解析不了
        # 5位没有second和year，6位没有year
        # 先将表达式中含有 ? 的转换成 *
        expr = expr.replace("?", "*")
        values = expr.split()
        length_of_expr = len(values)
        if length_of_expr == 5:
            return {"minute": values[0], "hour": values[1], "day": values[2], "month": values[3],
                    "day_of_week": values[4]}
        elif length_of_expr == 6:
            return {"second": values[0], "minute": values[1], "hour": values[2], "day": values[3],
                    "month": values[4], "day_of_week": values[5]}
        elif length_of_expr == 7:
            return {"second": values[0], "minute": values[1], "hour": values[2], "day": values[3],
                    "month": values[4], "day_of_week": values[5], "year": values[6]}
        else:
            raise ValueError('Wrong number of fields; got {}, '
                             'expected 5 or 6 or 7'.format(len(values)))

    def get_next_fire_time(self, expr):
        """
        计算cron表达式的下次执行时间
        :param expr: cron表达式
        :type expr: str
        :return: 下次执行时间
        :rtype: datetime.datetime
        """
        # 辅助函数，不做任何事情
        def _():
            pass
        try:
            fields = self.from_cron_expr(expr)
            second = fields.get("second", "*")
            minute = fields.get("minute", "*")
            hour = fields.get("hour", "*")
            day = fields.get("day", "*")
            month = fields.get("month", "*")
            day_of_week = fields.get("day_of_week", "*")
            year = fields.get("year", "*")
            job = self.scheduler.add_job(_, 'cron', second=second, minute=minute, hour=hour,
                                         month=month, day=day, day_of_week=day_of_week, year=year)
            r = job.next_run_time
            job.remove()
            return r
        except Exception as ex:
            print(ex)
        return None


if __name__ == '__main__':
    a = Cron()
    b = a.get_next_fire_time("0 0 12 ? * WED")
    print(b)
    next_time = a.get_next_fire_time("0 0 0,13,18,21 * * ?")
    print(next_time)

