# !/usr/bin/python3
# coding=utf-8
# @Time   : 2019/3/26/0026 17:00:27
# Author  : little star
import tkinter
from tkinter.scrolledtext import ScrolledText
from FunTools.TranslationByYouDao.gui import GUI
from FunTools.TranslationByYouDao.translation.youdao import Translation


class Index(GUI):
    def __init__(self, engine):
        super(Index, self).__init__()
        self.left_scrolled_text = None
        self.right_scrolled_text = None
        self.trans = Translation()
        self.menu = None
        self.text = None
        self.engine = engine

    def create_win(self, win):
        self.init_win(win, title="Google翻译")
        self.set_centered(win, 780, 380)
        self.left_label(win)
        self.right_label(win)

    def left_label(self, win):
        """
        带翻译的窗口
        :param win: 窗口
        :return:
        """
        label = tkinter.Label(win)
        label.grid(row=0, column=0, sticky="W", padx=5, pady=5)
        prompt_label = tkinter.Label(label, text="请输入你要翻译的文字")
        prompt_label.grid(row=0)

        text = ScrolledText(label, height=25, background="white", width=50, wrap=tkinter.WORD)
        self.left_scrolled_text = text
        text.grid(row=1)
        # 绑定键盘事件
        text.bind('<KeyRelease>', self.text_separator)

    def right_label(self, win):
        """
        显示翻译的窗口
        :param win: 窗口
        :return:
        """
        label = tkinter.Label(win)
        label.grid(row=0, column=1, sticky="E", padx=5, pady=5)
        prompt_label = tkinter.Label(label, text="文字")
        prompt_label.grid(row=0)
        text = ScrolledText(label, height=25, background="white", width=50)
        self.right_scrolled_text = text
        text.grid(row=1)
        self.add_command()

    def text_separator(self, event):
        content = self.left_scrolled_text.get(0.0, tkinter.END)
        content = content.replace("\n", "")
        if content:
            self.text = "输入的内容不能被翻译"
            try:
                self.text = self.trans.translate(content)
            except:
                pass
            self.insert_trans(self.text)

    def insert_trans(self, trans):
        # 先清空内容，再写入数据
        self.right_scrolled_text.delete(0.0, tkinter.END)
        self.right_scrolled_text.insert(0.0, trans)

    def add_command(self):
        """
        给显示翻译的窗口添加 右键菜单功能
        :return:
        """
        self.menu = tkinter.Menu(self.right_scrolled_text, tearoff=0)
        self.menu.add_command(label="语音", command=self.right_func)
        self.menu.add_separator()
        self.right_scrolled_text.bind("<Button-3>", self.popup_menu)

    def popup_menu(self, event):
        self.menu.post(event.x_root, event.y_root)

    def right_func(self):
        """
        右键功能函数
        :return:
        """
        if self.text:
            self.engine.say(self.text)
            # 这步才会发出声音
            self.engine.runAndWait()
