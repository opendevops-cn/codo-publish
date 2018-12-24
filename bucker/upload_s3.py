#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/12/12 17:31
# @Author  : Fred Yang
# @File    : upload_s3.py
# @Role    : 上传资源到AWS S3


import sys, os

Base_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(Base_DIR)

from publish_api import Publish_API
from public import exec_shell
import fire


class Publish_S3():
    def __init__(self, data):
        """
        S3发布
        :param data: 前端传来的配置信息
        """
        self.repository = data.get('repository')  # 代码仓库
        self.repo_name = self.repository.split('/')[-1].replace('.git', '')  # 仓库名字
        self.access_id = data.get('SecretID')
        self.access_key = data.get('SecretKey')
        self.region = data.get('region')  # Bucket区域
        self.bucket_name = data.get('bucket_name')  # Bucket名字
        self.clone_dir = '/opt'  # 代码拉取地址
        self.local_dir = '/tmp/{}/'.format(self.repo_name)  # 处理后的临时存放代码路径

    def git_clone(self):
        '''检测发布目录没有代码则进行git clone'''
        try:
            if not os.path.exists(self.clone_dir):
                print('[INFO]: Start pulling a new codebase to {}'.format(self.clone_dir))
                git_clone_cmd = '[ ! -d "{}" ] && mkdir {} ;cd {} && git clone {}'.format(self.clone_dir,
                                                                                          self.clone_dir,
                                                                                          self.clone_dir,
                                                                                          self.repository)  # 克隆代码
                # print('[CMD:] ', git_clone_cmd)
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
        """
        切换分支
        :param git_tag: 分支名称
        :return:
        """

        git_fetch_cmd = 'cd {}/{} && git fetch -t -p -f && git fetch --all'.format(self.clone_dir,

                                                                                   self.repo_name)  # 更新代码
        git_checkout_cmd = 'cd {}/{} && git clean -df  && git checkout {}'.format(
            self.clone_dir, self.repo_name, git_tag)  # 切换分支

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

    def get_exclude_file(self, data):
        """
        获取exclude文件内容写入临时文件,前端传来的只是字符串
        :param data: 发布配置信息，JSON
        :return:
        """
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

    def code_process(self, exclude_file):
        """
        代码处理，如过滤，处理完放到编译主机/tmp
        :param exclude_file:  过滤文件名称
        :return:
        """

        try:
            if os.path.exists(self.clone_dir):
                rsync_local_cmd = 'cd {} && rsync -ahqzt --delete --exclude-from="{}" {}/{} {}'.format(self.clone_dir,
                                                                                                       exclude_file,
                                                                                                       self.clone_dir,
                                                                                                       self.repo_name,
                                                                                                       '/tmp')
                # print('[CMD:]', rsync_local_cmd)
                recode, stdout = exec_shell(rsync_local_cmd)
                if recode == 0:
                    print('[Success]: 构建机器代码处理(如：exclude)到临时路径：/tmp/{} 完成 '.format(self.repo_name))

                else:
                    print('[Error]: Rsync bulid host:/tmp failed')
                    exit(405)

            else:
                print('[Error]: Not fount git repo dir:{} '.format(self.clone_dir))
                exit(404)

        except Exception as e:
            print(e)
            exit(406)

    def aws_configure(self):
        """
        配置AWS configure信息，使能访问AWS S3
        :return:
        """
        ca_file_name = '/root/.aws/credentials'
        ca_file_content = "[default]\naws_access_key_id = {}\naws_secret_access_key = {}".format(self.access_id,
                                                                                                 self.access_key)
        aws_config_name = '/root/.aws/config'
        aws_config_content = '[default]\nregion = {}'.format(self.region)
        try:
            f = open(ca_file_name, 'w', encoding='utf-8')
            f.write(ca_file_content)
            f.close()
            print('[INFO]: AWS 证书文件 – 位于 ~/.aws/credentials')
            f = open(aws_config_name, 'w', encoding='utf-8')
            f.write(aws_config_content)
            f.close()
            print('[INFO]: CLI 配置文件 – 位于 ~/.aws/config')
        except Exception as e:
            print(e)
            print('[Error]: AWS 配置文件写入失败，也可以使用aws configure进行交互式配置')
            exit(-1)

    def upload_file(self):
        """
        将资源文件上传到AWS S3,使用AWSCLI的 AWS S3 Sync方式
        :return:
        """
        source_dir = '/tmp/%s/' % (self.repo_name)
        upload_s3_cmd = 'aws s3 sync %s s3://%s --exclude *.git* --quiet' % (source_dir, self.bucket_name)
        print('[INFO]：Start upload for bucket: %s' % self.repo_name)
        upload_s3_status, upload_s3_ouput = exec_shell(upload_s3_cmd)
        if upload_s3_status == 0:
            print('[Success:] AWS S3 上传成功！')
        else:
            print('[Error:] AWS S3 上传失败！')


def get_publish_info(publish_name):
    """
    获取发布配置信息
    :param publish_name:发布应用名称
    :return:
    """
    obj = Publish_API()
    publish_info = obj.get_publish_name_info(publish_name)
    for data in publish_info:
        return data


def main(publish_name, git_tag):
    """
    :param publish_name: 发布应用名称
    :param git_tag: 发布TAG名称
    :return:
    """
    # 获取配置信息
    data = get_publish_info(publish_name)
    # 实例化
    obj = Publish_S3(data)
    # 克隆代码
    obj.git_clone()
    # 切换分支
    obj.checkout_tag(git_tag)
    # 获取过滤文件名字
    exclude_file_name = obj.get_exclude_file(data)
    # 文件处理，比如：过滤文件到/tmp临时文件
    obj.code_process(exclude_file_name)
    # AWS 配置
    obj.aws_configure()
    # 资源上传
    obj.upload_file()


if __name__ == '__main__':
    fire.Fire(main)
