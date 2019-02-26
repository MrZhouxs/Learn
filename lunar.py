# !/usr/bin/python3
# coding=utf-8
# @Time   : 2019/2/26/0026 14:04:07
# Author  : little star
# Func: 获取公历、农历

import sxtwl
# 天干
Gan = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
# 地支
Zhi = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
# 生肖
ShX = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]
#
numCn = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
# 星期几
Week = ["日", "一", "二", "三", "四", "五", "六"]
# 节气
jqmc = ["冬至", "小寒", "大寒", "立春", "雨水", "惊蛰", "春分", "清明", "谷雨", "立夏", "小满",
        "芒种", "夏至", "小暑", "大暑", "立秋", "处暑", "白露", "秋分", "寒露", "霜降", "立冬",
        "小雪", "大雪"]
# 农历月名称
ymc = [u"十一", u"十二", u"正", u"二", u"三", u"四", u"五", u"六", u"七", u"八", u"九", u"十"]
# 农历日名称
rmc = [u"初一", u"初二", u"初三", u"初四", u"初五", u"初六", u"初七", u"初八", u"初九", u"初十",
       u"十一", u"十二", u"十三", u"十四", u"十五", u"十六", u"十七", u"十八", u"十九",
       u"二十", u"廿一", u"廿二", u"廿三", u"廿四", u"廿五", u"廿六", u"廿七", u"廿八", u"廿九",
       u"三十", u"卅一"]


class Lunar(object):
    def __init__(self):
        self.lunar = sxtwl.Lunar()

    def lunar_or_solar(self, year, month, day, is_lunar=False, leap_month=False):
        """
        判断当前时间是否是农历还是公历，对应不同的解析方法
        :param year: 年
        :param month: 月
        :param day: 日
        :param is_lunar: 是否是农历
        :param leap_month: 是否是润月
        :return:
        """
        if is_lunar:
            _lunar_or_solar = self.lunar.getDayByLunar(year, month, day, leap_month)
        else:
            _lunar_or_solar = self.lunar.getDayBySolar(year, month, day)
        return _lunar_or_solar

    def gregorian2lunar(self, year, month, day):
        """
        将公历的日期换算成农历的日期
        :param year: 公历日期的年
        :param month: 公历日期的月
        :param day: 公历日期的日
        :return: 农历的年，月，日
        """
        solar = self.lunar_or_solar(year, month, day, is_lunar=False)
        # 获取属于农历的年份
        solar_year = solar.Lyear0 + 1984
        # 获取属于农历的月份
        solar_month = ymc[solar.Lmc]
        # 获取属于农历的月中的哪一天
        solar_day = rmc[solar.Ldi]
        return solar_year, solar_month, solar_day

    def lunar2gregorian(self, year, month, day, leap_month=False):
        """
        将农历的日期换算成公历的日期
        :param year: 农历的日期的年
        :param month: 农历的日期的月
        :param day: 农历日期的日
        :param leap_month: 是否是润月
        :return: 公历的年，月，日
        """
        lunar = self.lunar_or_solar(year, month, day, True, leap_month)
        lunar_year = lunar.y
        lunar_month = lunar.m
        lunar_day = lunar.d
        return lunar_year, lunar_month, lunar_day

    def solar_terms(self, year, month, day, is_lunar=False, leap_month=False):
        """
        获取当前时间的节气以及发生的时间
        :param year: 年
        :param month: 月
        :param day: 日
        :param leap_month: 是否是润月
        :param is_lunar: 当前时间是否是农历
        :return:
        """
        # 当日节气
        solar_term = None
        # 节气发生的时间
        solar_time = None
        # 当前时间是农历
        solar = self.lunar_or_solar(year, month, day, is_lunar, leap_month)

        if solar.qk >= 0:
            solar_term = jqmc[solar.jqmc]
            solar_time = solar.jqsj
        return solar_term, solar_time

    def week(self, year, month, day, is_lunar=False, leap_month=False):
        """
        获取当期时间是星期几
        :param year: 年
        :param month: 月
        :param day: 日
        :param is_lunar: 是否是农历时间
        :param leap_month: 是否是润月
        :return: 大写的星期几，小写的星期几
        """
        solar = self.lunar_or_solar(year, month, day, is_lunar, leap_month)
        week_index = solar.week
        which_day_of_week = Week[week_index]
        return which_day_of_week, week_index

    def tg_dz_by_date(self, year, month, day, hour=None, is_lunar=False, leap_month=False):
        """
        获取年月日格式的天干地址
        :param year: 年
        :param month: 月
        :param day: 日
        :param hour: 小时（24点格式）
        :param is_lunar: 是否是农历时间
        :param leap_month: 是否是润月
        :return:
        """
        obj = self.lunar_or_solar(year, month, day, is_lunar, leap_month)
        year_tg_dz = Gan[obj.Lyear2.tg] + Zhi[obj.Lyear2.dz]
        month_tg_dz = Gan[obj.Lmonth2.tg] + Zhi[obj.Lmonth2.dz]
        day_tg_dz = Gan[obj.Lday2.tg] + Zhi[obj.Lday2.dz]
        if hour is None:
            return year_tg_dz, month_tg_dz, day_tg_dz
        else:
            gz = self.lunar.getShiGz(obj.Lday2.tg, hour)
            hour_tg_dz = Gan[gz.tg] + Zhi[gz.dz]
            return year_tg_dz, month_tg_dz, day_tg_dz, hour_tg_dz

    def year_cal(self, year):
        """
        计算年的天干地支和生肖，2018年是戊戌年，狗年
        :param year: 年
        :return:
        """
        year = self.lunar.getYearCal(year)
        year_tg_dz = Gan[year.yearGan] + Zhi[year.yearZhi]
        year_sx = ShX[year.ShX]
        return year_tg_dz, year_sx

    def zodiac(self, year, month):
        obj = self.lunar.yueLiCalc(year, month)
        year_tg_dz = Gan[obj.yearGan] + Zhi[obj.yearZhi]
        sx = ShX[obj.ShX]
        return year_tg_dz, sx


if __name__ == '__main__':
    a = Lunar()
    print(a.gregorian2lunar(1994, 7, 22))
    print(a.lunar2gregorian(1970, 6, 14))
    print(a.solar_terms(2019, 3, 6, is_lunar=False))
    print(a.week(1995, 8, 8, True))
    print(a.tg_dz_by_date(1994, 6, 14, 12, True))
    print(a.year_cal(1994))
    print(a.zodiac(1994, 7))

