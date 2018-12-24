#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/12/7 13:42
# @Author  : Fred Yang
# @File    : deploy_code.py
# @Role    : 部署代码，下发代码，此步将代码最终发布到代码目录


import os
import sys

Base_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(Base_DIR)
from public import exec_shell
from public import exec_thread
from get_publish_info import get_publish_data, get_all_hosts
import fire


class DeployCode():

    def __init__(self, data):
        self.publish_path = data.get('publish_path')  # 发布目录
        self.repository = data.get('repository')  # 代码仓库
        self.repo_name = self.repository.split('/')[-1].replace('.git', '')  # 仓库名字

    def code_deploy(self, host):
        if not isinstance(host, dict):
            raise ValueError()

        '''/tmp下的代码是upload_code脚本上传过来的'''
        tmp_code_path = '/tmp/{}'.format(self.repo_name)
        # if not os.path.exists(tmp_code_path):
        #     print('[Error]: No code found')
        #     sys.exit(-100)

        ip = host.get('ip')
        port = host.get('port', 22)
        user = host.get('user', 'root')
        password = host.get('password')
        # code_path = self.publish_path + self.repo_name
        # depoly_cmd = "sshpass -p {} rsync -ahqzt --delete -e 'ssh -p {}  -o StrictHostKeyChecking=no '  {} {}@{}:{}".format(
        #     password, port, tmp_code_path, user, ip, self.publish_path)
        rsync_cmd = 'rsync -ahqzt --delete {} {}'.format(tmp_code_path, self.publish_path)
        depoly_cmd = "sshpass -p {} ssh -p {} -o StrictHostKeyChecking=no {}@{} '{}'".format(
            password,
            port,
            user, ip,
            rsync_cmd)
        # print('[CMD:]', depoly_cmd)

        try:
            depoly_status, depoly_output = exec_shell(depoly_cmd)
            if depoly_status == 0:
                print('[Success]: Host:{} 发布成功'.format(ip))
            else:
                print('[Error]: Host:{} 失败，错误信息: {}'.format(ip, depoly_output))
                exit(-3)

        except Exception as e:
            print(e)
            exit(-500)

def main(flow_id):
    print('[INFO]: 这部分是将代码正式下发/同步到你的代码目录')
    data = get_publish_data(flow_id)  # 获取发布信息
    obj = DeployCode(data)
    all_hosts = get_all_hosts(flow_id)
    exec_thread(func=obj.code_deploy, iterable1=all_hosts)


if __name__ == '__main__':
    fire.Fire(main)
