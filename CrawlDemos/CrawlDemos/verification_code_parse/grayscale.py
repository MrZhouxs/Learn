# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time   : 2019/4/4/0004 15:43:04
# Author  : little star
# Func: 图片灰度处理、二值化处理

from collections import defaultdict
from PIL import Image

from CrawlDemos.verification_code_parse.tesseract_identify import identification


def get_threshold(image):
    # 获取图片中像素点数量最多的像素
    pixel_dict = defaultdict(int)
    # 像素及该像素出现次数的字典
    rows, cols = image.size
    for i in range(rows):
        for j in range(cols):
            pixel = image.getpixel((i, j))
            pixel_dict[pixel] += 1
    # 获取像素出现出多的次数
    count_max = max(pixel_dict.values())
    pixel_dict_reverse = {v: k for k, v in pixel_dict.items()}
    # 获取出现次数最多的像素点
    threshold = pixel_dict_reverse[count_max]
    return threshold


def get_bin_table(threshold):
    # 按照阈值进行二值化处理
    # threshold: 像素阈值
    # 获取灰度转二值的映射table
    table = []
    for i in range(256):
        # 在threshold的适当范围内进行处理
        rate = 0.1
        if threshold * (1 - rate) <= i <= threshold * ( 1 + rate):
            table.append(1)
        else:
            table.append(0)
    return table


# 去掉二值化处理后的图片中的噪声点
def cut_noise(image):
    # 图片的宽度和高度
    rows, cols = image.size
    # 记录噪声点位置
    change_pos = []

    # 遍历图片中的每个点，除掉边缘
    for i in range(1, rows-1):
        for j in range(1, cols-1):
            # pixel_set用来记录该店附近的黑色像素的数量
            pixel_set = []
            # 取该点的邻域为以该点为中心的九宫格
            for m in range(i - 1, i + 2):
                for n in range(j - 1, j + 2):
                    # 1为白色,0位黑色
                    if image.getpixel((m, n)) != 1:
                        pixel_set.append(image.getpixel((m, n)))
            # 如果该位置的九宫内的黑色数量小于等于4，则判断为噪声
            if len(pixel_set) <= 4:
                change_pos.append((i, j))
    # 对相应位置进行像素修改，将噪声处的像素置为1（白色）
    for pos in change_pos:
        image.putpixel(pos, 1)
    # 返回修改后的图片
    return image


# 识别图片中的数字加字母
# 传入参数为图片路径，返回结果为：识别结果
def image_parse(image_path):
    # 打开图片文件
    image = Image.open(image_path)
    # 转化为灰度图
    image2grey = image.convert('L')
    # 获取图片中的出现次数最多的像素，即为该图片的背景
    max_pixel = get_threshold(image2grey)
    # 将图片进行二值化处理
    table = get_bin_table(threshold=max_pixel)
    out = image2grey.point(table, '1')
    # 去掉图片中的噪声（孤立点）
    out = cut_noise(out)
    # 显示图片
    out.show()
    # 显示图片
    return out


if __name__ == '__main__':
    img_path = "D:\Demos\pythonWorkSpace\CrawlDemos\CrawlDemos\\verification_code_parse\images\\1.jpg"
    img_path2 = "D:\Demos\pythonWorkSpace\CrawlDemos\CrawlDemos\\verification_code_parse\images\\2.png"
    a = image_parse(img_path2)
    print(identification(a))
