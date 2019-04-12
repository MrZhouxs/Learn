# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time   : 2019/4/4/0004 16:13:33
# Author  : little star
# Func: 利用pytesseract识别二维码
import pytesseract

# 添加pytesseract相关变量参数
pytesseract.pytesseract.tesseract_cmd = 'D:/Softs/Tesseract-OCR/tesseract.exe'
tesseract_data_dir_config = '--tessdata-dir "D:/Softs/Tesseract-OCR/tessdata"'


def identification(image):
    """
    利用pytesseract识别二维码
    :param image: PIL.Image.Image
    :return:
    """
    # 识别图片中的数字和字母
    if tesseract_data_dir_config:
        text = pytesseract.image_to_string(image, config=tesseract_data_dir_config)
    else:
        text = pytesseract.image_to_string(image)
    # 去掉识别结果中的特殊字符
    exclude_char_list = ' .:\\|\'\"?![],()~@#$%^&*_+-={};<>/¥'
    text = ''.join([x for x in text if x not in exclude_char_list])
    return text
