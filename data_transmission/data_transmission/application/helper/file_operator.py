#!/usr/bin/python3
# -*- coding: utf-8 -*-
import base64
import json
import os

from oslo_log import log


LOG_WARNING = log.getLogger()


class FileOperator(object):

    @staticmethod
    def save_file(data, file_name, file_path):
        """
        将数据写进文件中，写入的方式为追加的方式.
        :param data: 要写入文件的数据.
        :param file_name: 文件名称.
        :param file_path: 文件路径.
        :return: 保存成功返回True，否则返回False.
        """
        try:
            if not os.path.isdir(file_path):
                os.makedirs(file_path)
            temp_file_path = os.path.join(file_path, file_name)
            if os.path.isfile(temp_file_path):
                os.remove(temp_file_path)
            if not isinstance(data, str):
                data = json.dumps(data)
            with open(temp_file_path, "a+") as obj:
                obj.write(data)
            return True
        except Exception as ex:
            LOG_WARNING.error(u"文件写入有误，错误原因为：{}".format(str(ex)))
        return False

    @staticmethod
    def save_file_bytes(data, file_name, file_path):
        """
        将数据写进文件中，写入的方式为追加的方式.
        :param data: 要写入文件的数据.
        :param file_name: 文件名称.
        :param file_path: 文件路径.
        :return: 保存成功返回True，否则返回False.
        """
        try:
            if not os.path.isdir(file_path):
                os.makedirs(file_path)
            temp_file_path = os.path.join(file_path, file_name)
            data = base64.b64decode(data)
            with open(temp_file_path, "ab+") as obj:
                obj.write(data)
            return True
        except Exception as ex:
            LOG_WARNING.error(u"文件写入有误，错误原因为：{}".format(str(ex)))
        return False

    def read_file(self, file_name, file_path, limit_size=None):
        """
        读取文件内容.
        limit_size如果有值的情况下，每次读取文件的内容大小不能超过这个值，如果超过的话，需要将文件拆分出来.
                  拆分的文件每个大小最大为1M，如果limit_size没有1M大小，以1M为基准.
        limit_size没有值的情况下，则一次性将文件内容读取.
        :param file_name: 文件名.
        :param file_path: 文件路径.
        :param limit_size: 每个文件最大值.
        :return: 文件内容.
        """
        # 一次读取文件的大小
        single_read_size = 1024
        # 拆分的单个文件的大小
        single_file_size = 1024 * 1024
        # 默认以二进制的方式读取所有文件
        read_mode = "r"
        try:
            result = ""
            if not os.path.isdir(file_path):
                os.makedirs(file_path)
            file_full_path = os.path.join(file_path, file_name)
            # 判断读取文件内容是否需要拆分成小文件
            if limit_size is None:
                obj = open(file_full_path, read_mode)
                # 每次读取1024个bytes
                while True:
                    content = obj.read(single_read_size)
                    if not content:
                        break
                    result += content
            else:
                result = list()
                limit_size = self.calculate_digits(limit_size)
                # 判断limit_size的大小是否大于1M，如果小于，则将limit_size置为1M
                if limit_size < single_file_size:
                    limit_size = single_file_size
                obj = open(file_full_path, read_mode)
                single_file_content = ""
                while True:
                    content = obj.read(single_read_size)
                    if content:
                        seek = obj.tell()
                        single_file_content += content
                        # 当读取的文件内容等于limit_size时，保存文件内容，并清空缓存
                        if (seek % limit_size) == 0:
                            result.append(single_file_content)
                            single_file_content = ""
                    else:
                        obj.close()
                        break
                # 加上剩余的部分
                if single_file_content:
                    result.append(single_file_content)
        except Exception as ex:
            LOG_WARNING.error(u"读取文件内容是出错，错误原因为：{}".format(str(ex)))
            return None
        return result

    def read_file_by_bytes(self, file_name, file_path, limit_size=None):
        """
        读取文件内容.
        limit_size如果有值的情况下，每次读取文件的内容大小不能超过这个值，如果超过的话，需要将文件拆分出来.
                  拆分的文件每个大小最大为1M，如果limit_size没有1M大小，以1M为基准.
        limit_size没有值的情况下，则一次性将文件内容读取.
        :param file_name: 文件名.
        :param file_path: 文件路径.
        :param limit_size: 每个文件最大值.
        :return: 文件内容.
        """
        # 一次读取文件的大小
        single_read_size = 1024
        # 拆分的单个文件的大小
        single_file_size = 1024 * 1024
        # 默认以二进制的方式读取所有文件
        read_mode = "rb"
        try:
            result = ""
            if not os.path.isdir(file_path):
                os.makedirs(file_path)
            file_full_path = os.path.join(file_path, file_name)
            # 判断读取文件内容是否需要拆分成小文件
            if limit_size is None:
                obj = open(file_full_path, read_mode)
                # 每次读取1024个bytes，将bytes数据转换成str
                bytes_content = obj.read()
                base64_bytes = base64.b64encode(bytes_content)
                base64_string = base64_bytes.decode("utf8")
                result += base64_string
            else:
                result = list()
                limit_size = self.calculate_digits(limit_size)
                # 判断limit_size的大小是否大于1M，如果小于，则将limit_size置为1M
                if limit_size < single_file_size:
                    limit_size = single_file_size
                obj = open(file_full_path, read_mode)
                single_file_content = ""
                while True:
                    temp_file_content = obj.read(single_read_size)
                    base64_bytes = base64.b64encode(temp_file_content)
                    base64_string = base64_bytes.decode("utf8")
                    if base64_string:
                        seek = obj.tell()
                        single_file_content += base64_string
                        # 当读取的文件内容等于limit_size时，保存文件内容，并清空缓存
                        if (seek % limit_size) == 0:
                            result.append(single_file_content)
                            single_file_content = ""
                    else:
                        obj.close()
                        break
                # 加上剩余的部分
                if single_file_content:
                    result.append(single_file_content)
        except Exception as ex:
            LOG_WARNING.error(u"读取文件内容是出错，错误原因为：{}".format(str(ex)))
            return None
        return result

    def unite_file_content(self, file_content_list, file_name, file_path):
        """
        合并文件内容并保存在本地.
        :param file_content_list: 待合并的文件内容.
        :param str file_name: 待保存为的文件名称.
        :param str file_path: 待保存的文件历经.
        :return:
        """
        try:
            if file_content_list:
                temp_file_path_name = "tmp_split_file"
                temp_dir_file_path = os.path.dirname(file_path)
                temp_file_name = file_name.split(".")[0]
                split_file_path = os.path.join(temp_dir_file_path, temp_file_path_name, temp_file_name)
                for index, each_content in enumerate(file_content_list):
                    # 将拆分的文件内容个并成一个文件
                    self.save_file(data=each_content, file_name=file_name, file_path=file_path)
                    # 将拆分出的文件内容保存在临时目录下
                    self.save_file(data=each_content, file_name="{}-{}.txt".format(temp_file_name, index + 1),
                                   file_path=split_file_path)
            return True
        except Exception as ex:
            LOG_WARNING.error(u"合并文件内容时出错，错误原因为：{}".format(str(ex)))
        return False

    @staticmethod
    def file_size(file_name, file_path):
        """
        获取文件大小.
        :param file_name: 文件名.
        :param file_path: 文件路径.
        :return: 文件大小.
        """
        file_full_path = os.path.join(file_path, file_name)
        if not os.path.isfile(file_full_path):
            return None
        try:
            size = os.path.getsize(file_full_path)
            return size
        except Exception as ex:
            LOG_WARNING.error(u"获取文件大小出错，错误原因为：{}".format(str(ex)))
        return None

    @staticmethod
    def calculate_digits(digits):
        """
        换算字节大小.
        例： 1KB -> 1024 bytes; 1MB -> 1024*1024 bytes; 1GB -> 1024*1024*1024 bytes.
        :param digits: 需要换算的字节.
        :return int: 以bytes为单位的大小.
        """
        temp_digits = digits[: len(digits) - 1]
        temp_digits = int(temp_digits)
        if "K" in digits or "k" in digits:
            result = temp_digits * 1024
        elif "M" in digits or "m" in digits:
            result = temp_digits * 1024 * 1024
        elif "G" in digits or "g" in digits:
            result = temp_digits * 1024 * 1024 * 1024
        else:
            result = temp_digits
        return result
