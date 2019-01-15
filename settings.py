#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/12/24 16:57
# @Author  : Fred Yang
# @File    : settings.py
# @Role    : 发布配置信息


# 系统配置中的API地址,网关地址
api_gw = 'http://gw.shinezone.net.cn/api'
mail_api = '{}/mg/v2/notifications/mail/'.format(api_gw)
login_api = '{}/accounts/login/'.format(api_gw)
publish_info_api = '{}/task/v2/task_other/publish_cd/'.format(api_gw)
docker_registry_info_api = '{}/task/v2/task_other/docker_registry/'.format(api_gw)
get_key_api = '{}/task/v2/task/accept/'.format(api_gw)

### cmdb 读取get，获取CSRF 邮件发送post 镜像仓库信息get
api_user = 'publish'
api_pwd = 'shenshuo'
api_key = 'JJFTQNLXHBYWSVSCINNEWNDFJRKWGY2UNJTTSVTLMN3UGUKXPFDE4NDH'

api_settings = dict(
    api_user=api_user,
    api_pwd=api_pwd,
    api_key=api_key,
    api_gw=api_gw,
    mail_api=mail_api,
    login_api=login_api,
    publish_info_api=publish_info_api,
    get_key_api=get_key_api,
    docker_registry_info_api=docker_registry_info_api
)

# 发布接口账户密码
publish_info = {
    'user': 'publish',
    'password': 'shenshuo',
    'key': 'JJFTQNLXHBYWSVSCINNEWNDFJRKWGY2UNJTTSVTLMN3UGUKXPFDE4NDH'
}

# CMDB接口账户密码
cmdb_info = {
    'user': 'cmdb',
    'password': 'password',
    'key': 'O42EEODGMFHGMYT2OAM3KN3HJVBE4Z3CKI3TKRDHG5MWSUCGMNHEE6LI'
}
