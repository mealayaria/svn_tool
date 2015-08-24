#!encoding=utf-8
import shutil
import exception
import os

def copy(file, src_dir, des_dir, reply):
    if reply == '1':
        src_file = src_dir + file
    elif reply == '0':
        src_file = src_dir + os.path.basename(file)
    des_file = des_dir + file
    try:
        shutil.copy(src_file, des_file)
        #print 'copy ' + src_file + ' to ' + des_file 
    except:
        print 'copy ' + src_file + ' to ' + des_file + " FAILED"
        exception.fallback(reply)
        exit(1)

if __name__ == '__main__':
    copy('a.txt', 'aaa', 'bbb')
