# !/usr/bin/python3
# coding=utf-8
# @Time   : 2019/3/25/0025 16:04:54
# Author  : little star

import os
import time


def time2name():
    current_path = os.path.dirname(os.path.dirname(__file__))
    tmp_path = os.path.join(current_path, "tmp")
    if not os.path.isdir(tmp_path):
        os.makedirs(tmp_path)

    current_time = str(time.time())
    current_time = current_time.split(".")
    part1 = int(current_time[0])
    time_array = time.localtime(part1)
    part1 = time.strftime("%Y%m%d_%H%M%S", time_array)
    part2 = int(current_time[1])
    image_name = "{}_{}.png".format(part1, part2)
    image_path = os.path.join(current_path, "tmp", image_name)
    return image_path

