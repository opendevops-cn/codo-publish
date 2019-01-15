#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Contact : 191715030@qq.com
Author  : shenshuo
Date    : 2019/1/14
Desc    : 编译docker镜像 并上传
"""
import os
import sys
import fire

Base_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(Base_DIR)
from public import exec_shell
from get_publish_info import get_publish_data
from settings import api_settings
from api_handler import API


class BuildImage(object):
    def __init__(self, data, tag):
        self.git_tag = tag
        self.docker_registry = data.get('docker_registry')
        self.repository = data.get('repository')  # 代码仓库
        self.app_name = self.repository.split('/')[-1].replace('.git', '')
        self.version_dir = os.path.join('/var/www/version/', self.repository.split('/')[-2])
        self.code_dir = os.path.join(self.version_dir, self.app_name)
        self.image_name = "{}{}--{}:{}".format(self.docker_registry, self.repository.split('/')[-2], self.app_name,
                                               self.git_tag)

    def build_image(self):
        cmd = "cd {} && docker build . -t {}".format(self.code_dir, self.image_name)
        exec_status, exec_output = exec_shell(cmd)
        if exec_status == 0:
            print('[Success]: docker build {} OK...'.format(self.image_name))
        else:
            print('[Error]: docker build {} failed ...\n[Error]: {}'.format(self.image_name, exec_output))
            exit(-1)

    def login(self):
        obj = API()
        result = obj.get_api_info(api_settings['docker_registry_info_api'])
        for i in result:
            if i['registry_url'] == self.docker_registry:
                login_cmd = "docker login -u {} -p {} {}".format(i['user_name'], i['password'], i['registry_url'])
                print(login_cmd)
                exec_status, exec_output = exec_shell(login_cmd)
                if exec_status == 0:
                    print('[Success]: docker login {} OK...'.format(self.docker_registry))
                else:
                    print('[Error]: docker login {} failed ...\n[Error]: {}'.format(self.docker_registry, exec_output))
                    exit(-1)

    def push_image(self):
        self.login()
        cmd = "docker push {}".format(self.image_name)
        exec_status, exec_output = exec_shell(cmd)
        if exec_status == 0:
            print('[Success]: docker push {} successfully...'.format(self.image_name))
        else:
            print('[Error]: docker push {} failed ...\n[Error]: {}'.format(self.image_name, exec_output))
            exit(-1)


def main(flow_id, git_tag):
    """
    :param flow_id: 订单ID
    :param git_tag: Git Tag名字
    :return:
    """
    print('[INFO]: 这部分是用来在编译镜像，并且上传docker仓库')
    data = get_publish_data(flow_id)  # 配置信息
    obj = BuildImage(data, git_tag)  # 初始化类
    obj.build_image()  # 编译镜像
    obj.push_image()  # 上传镜像


if __name__ == '__main__':
    fire.Fire(main)
