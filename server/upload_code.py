#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/12/4 16:47
# @Author  : Fred Yang
# @File    : upload_code.py
# @Role    : 发布代码到服务器


import os
import sys

Base_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(Base_DIR)
import shutil
from public import exec_shell
from public import exec_thread
from get_publish_info import get_publish_data, get_all_hosts
import fire


class UploadCode():
    """
    发布代码到目标主机，并发操作
        01. 代码先同步到编译主机的/tmp下
        02. 将本地/tmp下并发上传到目标主机的/tmp
    """

    def __init__(self, data):
        self.publish_path = data.get('publish_path')  # 发布目录
        self.repository = data.get('repository')  # 代码仓库
        self.repo_name = self.repository.split('/')[-1].replace('.git', '')  # 仓库名字
        self.local_dir = '/tmp/'

    def code_process(self, exclude_file):
        '''代码处理，如过滤，处理完放到编译主机/tmp'''
        code_dir = self.publish_path + self.repo_name
        try:
            if os.path.exists(code_dir):
                rsync_local_cmd = 'cd {} && rsync -ahqzt --delete --exclude-from="{}" {} {}'.format(code_dir,
                                                                                                    exclude_file,
                                                                                                    code_dir,
                                                                                                    self.local_dir)
                # print('[CMD:]', rsync_local_cmd)
                recode, stdout = exec_shell(rsync_local_cmd)
                if recode == 0:
                    print('[Success]: 构建机器代码处理(如：exclude)到临时路径：/tmp/{} 完成 '.format(self.repo_name))

                else:
                    print('[Error]: Rsync bulid host:/tmp failed')
                    exit(405)

            else:
                print('[Error]: Not fount git repo dir:{} '.format(code_dir))
                exit(404)

        except Exception as e:
            print(e)

    def rsync_tmp(self, host):
        """
        发布代码到目标主机的/tmp目录
        :return:
        """
        if not isinstance(host, dict):
            raise ValueError()

        ip = host.get('ip')
        port = host.get('port', 22)
        user = host.get('user', 'root')
        password = host.get('password')

        local_code_path = self.local_dir + self.repo_name  # 处理后的本地代码路径
        rsync_tmp_cmd = "sshpass -p {} rsync -ahqzt --delete -e 'ssh -p {}  -o StrictHostKeyChecking=no '  {} {}@{}:{}".format(
            password, port, local_code_path, user, ip, '/tmp/')
        # print('[CMD:] ', rsync_tmp_cmd)
        rsync_status, rsync_output = exec_shell(rsync_tmp_cmd)
        if rsync_status == 0:
            # 同步完成删除/tmp/repo_name目录
            print('[Success]: rsync host:{} to /tmp/{} sucess...'.format(ip, self.repo_name))
        else:
            print('[Error]: rsync host:{} to /tmp/{} faild, please check your ip,port,user,password...'.format(ip,
                                                                                                               self.repo_name))
            exit(-407)

    def delete_tmp(self):
        """删除临时代码目录"""
        tmp_path = '/tmp/{}'.format(self.repo_name)
        if os.path.exists(tmp_path):
            shutil.rmtree(tmp_path)


def get_exclude_file(data):
    '''获取exclude文件内容写入临时文件,前端传来的只是字符串'''
    try:
        exclude_content = data.get('exclude_file')
        publish_name = data.get('publish_name')
        file_name = '/tmp/publish_exclude_{}_file.txt'.format(publish_name)
        f = open(file_name, 'w', encoding='utf-8')
        f.write(exclude_content)
        f.close()
        print('[Success]: Publish exclude_file has been written {}'.format(file_name))
        return file_name
    except Exception as e:
        print(e)
        print('[Error]: Publish exclude_file write falid')
        exit(-500)


def main(flow_id):
    """
    01. 处理exclude文件
    02. 获取所有主机信息
    03. 并发代码到目的主机/tmp
    :return:
    """
    print('[INFO]: 这部分是处理exclude 将过滤后的代码并发到你的目标主机/tmp下，等待你的部署,如果rsync同步失败请确认服务器和目标主机都有rsync命令')
    data = get_publish_data(flow_id)  # 获取发布信息
    exclude_file = get_exclude_file(data)  # 过滤文件名称
    obj = UploadCode(data)
    obj.code_process(exclude_file)  # 处理代码，如：exclude操作
    all_hosts = get_all_hosts(flow_id)
    exec_thread(func=obj.rsync_tmp, iterable1=all_hosts)
    obj.delete_tmp()


if __name__ == '__main__':
    fire.Fire(main)
