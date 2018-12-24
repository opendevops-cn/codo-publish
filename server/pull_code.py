#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/12/4 11:00
# @Author  : Fred Yang
# @File    : pull_code.py
# @Role    : 02. 获取代码


import os
import sys

Base_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(Base_DIR)
from public import exec_shell
from get_publish_info import get_publish_data
import fire


class PullCode():
    """
    通过git地址拉取代码
    首次： git clone
    存在： git tetch --all && git pull
    """

    def __init__(self, data):
        self.publish_path = data.get('publish_path')  # 发布目录
        self.repository = data.get('repository')  # 代码仓库
        self.repo_name = self.repository.split('/')[-1].replace('.git', '')  # 仓库名字

    def git_clone(self):
        '''检测发布目录没有代码则进行git clone'''
        code_dir = self.publish_path + self.repo_name
        try:
            if not os.path.exists(code_dir):
                print('[INFO]: Start pulling a new codebase to {}'.format(code_dir))
                git_clone_cmd = '[ ! -d "{}" ] && mkdir {} ;cd {} && git clone {}'.format(self.publish_path,
                                                                                          self.publish_path,
                                                                                          self.publish_path,
                                                                                          self.repository)  # 克隆代码
                print('[CMD:] ', git_clone_cmd)
                git_clone_status, git_clone_output = exec_shell(git_clone_cmd)
                if git_clone_status == 0:
                    print('[Success]: git clone {} sucess...'.format(self.repository))
                else:
                    print('[Error]: git clone {} faild...'.format(self.repository))
                    exit(404)
            else:
                print('[PASS]： The repository already exists, skip the clone and update directly')
        except Exception as e:
            print(e)

    def checkout_tag(self, git_tag):
        '''切换分支'''
        git_fetch_cmd = 'cd {}/{} && git fetch -t -p -f && git fetch --all'.format(self.publish_path,

                                                                                   self.repo_name)  # 更新代码
        git_checkout_cmd = 'cd {}/{} && git clean -df  && git checkout {}'.format(
            self.publish_path, self.repo_name, git_tag)  # 切换分支

        # print('[CMD:]', git_fetch_cmd)
        # print('[CMD:]', git_checkout_cmd)
        try:
            git_fetch_status, git_fetch_output = exec_shell(git_fetch_cmd)
            if git_fetch_status == 0:
                git_check_status, git_check_output = exec_shell(git_checkout_cmd)
                if git_check_status == 0:
                    print('[Success]: git checkout tag: {} successfully...'.format(git_tag))
                else:
                    print('[Error]: git checkout tag: {} faild...'.format(git_tag))
                    exit(402)
            else:
                print('[Error]: git fetch faild...')
                exit(403)
        except Exception as e:
            print(e)
            exit(-500)


def main(flow_id, git_tag):
    """
    :param flow_id: 订单ID
    :param git_tag: Git Tag名字
    :return:
    """
    print('[INFO]: 这部分是用来在构建机器上拉取代码，切换Tag操作')
    data = get_publish_data(flow_id)  # 配置信息
    obj = PullCode(data)  # 初始化类
    obj.git_clone()  # 克隆代码
    obj.checkout_tag(git_tag)  # 切换Tag


if __name__ == '__main__':
    fire.Fire(main)
