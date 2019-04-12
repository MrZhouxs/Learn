# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time   : 2019/4/2/0002 15:01:06
# Author  : little star
# Func: python的四舍五入精确用法

from decimal import Decimal, ROUND_HALF_UP


def my_round(number, digits=None):
    # python自带的round函数不是很准确
    # print(round(number, ndigits=digits))
    if not isinstance(number, str):
        number = str(number)
    origin_num = Decimal(number)
    exp = "0."
    if digits is None or digits == 0:
        exp = "0"
    else:
        for _ in range(0, digits):
            exp += "0"
    answer_num = origin_num.quantize(Decimal(exp), rounding=ROUND_HALF_UP)
    return answer_num


if __name__ == '__main__':
    my_round(11.245)
