# !/usr/bin/python3
# coding=utf-8
# @Time   : 2019/3/25/0025 13:34:24
# Author  : little star

import tkinter
import os

# from FunTools.QRCodeTool import ICO_PATH
from tkinter import messagebox, filedialog
from FunTools.QRCodeTool.QRCodeMaker.image_qrcode import ImageQRCode
from FunTools.QRCodeTool.gui import INFO_MESSAGE, IMAGE_BUTTON_TEXT


class ImageButton(object):
    def __init__(self, win_width, win_height):
        self.button_tk = tkinter.Tk()
        self.button_tk.title(IMAGE_BUTTON_TEXT)
        self.win_width = win_width
        self.win_height = win_height
        self.init_win()
        self.text = None
        self.entry = None
        self.qr_maker = ImageQRCode()

    def init_win(self):
        width = 570
        height = 312
        x = int((self.win_width - width) / 2)
        y = int((self.win_height - height) / 2)
        self.button_tk.geometry("{}x{}+{}+{}".format(width, height, x, y))
        self.button_tk.resizable(False, False)
        # 窗口保持最上面
        # self.button_tk.attributes("-topmost", True)
        # self.button_tk.iconbitmap(ICO_PATH)

    def create_win(self):
        label = tkinter.Label(self.button_tk, text="输入二维码的内容：")
        label.grid(row=0, sticky="W", padx=5, pady=5)

        self.text = tkinter.Text(self.button_tk, height=15, background="white")
        self.text.grid(row=1)

        label2 = tkinter.Button(self.button_tk, text="选择图片", width=15,
                                command=self.select_image_button)
        label2.grid(row=2, sticky="E", padx=5, pady=5)
        self.entry = tkinter.Entry(self.button_tk, width=50)
        self.entry.grid(row=2, sticky="W", padx=5, pady=5)

        confirm_button = tkinter.Button(self.button_tk, text="生成", command=self.confirm_button)
        confirm_button.grid(row=3, sticky="E", padx=5, pady=5)

    def confirm_button(self):
        image_path = self.entry.get()
        if not os.path.isfile(image_path):
            tkinter.messagebox.showerror(title="提示", message="请选择图片")
            return
        content = self.text.get(0.0, tkinter.END)
        content = content.replace("\n", "")
        if content:
            flag = self.qr_maker.maker(content, image_path)
            if flag is not True:
                tkinter.messagebox.showerror("错误", flag)
        else:
            tkinter.messagebox.showinfo('提示', INFO_MESSAGE)

    def select_image_button(self):
        file_path = tkinter.filedialog.askopenfilename(title="选择图片")
        if os.path.isfile(file_path):
            if self.entry.get() is not None:
                self.entry.delete(0, tkinter.END)
            self.entry.insert(0, file_path)
        else:
            tkinter.messagebox.showerror(title="提示", message="请选择图片")
