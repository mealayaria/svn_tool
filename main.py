# coding=utf-8

import excel
import xml_opt
import svn
import conf 
import copy
import showlist
import exception
import shutil
import datetime
import os
import sys

#获取要提交文件的类型
#若为xml则执行文件内容修改操作
#若为其他类型则直接进行文件覆盖
def get_file_info(commit_info):
    #fileInfo = commit_info[-1].split('/')[-1].split('.')
    #file_name, file_type = fileInfo[0], fileInfo[1]
    file_path = os.path.basename(commit_info[-1])
    file_name, file_type = os.path.splitext(file_path)
    #print file_type
    #新增文件直接复制
    if commit_info[0] == u'新增':
        return -1
    else:
        #若为xml格式则执行文件内容修改逻辑
        if file_type == '.xml':
            return conf.format_str_dict[file_name]
            #return 0
        #其他格式则直接进行文件替换
        else:
            return 1

# 获取未提交文件列表
def get_file_list(commit_info_li):
    #print 'commit_info_li, ', commit_info_li
    new_add_file_list = []
    other_file_list = []
    for file_info in commit_info_li:
        del file_info[2]; del file_info[-1]
        if file_info[0] == u'新增':
            #new_add_file_list.append(file_info[-1])
            new_add_file_list.append(file_info)
        else:
            #other_file_list.append(file_info[-1])
            other_file_list.append(file_info)
    #print file_list
    return new_add_file_list, other_file_list

def join_file(des_dir, file_list):
    new_file_list = []
    for file in file_list:
        new_file_list.append(des_dir + file.encode('utf-8'))
    #print ' '.join(new_file_list)
    return ' '.join(new_file_list)

#嵌套列表组合成字符串
def nest_li_to_str(msg, commit_info_li):
    for commit_info in commit_info_li:
        if isinstance(commit_info, list):
            try:
                msg += ':'.join(commit_info) + '\t'
            except:
                msg = nest_li_to_str(msg, commit_info)
        else:
            msg += commit_info + '\t'
    msg += '\n'
    return msg

def create_msg(commit_info_li):
    #print u'create_msg: ', commit_info_li
    msg_obj = open(conf.log_file, 'w+b')
    msg = ''
    try:
        msg = nest_li_to_str(msg, commit_info_li).encode('gb2312')
        msg_obj.write(msg)
    except:
        print u'注释文件生成失败'
        exception.fallback(conf.reply)
    finally:
        msg_obj.close()

def ready_for_commit(des_dir, file_info):
    if isinstance(file_info[0], list):
        file_list = map(lambda file_info: file_info[-1], file_info)
    else:
        file_list = file_info
    #print 'file_list, ', file_list
    file_list_str = join_file(des_dir, file_list)
    #print 'file_list_str, ', file_list_str
    svn.svn_opt('update', file_list_str)
    print 'update OK'
    try:
        svn.svn_opt('lock', file_list_str)
    except svn.svnError:
        print u'lock失败，请确认是否有其他人正在操作'
        exception.fallback(conf.reply)
    else:
        print file_list_str, 'lock OK'

def add_new_file(des_dir, new_add_info):
    new_add_list = map(lambda new_add_info: new_add_info[-1], new_add_info)
    new_add_list_str = join_file(des_dir, new_add_list)
    try:
        svn.svn_opt('add', new_add_list_str)
    except:
        print u'新增文件失败'
        svn.svn_opt('revert', new_add_list_str)
        exception.fallback(conf.reply)
        #exception.dat_fallback()
        #exception.unlock_dat_file()
        exit(1)
    else:
        print 'add OK'

#def update_file_stat(ready_commit_info, cur_svn_ver):
#    for file_info in ready_commit_info:
#        file_info[3] = 'OK'
#        file_info[4] = cur_svn_ver
#    return ready_commit_info

def commit_to_des(des_dir, file_info):
    if isinstance(file_info[0], list):
        file_list = map(lambda file_info: file_info[-1], file_info)
    else:
        file_list = file_info
    #msg = u'本次共提交%d个文件 ' % len(file_list)
    create_msg(file_info)
    file_list_str = join_file(des_dir, file_list)
    #print u'提交文件列表，', file_list_str
    try:
        #svn.svn_opt('commit', file_list_str, msg.encode('gb2312'))
        svn.svn_opt('commit', file_list_str)
    except svn.svnError:
        print u'svn commit失败'
        exception.fallback(conf.reply)
        #exception.dat_fallback()
        #exception.unlock_dat_file()
        exit(1)
    #print 'commit OK'
    #cur_ver = svn.get_cur_ver(file_list_str)
    #return cur_ver


def dat_bak(reply):
    try:
        #提交code库功能暂时不用
        if reply == '0':
            shutil.copy(conf.code_dat, conf.code_dat + '.bak')
        shutil.copy(conf.sit_dat, conf.sit_dat + '.bak')
    except:
        print u'数据文件备份失败'
        exit(1)
    print u'数据文件备份成功'

def info_to_dat(xls_path, reply):
    src_xls = excel.xl_rd(xls_path)
    try:
        commit_info_li = src_xls.get_commit_info()
        if not commit_info_li :
            raise Exception
    except Exception:
        print u'不存在需提交内容，请更新"文件提交单.xls"'
        exception.unlock_dat_file(conf.reply)
        exit(1)
 
    #备份本次提交excel列表，加上时间戳
    now = datetime.datetime.now().strftime('%Y%m%d%H%M')
    try:
        os.rename(xls_path, conf.xls_bak_path + xls_path + '.' + now)
    except WindowsError:
        print u'备份文件提交单出错，请先关闭已打开的"文件提交单.xls"'
        exit(1)
    shutil.copy(conf.template, xls_path)

    #将excel中未提交的文件列表写进数据文件中
    try:
        if reply == '0':
            code_dat = showlist.jsonProcess(conf.code_dat)
            code_dat.add_file(commit_info_li, conf.code_dat)
        sit_dat  = showlist.jsonProcess(conf.sit_dat)
        sit_dat.add_file(commit_info_li, conf.sit_dat)
    except:
        print u'写入数据列表失败'
        exception.fallback(conf.reply)
        #exception.dat_fallback()
        #exception.unlock_dat_file()
        exit(1)


if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf-8')

    while True:
        print u'请选择要提交的版本库：\n0. code库(暂不要使用)  \n1. 准sit库  \n2. 查询3天提交记录(未实现)  \n3. 查询7天提交记录(未实现)  \nq. 退出 \n请输入选择序号：'
        try:
            conf.reply = raw_input()
        except KeyboardInterrupt:
            exit(1)
            #exception.dat_fallback()
        else:
            if conf.reply == '0':
                print u'提交至code库功能暂时不用'
                exit(0)
                ready_for_commit('', [conf.code_dat, conf.sit_dat])
                #备份数据文件防止中途出错
                dat_bak(conf.reply)
                info_to_dat(conf.xls_path, conf.reply)
                src_dir, des_dir = conf.cur_src_dir, conf.cur_code_dir
                dat = showlist.jsonProcess(conf.code_dat)
                break
            elif conf.reply == '1':
                print u'提交至准sit库'
                #若开启code库功能则注释掉下一行
                ready_for_commit('', [conf.sit_dat])
                #备份数据文件防止中途出错
                dat_bak(conf.reply)
                info_to_dat(conf.xls_path, conf.reply)
                src_dir, des_dir = conf.cur_code_dir, conf.cur_sit_dir
                dat = showlist.jsonProcess(conf.sit_dat)
                break
            elif conf.reply == '2':
                print u'查询3天提交记录'
                exit(0)
            elif conf.reply == '3':
                print u'查询7天提交记录'
                exit(0)
            elif conf.reply == 'q':
                exit(0)
            else:
                print u'选项错误，请重新输入'

    #try:
    #打印未提交文件列表
    dat.show_list()

    #获取未提交的文件信息列表
    try:
        cur_commit_info_li = dat.get_commit_info()
    #print 'cur_commit_info_li, ', cur_commit_info_li
    #未提交文件列表,分别为已存在的文件列表和新增文件列表
        new_add_commit_info, other_commit_info = get_file_list(cur_commit_info_li)
    except:
        print u'获取未提交的文件信息列表失败'
        exception.fallback(conf.reply)
        exit(1)

    #提交前svn更新、锁定待提交文件
    #print u'新增的未提交文件列表, ', new_add_commit_info
    #print u'已存在的未提交文件列表, ', other_commit_info
    if other_commit_info:
        ready_for_commit(des_dir, other_commit_info)
    
    #修改目标文件内容
    for commit_info in cur_commit_info_li:
        ret = get_file_info(commit_info)
        #非xml文件直接覆盖
        if ret == 1:
            copy.copy(commit_info[-1], src_dir, des_dir, conf.reply)
        #新增文件直接复制，提交时需先add才能commit
        elif ret == -1:
            #new_add_commit_info.append(commit_info)
            copy.copy(commit_info[-1], src_dir, des_dir, conf.reply)
        #已存在的xml文件先修改再commit
        else:
            file_opt_obj = xml_opt.file_opt(commit_info, src_dir, des_dir, conf.reply)
            file_opt_obj.format_str_list = ret
            file_opt_obj.file_chg()

    if new_add_commit_info:
        #new_add_list = get_file_list(new_add_commit_info)
        add_new_file(des_dir, new_add_commit_info)

    #生成注释文件
    #create_msg(cur_commit_info_li)
    #提交svn
    commit_to_des(des_dir, new_add_commit_info + other_commit_info)
    #更新最后修改日期
    dat.update_stat()
    print u'更新数据文件...'
    #生成注释文件
    #create_msg([conf.code_dat, conf.sit_dat])
    commit_to_des('', [conf.code_dat, conf.sit_dat])
    #cur_svn_ver = commit_to_des(des_dir, des_file_list)
    #print 'cur_svn_ver', cur_svn_ver
    #cur_svn_ver = '123456'
    #except KeyboardInterrupt:
    #    pass
    #except:
    #    print u'未知错误'
    #    exception.fallback(conf.reply)
