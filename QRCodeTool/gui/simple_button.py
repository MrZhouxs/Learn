#!/usr/bin/python3
# -*- coding: utf-8 -*-
import tkinter
from tkinter import messagebox

# from FunTools.QRCodeTool import ICO_PATH
from FunTools.QRCodeTool.QRCodeMaker.simple_qrcode import QRCodeMaker
from FunTools.QRCodeTool.gui import INFO_MESSAGE, SIMPLE_BUTTON_TEXT


class SimpleButton(object):
    def __init__(self, win_width, win_height):
        self.button_tk = tkinter.Tk()
        self.button_tk.title(SIMPLE_BUTTON_TEXT)
        self.win_width = win_width
        self.win_height = win_height
        self.init_win()
        self.text = None
        self.qr_maker = QRCodeMaker()

    def init_win(self):
        width = 570
        height = 275
        x = int((self.win_width - width) / 2)
        y = int((self.win_height - height) / 2)
        self.button_tk.geometry("{}x{}+{}+{}".format(width, height, x, y))
        self.button_tk.resizable(False, False)
        # self.button_tk.iconbitmap(ICO_PATH)

    def create_win(self):
        label = tkinter.Label(self.button_tk, text="输入二维码的内容：")
        label.grid(row=0, sticky="W", padx=5, pady=5)

        self.text = tkinter.Text(self.button_tk, height=15)
        self.text.grid(row=1)

        confirm_button = tkinter.Button(self.button_tk, text="生成", command=self.confirm_button)
        confirm_button.grid(row=2, sticky="E", padx=5, pady=5)

    def confirm_button(self):
        content = self.text.get(0.0, tkinter.END)
        content = content.replace("\n", "")
        if content:
            flag = self.qr_maker.maker(content)
            if flag is not True:
                tkinter.messagebox.showerror("错误", flag)
        else:
            tkinter.messagebox.showinfo('提示', INFO_MESSAGE)
