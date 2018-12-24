#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/12/11 14:32
# @Author  : Fred Yang
# @File    : upload_cos.py
# @Role    : 上传资源到腾讯云COS


import sys, os

Base_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(Base_DIR)

from publish_api import Publish_API
from public import exec_shell
import fire


class Publish_COS():
    def __init__(self, data):
        """
        COS发布
        :param data: 前端传来的配置信息
        """
        self.repository = data.get('repository')  # 代码仓库
        self.repo_name = self.repository.split('/')[-1].replace('.git', '')  # 仓库名字
        self.access_id = data.get('SecretID')
        self.access_key = data.get('SecretKey')
        self.region = data.get('region')  # Bucket区域
        self.bucket_name = data.get('bucket_name')  # Bucket名字
        self.bucket_path = data.get('bucket_path')  # 目录路径
        self.clone_dir = '/opt'  # 代码拉取地址

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
        '''切换分支'''
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

    def code_process(self, exclude_file):
        '''代码处理，如过滤，处理完放到编译主机/tmp'''
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

    def login_cos(self):
        """
        登陆COS
        :return:
        """
        print('[INFO:] 开始登陆COS')
        login_cos = 'coscmd config -a %s -s %s -b %s -r %s -m 20 >/dev/null' % (
            self.access_id, self.access_key, self.bucket_name, self.region)
        login_cos_status, login_cos_output = exec_shell(login_cos)
        if login_cos_status == 0:
            print('[Success:] COS登陆成功')
        else:
            print('[Error:] COS登陆失败，错误信息：{}'.format(login_cos_output))

    def cos_upload(self):
        """
        上传资源到COS
        :return:
        """
        # 判断有没有权限
        print('[INFO:] 正在检查权限')
        check_cos = "coscmd getbucketacl"
        check_cos_status, check_cos_output = exec_shell(check_cos)
        if check_cos_status != 0:
            print('[Error:]Access Denied，请确认密钥是否有权限访问Bucket: {}'.format(self.bucket_name))
            exit(-403)

        source_dir = '/tmp/%s' % (self.repo_name)

        # cmd = 'aws s3 sync %s s3://%s --exclude *.git* --profile %s --quiet'%(source_dir,BucketDict[self.app_name][self.tag_type],BucketDict[self.app_name]['s3_key'])
        upload_cmd = 'coscmd upload -rs %s/ %s  >/dev/null 2>&1' % (source_dir, self.bucket_path)
        upload_cmd_status, upload_cmd_output = exec_shell(upload_cmd)
        if upload_cmd_status == 0:
            print('[Success:] 文件上传成功')
        else:
            print('[Error:] 上传失败，错误信息：{}'.format(upload_cmd_output))
            exit(-404)


def get_publish_info(publish_name):
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
    obj = Publish_COS(data)
    # 克隆代码
    obj.git_clone()
    # 切换分支
    obj.checkout_tag(git_tag)
    # 获取过滤文件名字
    exclude_file_name = obj.get_exclude_file(data)
    # 文件处理，比如：过滤文件到/tmp临时文件
    obj.code_process(exclude_file_name)
    # 登陆COS
    obj.login_cos()
    # 上传文件
    obj.cos_upload()


if __name__ == '__main__':
    fire.Fire(main)
