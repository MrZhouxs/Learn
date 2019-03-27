# !/usr/bin/python3
# coding=utf-8
# @Time   : 2019/3/26/0026 17:00:14
# Author  : little star


class GUI(object):
    def __init__(self):
        pass

    def init_win(self, win, **kwargs):
        title = kwargs.get("title", None)
        # 设置窗口标题
        if title:
            win.title(title)
        # 设置窗口不可改变大小
        # win.resizable(False, False)

    @staticmethod
    def screen_w_h(win):
        """
        获取屏幕的尺寸大小
        :param win: 窗口对象
        :return:
        """
        screen_width = win.winfo_screenwidth()
        screen_height = win.winfo_screenheight()
        return screen_width, screen_height

    def set_centered(self, win, win_width, win_height):
        """
        设置窗口居中.
        :param win: 窗口对象
        :param win_width: 窗口宽度
        :param win_height: 窗口高度
        :return:
        """
        screen_width, screen_height = self.screen_w_h(win)
        x = int((screen_width - win_width) / 2)
        y = int((screen_height - win_height) / 2)
        win.geometry("{}x{}+{}+{}".format(win_width, win_height, x, y))
