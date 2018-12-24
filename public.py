#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/12/4 13:18
# @Author  : Fred Yang
# @File    : public.py
# @Role    : 公共工具

import os
import sys
import re
import time
import subprocess
import paramiko
import concurrent.futures


def lock_json(script_name):
    """文件锁"""
    pid_file = '/tmp/publish_data_json.pid'
    lock_count = 0
    while True:
        if os.path.isfile(pid_file):
            ###打开脚本运行进程id文件并读取进程id
            with open(pid_file, 'r') as fp_pid:
                process_id = fp_pid.read()

            ###判断pid文件取出的是否是数字
            if not process_id:
                break

            if not re.search(r'^\d', process_id):
                break

            ###确认此进程id是否还有进程
            lock_count += 1
            if lock_count > 30:
                print('1 min after this script is still exists')
                sys.exit(111)
            else:
                check_list = os.popen('/bin/ps %s|grep "%s"' % (process_id, script_name)).readlines()
                if check_list:
                    print('check_list--->', check_list)
                    print('cmd ----> /bin/ps %s|grep "%s"' % (process_id, script_name))
                    print("The script is running...... ,Please wait for a moment!")
                    time.sleep(5)
                else:
                    os.remove(pid_file)
        else:
            break

    ###把进程号写入文件
    with open(pid_file, 'w') as wp_pid:
        p_id = os.getpid()
        wp_pid.write(str(p_id))


def exec_shell(cmd):
    '''执行shell命令函数'''
    sub2 = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = sub2.communicate()
    ret = sub2.returncode
    if ret == 0:
        return ret, stdout.decode('utf-8').split('\n')
    else:
        return ret, stdout.decode('utf-8').replace('\n', '')


def ssh_connect(ip, port, user, password):
    try:
        _ssh_fd = paramiko.SSHClient()
        _ssh_fd.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        _ssh_fd.connect(hostname=ip, port=port, username=user, password=password)
        return _ssh_fd
    except Exception as e:
        print('[Error]: ssh {}@{} {}'.format(user, ip, e))


def exec_thread(func, iterable1):
    ### 取所有主机 最多启动100个进程
    pool_num = 10
    with concurrent.futures.ProcessPoolExecutor(pool_num) as executor:
        executor.map(func, iterable1)
