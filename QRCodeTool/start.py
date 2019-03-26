#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Func: gui页面主入口
import ctypes
import tkinter

# from FunTools.QRCodeTool import ICO_PATH
from FunTools.QRCodeTool.gui import SIMPLE_BUTTON_TEXT, IMAGE_BUTTON_TEXT, WIN_TITLE
from FunTools.QRCodeTool.gui.image_button import ImageButton
from FunTools.QRCodeTool.gui.simple_button import SimpleButton

tk = tkinter.Tk()
tk.title(WIN_TITLE)


class GUI(object):
    def __init__(self):
        self.win_width = tk.winfo_screenwidth()
        self.win_height = tk.winfo_screenheight()

    def simple_button(self):
        SimpleButton(self.win_width, self.win_height).create_win()

    def image_button(self):
        ImageButton(self.win_width, self.win_height).create_win()

    def start(self):
        width = 300
        height = 200
        x = int((self.win_width - width) / 2)
        y = int((self.win_height - height) / 2)
        tk.geometry("{}x{}+{}+{}".format(width, height, x, y))
        tk.resizable(False, False)
        # 自定义左上角图标
        # tk.iconbitmap(ICO_PATH)
        button = tkinter.Button(tk, text=SIMPLE_BUTTON_TEXT, command=self.simple_button)
        button.pack(pady=50)
        button = tkinter.Button(tk, text=IMAGE_BUTTON_TEXT, command=self.image_button)
        button.pack()


if __name__ == '__main__':
    # 指定弹出窗口的AppUserModelID，是的任务栏图标有效
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("QRCodeMaker")
    gui = GUI()
    gui.start()
    tk.mainloop()
