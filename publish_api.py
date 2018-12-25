#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/12/5 10:24
# @Author  : Fred Yang
# @File    : publish_api.py
# @Role    : 发布接口API


import pyotp
import requests
import json
from settings import api_gw, publish_info


class Publish_API():
    def __init__(self):
        self.url = api_gw
        self.user = publish_info.get('user')
        self.pwd = publish_info.get('password')
        self.key = publish_info.get('key')

    @property
    def get_mfa(self):
        t = pyotp.TOTP(self.key)
        return t.now()

    def login(self):
        try:
            headers = {"Content-Type": "application/json"}
            params = {"username": self.user, "password": self.pwd, "dynamic": self.get_mfa}
            result = requests.post('%s/accounts/login/' % self.url, data=json.dumps(params), headers=headers)

            ret = json.loads(result.text)
            if ret['code'] == 0:
                return ret['auth_key']
            else:
                print(ret)
                print(ret['msg'])
                exit(1)
        except Exception as e:
            print('[Error:] Publish用户接口登陆失败，错误信息：{}'.format(e))

    def get_publish_name_info(self, publish_name):
        token = self.login()
        try:
            params = {'key': 'publish_name', 'value': publish_name}
            res = requests.get('%s/task/v2/task_other/publish_cd/' % self.url, params=params,
                               cookies=dict(auth_key=token))
            ret = json.loads(res.content)
            if ret['code'] == 0: return ret['data']
        except Exception as e:
            print('[Error:] Publish发布接口连接失败，错误信息：{}'.format(e))
            exit(-2)

    def get_publish_all_info(self):
        '''获取发布配置所有信息'''
        try:
            token = self.login()
        except Exception as e:
            print(e)
            token = self.login()

        res = requests.get('%s/task/v2/task_other/publish_cd/' % self.url, cookies=dict(auth_key=token))
        ret = json.loads(res.content)
        if ret['code'] == 0: return ret['data']
