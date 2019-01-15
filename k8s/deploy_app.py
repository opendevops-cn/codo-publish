#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Contact : 191715030@qq.com
Author  : shenshuo
Date    : 2019/1/15
Desc    : 滚动升级
"""

import os
import sys
import fire

Base_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(Base_DIR)
from public import exec_shell
from get_publish_info import get_publish_data


class Deploy(object):
    def __init__(self, data, tag):
        self.git_tag = tag
        self.docker_registry = data.get('docker_registry')
        self.repository = data.get('repository')  # 代码仓库
        self.app_name = self.repository.split('/')[-1].replace('.git', '')
        self.deploy_name = "{}--{}".format(self.repository.split('/')[-2], self.app_name).replace("_", "-")
        self.image_name = "{}{}--{}:{}".format(self.docker_registry, self.repository.split('/')[-2], self.app_name,
                                               self.git_tag)
        self.k8s_host = data.get('k8s_host')
        self.namespace = data.get('namespace')

    def run(self):
        cmd = "kubectl set image deployment/{} {}={} -n {}".format(self.deploy_name, self.deploy_name, self.image_name,
                                                                   self.namespace)
        exec_status, exec_output = exec_shell("ssh {} '{}'".format(self.k8s_host, cmd))
        if exec_status == 0:
            print('[Success]: kubernetes rolling-update {} successfully...'.format(self.image_name))
        else:
            print('[Error]: kubernetes rolling-update {} failed ...\n[Error]: {}'.format(self.image_name, exec_output))
            exit(-1)

    def check(self):
        cmd = "ssh %s kubectl get pod -n %s -o wide -l app=%s |grep -v 'NAME' |awk '{print($3)}'" % (self.k8s_host,
                                                                                                     self.namespace,
                                                                                                     self.deploy_name)

        exec_status, exec_output = exec_shell(cmd)
        if exec_status == 0 and exec_output[0] == 'Running':
            print('[Success]: The pod status is running...')
        else:
            print('[Error]: The pod status is not running...\n[Error]: {}'.format(exec_output))
            print('[Warning] rollout undo deployment start !!!!')
            rollback_cmd = "ssh {} kubectl rollout undo -n {} deployment {}".format(self.k8s_host, self.namespace,
                                                                                    self.deploy_name)
            exec_status1, exec_output1 = exec_shell(rollback_cmd)
            print("{} {}".format(exec_status1, exec_output1))
            print("Roll back to the last version end")
            exit(-2)


def main(flow_id, git_tag):
    """
    :param flow_id: 订单ID
    :param git_tag: Git Tag名字
    :return:
    """
    print('[INFO]: 这部分是用来在编译镜像，并且上传docker仓库')
    data = get_publish_data(flow_id)  # 配置信息
    obj = Deploy(data, git_tag)  # 初始化类
    obj.run()  # 滚动升级
    obj.check()  # 检查POD状态


if __name__ == '__main__':
    fire.Fire(main)

### 注意事项  ssh kubernetes master可到以直连 要设置镜像仓库的key。命名空间隔离，所以每个命名空间都要单独设置
### kubectl create secret docker-registry registrysecret --docker-server=harbor.shinezone.com  --docker-username=admin --docker-password=xxxxxxxxxxxxx --docker-email=191715030@qq.com -n shenshuo
### kubectl patch serviceaccount default -p '{"imagePullSecrets": [{"name": "registrysecret"}]}'  -n shenshuo
###  python3 /home/dev/python_dev/codo-publish/k8s/deploy_app.py 234 v0.20181226R1
