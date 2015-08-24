#!/usr/bin/python
# coding=utf-8

import conf
import exception 
import subprocess

#svn操作类型
svn = {
    'update' : 'svn update ',
    'commit' : 'svn commit -F ' + conf.log_file + ' ',
    'lock' : 'svn lock ',
    'unlock' : 'svn unlock ',
    'log' : 'svn log ',
    'info' : 'svn info ',
    'add' : 'svn add ',
    'del' : 'svn delete ',
    'revert' : 'svn revert '
}

class svnError(Exception):
    pass

def svn_opt(opt, files, *msg):
    try:
        #if opt == 'commit':
            #print svn[opt] + msg[0] + files.encode('gb2312')
            #print u'提交信息log, ', msg[0]
            #p = subprocess.Popen(svn[opt] + msg[0] + files.encode('gb2312'), stderr = subprocess.STDOUT)
            #log = os.popen(svn[opt] + msg[0] + files.encode('gb2312'))
        #else:
        p = subprocess.Popen(svn[opt] + files.encode('gb2312'), stderr = subprocess.STDOUT) 
        if p.wait() != 0:
            raise svnError
    except IndexError:
        print svn[opt] + u'缺少message信息'
        exception.fallback(conf.reply)
        #exception.dat_fallback()
        #exception.unlock_dat_file()
        exit(1)

    #except:
    #    print svn[opt] + files.encode('gb2312') + '\nFAILED'
    #    exception.dat_fallback()
    #    exception.unlock_dat_file()
    #    exit(1)
        #log = os.popen(svn[opt] + files.encode('gb2312'))
        #if opt == 'info':
        #    ret_str = log.readlines()
        #    return ret_str
    #print log.read()

#def get_cur_ver(file_list_str):
#    log = svn_opt('info', file_list_str)
#    for line in log:
#        if line.split(':')[0] == 'Last Changed Rev':
#            return line.split(':')[1]

if __name__ == '__main__':
    svn_opt('log', conf.cur_code_dir + 'r.txt') 
