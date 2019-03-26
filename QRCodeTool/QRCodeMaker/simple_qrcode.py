#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Func: 制作二维码
import qrcode
from PIL import Image

from FunTools.QRCodeTool.utils.image_name import time2name


class QRCodeMaker(object):
    def __init__(self):
        pass

    def maker(self, message):
        qr = qrcode.QRCode(
            version=5,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(message)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        image_path = time2name()
        img.save(image_path)
        try:
            _image = Image.open(image_path)
            _image.show()
            return True
        except Exception as ex:
            return str(ex)


if __name__ == '__main__':
    a = QRCodeMaker()
    a.maker('http://www.baidu.com/')
