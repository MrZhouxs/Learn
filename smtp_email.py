# !/usr/bin/python3
# coding=utf-8
# @Time   : 2019/2/27/0027 16:40:46
# Author  : little star
# Func: python发送邮件

import smtplib
from email.mime.text import MIMEText
from email.header import Header

# 第三方 SMTP 服务
MAIL_HOST = "smtp.163.com"  # 设置服务器
MAIL_USER = "mrzhouxs"    # 用户名
MAIL_PASS = "zhouxs997464"   # 口令
SENDER = "Mrzhouxs@163.com"

txt = """《双子星点》系列的开发商LGM Games今日公布了新作《双子星点3》，这是一款开放世界、单人动作角色扮演游戏，玩家扮演一个太空冒险家穿越浩瀚的宇宙，官方也发布了最新预告。

　　据介绍新作还将是主打太空战舰在游戏进程中的升级强化。但在内容和细节等方面已经做出了很多强化。在游戏的Steam页面我们可以看到，官方表示：

　　新作的地图将不仅有双子星座，还将有两个全新的星系。

　　新增了可脱离船只的无人机，操控它探索各种宇宙建筑;

　　飞船的操作和战斗视角全面升级;

　　舰船不同模块升级改造系统，升级改造后舰船造型也会相应改变;

　　在支持语言方面，也可以看到新作将支持简体中文。目前游戏的PC配置要求和具体的发售日期还未公布。
"""


class SendEmail(object):
    def __init__(self, mail_port=25):
        self.mail_port = mail_port
        self.email_obj = self.login()

    def login(self):
        try:
            email_obj = smtplib.SMTP()
            email_obj.connect(MAIL_HOST, self.mail_port)    # 25 为 SMTP 端口号
            email_obj.login(MAIL_USER, MAIL_PASS)
            return email_obj
        except Exception as ex:
            print(str(ex))
            return None

    def send_email(self, receivers, content, subject=str()):
        """
        发送纯文本格式的email
        :param receivers:
        :param content:
        :param subject:
        :return:
        """
        if not isinstance(receivers, list):
            receivers = [receivers]
        for receiver in receivers:
            try:
                message = MIMEText(content, 'plain', 'utf-8')
                message['From'] = SENDER
                message['To'] = receiver
                message['Subject'] = Header(subject, 'utf-8')
                self.email_obj.sendmail(SENDER, [receiver], message.as_string())
            except Exception as ex:
                print(ex)
                print("send email to {} fail".format(receiver))


if __name__ == '__main__':
    a = SendEmail()
    a.send_email(["863913681@qq.com"], txt)
