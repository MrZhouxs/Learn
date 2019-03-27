# !/usr/bin/python3
# coding=utf-8
# @Time   : 2019/3/26/0026 16:59:06
# Author  : little star
# Func: 有道翻译
import ctypes
import tkinter
import pyttsx3
from FunTools.TranslationByYouDao.gui.welcome import Index


if __name__ == '__main__':
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Translation")
    engine = pyttsx3.init()
    rate = engine.getProperty('rate')
    engine.setProperty('rate', int(rate) - 60)
    root = tkinter.Tk()
    Index(engine).create_win(root)
    root.mainloop()
