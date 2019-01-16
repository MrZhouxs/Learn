# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import platform
import subprocess
import re
import tarfile
import zipfile
import multiprocessing
import requests
import time
import urllib
from oslo_log import log
from urllib import parse

from ..zk_help import ZkHelp
from ..server_manager import TaskManage,ProcessManage
from ..common.commfunc import get_id
from ..out_puter import init_logstash_sender, logstash_sender
from ..common.timeutils import STANDARD_TIME_FORMAT
LOG = log.getLogger("log")
VERSION_FLAG = None

class ZookeeperHelper(object):
    def __init__(self, zookeeper):
        self.zookeeper = zookeeper
        self.zk_helper = ZkHelp(hosts=zookeeper)
        self.zk_helper.start()

    def clear_node(self, node_path):
        try:
            # LOG.info(u"开始删除原服务zookeeper节点")
            send_message_to_logstash(u"开始删除原服务zookeeper节点",1)
            self.zk_helper.remove_node(path=node_path)
            # LOG.info(u"删除原服务zookeeper节点成功")
            send_message_to_logstash(u"删除原服务zookeeper节点成功", 1)
        except Exception as ex:
            # LOG.info(u"delete zookeeper node fail, the failure reason is:{}".format(str(ex)))
            send_message_to_logstash(u"delete zookeeper node fail, the failure reason is:{}".format(str(ex)), -1)
        finally:
            self.zk_helper.stop_zk()

class UpdateSelf(object):
    def __init__(self, env_args, update_args, handlers,download_count=3):
        self.download_count = download_count
        self.package_path, self.env_path,  self.zookeeper = env_args
        self.main_process_pid = os.getpid()
        self.server_name = update_args.get("server_name")
        self.new_version = update_args.get("version")
        self.update_file_url = update_args.get("path")
        self.handlers = handlers
        init_logstash_sender(handlers, self.server_name)

    @classmethod
    def stop_server(cls, server_name):
        iret = False
        cmd = 'supervisorctl stop {}'.format(server_name)
        # LOG.info("exec cmd:{}".format(cmd))
        send_message_to_logstash(cmd,1)
        stdout = os.popen(cmd)
        result = stdout.read()
        if result:
            if re.search(':\s*?stopped', result) or re.search('not\s*?running', result):
                iret = True
        return iret

    @classmethod
    def start_server(cls, server_name):
        iret = False
        cmd = 'supervisorctl start {}'.format(server_name)
        # LOG.info("exec cmd:{}".format(cmd))
        send_message_to_logstash(cmd,1)
        stdout = os.popen(cmd)
        result = stdout.read()
        if result:
            if re.search(':\s*?started', result):
                iret = True
        return iret

    @property
    def platform(self):
        """
        获取当前操作系统.
        :return:
        """
        operate_system = platform.system().lower()
        return operate_system

    def execute_command(self, command, pattern=None):
        """
        执行脚本命令.
        :param command: 脚本命令.
        :param pattern: 正则表达式.
        :return:
        """
        try:
            # LOG.info("the execute command is:{}".format(command))
            send_message_to_logstash(command,1)
            stdout = os.popen(command)
            result = stdout.read()
            if self.platform == "linux":
                os.wait()
            if pattern:
                if re.search(pattern=pattern, string=result):
                    return True
                else:
                    return False
            return True
        except Exception as ex:
            # LOG.info(u"执行命令出错，错误原因:{}".format(str(ex)))
            send_message_to_logstash(ex,-1)
        return False

    def check_version(self, server_name):
        """

        :param server_name: 服务名称
        :return: 服务版本
        """
        server_version = None
        system = platform.system().lower()
        if system == 'linux':
            server_name = server_name.replace('_', '-')
            cmd = "%s/pip list | grep %s |awk '{print $2}'" % (self.env_path, server_name)
            # LOG.info("linux cmd:{}".format(cmd))
            send_message_to_logstash(cmd, 1)
            stdout = os.popen(cmd)
            server_version = stdout.read().strip("\n")
            info = re.search('[\(]*(.*?)[\)]', server_version)
            if info:
                server_version = info.group(1)
                server_version = server_version.strip('\n')
        elif system == 'windows':
            cmd = '{}/pip list | findstr {}'.format(self.env_path, server_name)
            # LOG.info("windows cmd:{}".format(cmd))
            send_message_to_logstash(cmd, 1)
            stdout = os.popen(cmd)
            result = stdout.read()
            if result:
                name_version_list = result.split()
                if len(name_version_list) > 1:
                    server_version = name_version_list[1]
                    server_version = server_version.strip('\n')
        else:
            # LOG.info(u"暂不支持其它操作系统")
            send_message_to_logstash(u"暂不支持其它操作系统", 1)
        return server_version

    def download_update_file(self, url, server_name, version, file_type="tar.gz"):
        if file_type == "tar.gz":
            temp_tar_file_path = os.path.join(self.package_path, "{}-{}.tar.gz".format(server_name, version))
        else:
            temp_tar_file_path = os.path.join(self.package_path, "{}-{}.zip".format(server_name, version))
        temp_file_path = os.path.join(self.package_path, "{}-{}".format(server_name, version))
        if os.path.isfile(temp_file_path):
            return True
        elif os.path.isfile(temp_tar_file_path):
            return True
        count = 1
        while count <= self.download_count:
            try:
                response = requests.get(url=url, verify=False)
                update_file_path = os.path.join(self.package_path, temp_tar_file_path)
                with open(update_file_path, 'wb') as write_file:
                    write_file.write(response.content)
                requests_size = int(response.headers['Content-Length'])
                local_size =int(os.path.getsize(update_file_path))
                if local_size<requests_size:
                    raise Exception("下载文件不全,源文件大小{}，下载大小{}".format(str(requests_size),str(local_size)))
                return True
            except Exception as ex:
                # LOG.info(u"第{}次下载更新包出错，错误原因为:{}".format(count, str(ex)))
                send_message_to_logstash(u"第{}次下载更新包出错，错误原因为:{}".format(count, str(ex)), -1)
                count += 1
                time.sleep(0.01)
        # LOG.info(u"尝试{}次下载失败，不再进行尝试下载".format(count - 1))
        send_message_to_logstash(u"尝试{}次下载失败，不再进行尝试下载".format(count, str(ex)), 0)
        return False

    def back_flag(self):
        # 本地添加文件标记当前是否是回退了老版本
        current_path = os.path.dirname(os.path.dirname(__file__))
        file_path = os.path.join(current_path, "back_version_flag")
        flag = {"update_version": self.new_version, "back_flag": 1}
        json_string = json.dumps(flag)
        with open(file_path, "w") as write_obj:
            write_obj.write(json_string)

    def back_version(self, server_name, run_version, update_url):
        # 先卸载当前已安装的版本（不论现在安装是新版本还是旧版本）
        # 重新安装旧版本的代码并重启服务
        download_file_url = self.parse_url(url=update_url, version=run_version)
        if not self.download_update_file(url=download_file_url, server_name=server_name, version=run_version):
            # LOG.info(u"回退版本时，下载旧版本的更新包出错,不进行本次回退操作")
            send_message_to_logstash(u"回退版本时，下载旧版本的更新包出错,不进行本次回退操作",0)
            return False
        if run_version:
            self.back_flag()
            if self.uninstall_server(server_name=server_name):
                # LOG.info(u"卸载当前{}服务成功".format(server_name))
                send_message_to_logstash(u"卸载当前{}服务成功".format(server_name),1)
            else:
                # LOG.info(u"卸载当前{}服务失败".format(server_name))
                send_message_to_logstash(u"卸载当前{}服务失败".format(server_name),0)
            # LOG.info(u"开始安装旧版本{}服务".format(server_name))
            send_message_to_logstash(u"开始安装旧版本{}服务".format(server_name),1)
            result = self.install_server(server_name, run_version)
            if result:
                # LOG.info("{}-{}安装成功, 版本回退成功".format(server_name, run_version))
                send_message_to_logstash("{}-{}安装成功, 版本回退成功".format(server_name, run_version),1)
                return True
            else:
                # LOG.info('{}-{}安装失败, 版本回退失败'.format(server_name, run_version))
                send_message_to_logstash('{}-{}安装失败, 版本回退失败'.format(server_name, run_version),0)
        else:
            # LOG.info('没有安装{}服务,不进行版本回退'.format(server_name))
            send_message_to_logstash('没有安装{}服务,不进行版本回退'.format(server_name),1)
        return False

    @staticmethod
    def parse_url(url, version):
        url_split = url.split("?")
        res = urllib.parse.parse_qs(url_split[1])
        res["version"] = version
        res_url = url_split[0] + "?"
        for key, val in res.items():
            res_url += str(key) + "="
            if isinstance(val, list):
                for each in val:
                    res_url += str(each)
            else:
                res_url += str(val)
            res_url += "&"
        res_url = res_url[: len(res_url) - 1]
        return res_url

    @staticmethod
    def un_zip(zip_path, target_path=None):
        """
        解压zip包.
        :param zip_path: zip包文件路径.
        :param target_path: 解压出的文件存放路径.
        :return:
        """
        if os.path.isfile(zip_path):
            if not target_path:
                target_path = os.path.dirname(zip_path)
            try:
                zip_obj = zipfile.ZipFile(zip_path, 'r')
                zip_obj.extractall(path=target_path)
                zip_obj.close()
                return True
            except Exception as ex:
                # LOG.info(u"解压zip文件时出错，错误原因为:{}".format(str(ex)))
                send_message_to_logstash(u"解压zip文件时出错，错误原因为:{}".format(str(ex)),-1)
        else:
            # LOG.info(u"给出的zip文件不存在，文件路径为:{}".format(zip_path))
            send_message_to_logstash(u"给出的zip文件不存在，文件路径为:{}".format(zip_path),0)
        return False

    @staticmethod
    def un_tar(tar_path, target_path=None):
        """
        解压tar包.
        :param tar_path: tar包文件路径.
        :param target_path: 解压出的文件存放路径.
        :return: 解压成功返回True，否则返回False.
        """
        if os.path.isfile(tar_path):
            if not target_path:
                target_path = os.path.dirname(tar_path)
            try:
                tar_obj = tarfile.open(tar_path, "r:gz")
                tar_obj.extractall(path=target_path)
                tar_obj.close()
                return True
            except Exception as ex:
                # LOG.info(u"解压tar文件时出错，错误原因为:{}".format(str(ex)))
                send_message_to_logstash(u"解压tar文件时出错，错误原因为:{}".format(str(ex)),-1)
        else:
            #LOG.info(u"给出的tar文件不存在，文件路径为:{}".format(tar_path))
            send_message_to_logstash(u"给出的tar文件不存在，文件路径为:{}".format(tar_path),0)
        return False

    def decompress_helper(self, server_name, version):
        # 先检查要解压的压缩包有没对应的文件夹存在，存在则不解压
        server_file_path = "{}/{}-{}".format(self.package_path, server_name, version)
        decompress_flag = False
        if os.path.isfile(server_file_path):
            decompress_flag = True
        else:
            decompress_tar_path = server_file_path + '.tar.gz'
            decompress_zip_path = server_file_path + '.zip'
            # 要么需要解压的是tar.gz包，要么是zip包
            if os.path.isfile(decompress_tar_path):
                decompress_flag = self.un_tar(tar_path=decompress_tar_path)
            elif os.path.isfile(decompress_zip_path):
                decompress_flag = self.un_zip(zip_path=decompress_zip_path)
            else:
                # LOG.info(u"待解压的压缩包不存在，压缩包的名称为:{}".format(server_file_path))
                send_message_to_logstash(u"待解压的压缩包不存在，压缩包的名称为:{}".format(server_file_path),0)
        return decompress_flag

    def install_server(self, server_name, version):
        server_file_path = "{}/{}-{}".format(self.package_path, server_name, version)
        server_setup_file = '{}/setup.py'.format(server_file_path)
        if not os.path.exists(server_setup_file):
            # LOG.info('找不到安装文件:{}'.format(server_setup_file))
            send_message_to_logstash('找不到安装文件:{}'.format(server_setup_file),0)
            return False
        os.chdir(server_file_path)
        # LOG.info(u"当前工作路径:{}".format(os.getcwd()))
        send_message_to_logstash("当前工作路径:{}".format(os.getcwd()), 1)
        cmd = '{}/python {} install'.format(self.env_path, server_setup_file)
        # LOG.info(u"执行安装命令:{}".format(cmd))
        send_message_to_logstash(u"执行安装命令:{}".format(cmd),1)
        stdout = os.popen(cmd)
        result = stdout.read()
        if re.search('\s*?[Ee]rror\s', result):
            return False
        # LOG.info('install {}-{} success!'.format(server_name, version))
        send_message_to_logstash('install {}-{} success!'.format(server_name, version), 1)
        return True

    def uninstall_server(self, server_name):
        cmd = '{}/pip uninstall {} -y'.format(self.env_path, server_name)
        #LOG.info("execute uninstall {} command:{}".format(server_name, cmd))
        send_message_to_logstash("execute uninstall {} command:{}".format(server_name, cmd),1)
        stdout = os.popen(cmd)
        result = stdout.read()
        if re.search('Successfully\s*?uninstalled\s*?{}'.format(server_name), result):
            # LOG.info('uninstall {} success!'.format(server_name))
            send_message_to_logstash('uninstall {} success!'.format(server_name),1)
            return True
        if re.search(':\s*?[Ee]rror\s', result):
            # LOG.info('uninstall {} error!'.format(server_name))
            send_message_to_logstash('uninstall {} error!'.format(server_name),0)
            return False

    def update_server(self, server_name, new_version, run_version, file_url):
        if run_version == new_version:
            #LOG.info('待更新版本与运行版本一致，不更新')
            send_message_to_logstash('待更新版本与运行版本一致，不更新',1)
            return False
        if file_url:
            if not self.download_update_file(file_url, server_name, new_version):
                # LOG.info("更新包下载出错，不进行本次更新")
                send_message_to_logstash("更新包下载出错，不进行本次更新",0)
                return False
        else:
            # LOG.info(u"用户未选择上传更新文件，使用默认路径下的更新文件")
            send_message_to_logstash(u"用户未选择上传更新文件，使用默认路径下的更新文件",1)
        # LOG.info(u"准备解压新版本的压缩包")
        send_message_to_logstash(u"准备解压新版本的压缩包", 1)
        if self.decompress_helper(server_name=server_name, version=new_version):
            # LOG.info(u"成功解压新版本的压缩包")
            send_message_to_logstash(u"成功解压新版本的压缩包,准备安装新版本", 1)
            # LOG.info(u"准备安装新版本")
            if self.install_server(server_name=server_name,
                                   version=new_version):
                # LOG.info(u"服务更新成功")
                send_message_to_logstash(u"服务更新成功", 1)
                return True
            else:
                # LOG.info(u"安装{}新版本失败，准备进行版本回退".format(server_name))
                send_message_to_logstash(u"安装{}新版本失败，准备进行版本回退".format(server_name), 0)
        else:
            # LOG.info(u"解压文件失败，不进行本次升级.")
            send_message_to_logstash(u"解压文件失败，不进行本次升级.",0)
        return False

    def stop_all(self):
        # LOG.info(u"停止{}服务下各个业务服务".format(self.server_name))
        # 自己添加杀掉 所有业务进程的方法
        # TaskManage().stop_all()
        # mq_pid_list = ProcessManage().get_task().keys()
        # if mq_pid_list:
        #     ProcessManage().stop(list(mq_pid_list))
        # LOG.info(u"停止{}主进程服务".format(self.server_name))
        send_message_to_logstash(u"停止{}主进程服务".format(self.server_name),1)
        self.stop_server(server_name=self.server_name)

    def start_update_process(self):

        run_version = self.check_version(server_name=self.server_name)
        if run_version:
            flag = self.update_server(server_name=self.server_name,
                                      new_version=self.new_version,
                                      run_version=run_version,
                                      file_url=self.update_file_url)
            if flag:
                self.stop_all()
                # LOG.info(u"重启服务")
                send_message_to_logstash(u"重启服务", 1)
                if not self.start_server(server_name=self.server_name):
                    # 版本回退
                    # LOG.info(u"重启服务失败，开始回退版本")
                    send_message_to_logstash(u"重启服务失败，开始回退版本", 1)
                    if self.back_version(server_name=self.server_name,
                                         run_version=run_version,
                                         update_url=self.update_file_url):
                        # LOG.info(u"停止老版本")
                        send_message_to_logstash(u"停止老版本", 1)
                        self.stop_server(server_name=self.server_name)
                        if self.start_server(server_name=self.server_name):
                            # LOG.info(u"成功启动旧版本服务")
                            send_message_to_logstash(u"成功启动旧版本服务", 1)
                        else:
                            # LOG.info(u"启动旧版本服务失败，请手动重启服务")
                            send_message_to_logstash(u"启动旧版本服务失败，请手动重启服务", -1)
                    else:
                        # LOG.info(u"版本回退失败，请手动升级服务")
                        send_message_to_logstash(u"版本回退失败，请手动升级服务", -1)
                else:
                    # LOG.info(u"服务重启成功")
                    send_message_to_logstash(u"服务重启成功", 1)
        else:
            # LOG.info(u"系统下未安装{}服务，不进行升级操作".format(self.server_name))
            send_message_to_logstash(u"系统下未安装{}服务，不进行升级操作".format(self.server_name), 1)

        global VERSION_FLAG
        VERSION_FLAG = None
        ZookeeperHelper(zookeeper=self.zookeeper).clear_node(node_path="/server_state/{}/{}".format(self.server_name,get_id(self.server_name)))
        # LOG.info(u"准备停止升级服务进程")
        send_message_to_logstash(u"准备停止升级服务进程",1)
        exit("停止升级服务进程")
        # update_pid = os.getpid()
        # command = "kill -9 {}".format(update_pid)
        # self.execute_command(command=command)

    def make_dirs(self):
        if not os.path.isdir(self.package_path):
            os.makedirs(self.package_path)

    def is_back_version(self):
        # 判断是否是回退的老版本的代码正在运行
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "back_version_flag")
        send_message_to_logstash(u"back_version_flag path {}".format(file_path), 1)
        if os.path.isfile(file_path):
            with open(file_path, "r") as read_obj:
                content = read_obj.read()
                if content:
                    json_obj = json.loads(content)
                    if (json_obj.get("back_flag") == 1) and (json_obj.get("update_version") == self.new_version):
                        return True
        return False

    def update(self):
        # 判断是否在升级过程中，如果在升级过程中，不接收升级策略
        global VERSION_FLAG
        if VERSION_FLAG:
            send_message_to_logstash("error:在升级过程中", 0)
            return "error:在升级过程中"
        else:
            VERSION_FLAG = self.new_version
            # 判断是否是升级不成功回退老版本的代码正在运行，是的话，不升级
            if self.is_back_version():
                send_message_to_logstash("error: 回退老版本的代码正在运行", 0)
                return "error: 回退老版本的代码正在运行"
        self.make_dirs()
        process = multiprocessing.Process(target=self.start_update_process)
        process.start()
        process.join()

    
def send_message_to_logstash(info,type):
    '''

    :param msg: 发送给logstash的信息
    :param LogFlag: 是否为日志信息
    :return:
    '''
    msg = {
        "SERVER": "log",
        "level": "info",
        "time": time.strftime(STANDARD_TIME_FORMAT),
        "log_type": "update",
        "content":info
    }
    if type ==-1:
        msg["level"] ="error"
    elif type ==0:
        msg["level"] = "warning"
    else:
        msg["level"] = "info"

    send_result = logstash_sender.send_to_logstash(msg)
    print(send_result)


            

