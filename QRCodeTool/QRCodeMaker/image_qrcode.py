# !/usr/bin/python3
# coding=utf-8
# @Time   : 2019/3/25/0025 15:45:04
# Author  : little star
import qrcode
from PIL import Image

from FunTools.QRCodeTool.utils.image_name import time2name


class ImageQRCode(object):
    def __init__(self):
        pass

    def maker(self, message, image_path):
        qr = qrcode.QRCode(
            version=5,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4
        )
        qr.add_data(message)
        qr.make(fit=True)

        img = qr.make_image()
        img = img.convert("RGBA")

        icon = Image.open(image_path)

        img_w, img_h = img.size
        factor = 4
        size_w = int(img_w / factor)
        size_h = int(img_h / factor)

        icon_w, icon_h = icon.size
        if icon_w > size_w:
            icon_w = size_w
        if icon_h > size_h:
            icon_h = size_h
        icon = icon.resize((icon_w, icon_h), Image.ANTIALIAS)

        w = int((img_w - icon_w) / 2)
        h = int((img_h - icon_h) / 2)
        img.paste(icon, (w, h))
        image_path = time2name()
        img.save(image_path)
        try:
            _image = Image.open(image_path)
            _image.show()
            return True
        except Exception as ex:
            return str(ex)
