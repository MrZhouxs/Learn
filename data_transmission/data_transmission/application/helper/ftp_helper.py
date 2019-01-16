#!/usr/bin/python3
# -*- coding: utf-8 -*-

import ftplib
import os
import time

from oslo_log import log

LOG = log.getLogger("log")


class FtpHelper(object):
    def __init__(self, host, user, password, port=21):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.ftp = None

    def login(self):
        flag = False
        while not flag:
            LOG.info(u"尝试连接ftp服务器")
            try:
                print(u"尝试连接ftp服务器")
                self.ftp = ftplib.FTP()
                self.ftp.connect(host=self.host, port=self.port, timeout=10)
                self.ftp.login(user=self.user, passwd=self.password)
                flag = True
                print(u"成功连接服务器")
            except:
                LOG.error(u"连接ftp服务器失败，5s后重新连接")
                time.sleep(5)

    def upload_file(self, file_name, file_path):
        pass

    def download_file(self, local_file, remote_file):
        self.login()
        while True:
            try:
                flag = self._download_file(local_file=local_file, remote_file=remote_file)
                break
            except Exception as ex:
                LOG.error(u"执行下载操作时，发生异常，异常原因：{}".format(str(ex)))
                time.sleep(5)
        if flag:
            LOG.info(u"文件下载成功")
        return flag

    def _download_file(self, local_file, remote_file):
        # 判断文件所在的路径是否存在，不存在，先创建
        local_file_dir = os.path.dirname(local_file)
        if not os.path.isdir(local_file_dir):
            os.makedirs(local_file_dir)
        # 先判断文件是否存在，存在的话，先删除，再下载
        if os.path.isfile(local_file):
            os.remove(local_file)
        file_handler = open(local_file, "wb")
        self.ftp.retrbinary("RETR {}".format(remote_file), file_handler.write, 1024)
        file_handler.close()
        LOG.info(u"{}文件下载成功".format(local_file))
        return True


if __name__ == '__main__':
    f = FtpHelper(host="192.168.0.88", user="admin", password="123456")
    local_file = "/opt/ftp/soft1547227952746.tar.gz"
    remote_file = "6xx/softupdate/file/2019/01/12/soft1547227952746.gz"
    f.download_file(local_file=local_file, remote_file=remote_file)
