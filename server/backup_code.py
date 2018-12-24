#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/12/5 18:35
# @Author  : Fred Yang
# @File    : backup_code.py
# @Role    : 备份代码


import os
import sys

Base_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(Base_DIR)
from public import exec_shell
from public import exec_thread

from get_publish_info import get_publish_data, get_all_hosts
import fire


class BackupCode():
    def __init__(self, data):
        self.publish_path = data.get('publish_path')  # 发布目录
        self.repository = data.get('repository')  # 代码仓库
        self.repo_name = self.repository.split('/')[-1].replace('.git', '')  # 仓库名字
        self.local_dir = '/tmp/'
        self.backup_dir = '/tmp/code_backup/'

    def code_backup(self, host):
        """
        :param host: 主机信息，IP端口用户密码
        :return:
        """
        if not isinstance(host, dict):
            raise ValueError()

        ip = host.get('ip')
        port = host.get('port', 22)
        user = host.get('user', 'root')
        password = host.get('password')
        code_path = self.publish_path + self.repo_name
        try:
            backup_cmd = '[ ! -d "{}" ] && mkdir {} ; cp -aR {} {} && echo success'.format(
                self.backup_dir, self.backup_dir, code_path, self.backup_dir)
            ssh_cmd = "sshpass -p {} ssh -p {} -o StrictHostKeyChecking=no {}@{} '{}'".format(password, port, user,
                                                                                              ip,
                                                                                              backup_cmd)

            ssh_status, ssh_output = exec_shell(ssh_cmd)
            if ssh_status == 0:
                print('[Success]: Host: {}  备份路径: {}'.format(ip, self.backup_dir))
            else:
                print('[Error]:  Host: {} 备份失败，信息: {} faild'.format(ip, ssh_output))
                print(ssh_output)
        except Exception as e:
            print(e)
            exit(-500)


def main(flow_id):
    print('[INFO]: 这部分是备份你目标主机的代码,只保留一天备份，若不需要可以跳过此步骤')
    data = get_publish_data(flow_id)  # 获取发布信息
    obj = BackupCode(data)
    all_hosts = get_all_hosts(flow_id)
    exec_thread(func=obj.code_backup, iterable1=all_hosts)


if __name__ == '__main__':
    fire.Fire(main)
