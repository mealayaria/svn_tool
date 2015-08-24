#!/usr/bin/python
# coding=utf-8

import conf
import shutil
import svn
import os

#解锁数据文件
def unlock_dat_file(reply):
    if reply == '0':
        dat_file = conf.code_dat + ' ' + conf.sit_dat
    elif reply == '1':
        dat_file = conf.sit_dat
    svn.svn_opt('unlock', dat_file)

#解锁待提交文件
def unlock_des_file():
    pass

#恢复数据文件
def dat_fallback(reply):
    code_dat_bak = conf.code_dat + '.bak' 
    sit_dat_bak = conf.sit_dat + '.bak' 

    if reply == '0':
        shutil.copy(code_dat_bak, conf.code_dat)
    shutil.copy(sit_dat_bak, conf.sit_dat)

    print u'数据文件回退成功'

#恢复未修改完成的xml文件
def file_fallback(des_path):
    shutil.copy(des_path + '.bak', des_path)
    print des_path + u' 回退成功'

#恢复之前的提交单
def xls_fallback(reply):
    #if reply == '0':
        xls_list = sorted(os.listdir(conf.xls_bak_path))
        #print conf.xls_bak_path + xls_list[-1]
        os.remove(conf.xls_path)
        os.rename(conf.xls_bak_path + xls_list[-1], conf.xls_path)
        print u'提交单恢复成功'

def fallback(reply):
    print u'回退数据文件'
    dat_fallback(reply)
    print u'解锁数据文件'
    unlock_dat_file(reply)
    print u'回退文件提交单'
    xls_fallback(reply)


if __name__ == '__main__':
    #dat_fallback()
    xls_fallback('0')
