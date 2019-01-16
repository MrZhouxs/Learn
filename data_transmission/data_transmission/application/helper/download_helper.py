#!/usr/bin/python3
# -*- coding: utf-8 -*-
import requests
import os
import time
from oslo_log import log


LOG_WARNING = log.getLogger()


class DownloadPackage(object):
    def __init__(self):
        self.download_count = 3

    def download_update_file(self, update_params, package_save_path, file_type="tar.gz"):
        url = update_params.get("path")
        server_name = update_params.get("server_name")
        version = update_params.get("version")
        # 判断package_save_path的路径是否存在，不存在则创建
        if not os.path.isdir(package_save_path):
            os.makedirs(package_save_path)
        count = 1
        while count <= self.download_count:
            try:
                response = requests.get(url=url, verify=False)
                headers = response.headers.get("Content-Disposition")
                response_file_type = headers.split(";")[1]
                if response_file_type.endswith(".tar.gz") or response_file_type.endswith(".gz"):
                    file_type = "tar.gz"
                elif response_file_type.endswith(".zip"):
                    file_type = "zip"
                elif response_file_type.endswith(".war"):
                    file_type = "war"
                temp_tar_file_path = os.path.join(package_save_path, "{}-{}.{}".format(server_name, version, file_type))
                # 判断要升级的压缩包本地是否已经存在
                if os.path.isfile(temp_tar_file_path):
                    os.remove(temp_tar_file_path)
                with open(temp_tar_file_path, 'wb') as write_file:
                    write_file.write(response.content)
                return True
            except Exception as ex:
                LOG_WARNING.error(u"第{}次下载更新包出错，错误原因为:{}".format(count, str(ex)))
                count += 1
                time.sleep(0.01)

        LOG_WARNING.info(u"尝试{}次下载失败，不再进行尝试下载".format(count - 1))
        return False
