#!/usr/bin/python
# coding=utf-8

import datetime
import json
import exception
import conf

class jsonProcess:
    def __init__(self, path):
        self.des_path = path
        f = open(path, 'a+b')
        try:
            self.file_list = json.load(f)
            self.len = len(self.file_list)
            self.pos_li = self.file_list[-1]
        except:
            print u'数据文件为空'
            self.file_list = []
            self.len = 0
            self.pos_li = []
        finally:
            f.close()
        self.cur_pos_li = []
        
    #写入新增的文件列表
    def add_file(self, new_file_list, data_path):
        #将列表转换为字典
        #将原始key_words转换为列表
        new_li = list(map(self.li_to_dict, new_file_list))
        #初始化所有未提交的key_word下标
        pos_li = self.rec_idx(new_li)
        #为新增文件添加时间戳
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for file_info in new_li:
            file_info['author'] = conf.author
            file_info['last_update'] = now

        #删除并替换原记录坐标列表,加入新增的文件列表
        try:
            self.file_list[-1:] = new_li
            pos_li += self.pos_li
            self.file_list.append(sorted(pos_li))
        except:
            print u'列表为空'
            self.file_list = new_li
            self.file_list.append(sorted(pos_li))

        #print 'self.file_list, ', self.file_list

        #转换为json格式的数据
        #print json.dumps(self.file_list, indent = 2)
        #print json.dumps(self.file_list, indent = True)
        #写入新文件
        fp = open(data_path, 'w+b')
        try:
            json.dump(self.file_list, fp, indent = 2)
        except:
            print u'写入数据文件失败'
            exception.fallback(conf.reply)
            #exception.dat_fallback()
            #exception.unlock_dat_file()
            exit(1)
        finally:
            fp.close()

    #将列表转换为字典
    def li_to_dict(self, val_list):
        #print 'val_list, ', val_list
        key_list = ['file_path', 'opt', 'key_words']
        try:
            val_list[2] = val_list[2].split(':')
        except:
            pass
        #print dict(zip(key_list, val_list))
        return dict(zip(key_list, val_list))

    #添加时间戳,可根据此键值做查询7天内提交历史查询
    def add_ts(self, now, file_list):
        for file_info in file_list:
            file_info['last_update'] = now

    #初始化所有未提交的key_word下标到最后一个list中,只在初始化时进行一次操作
    def rec_idx(self, file_list):
        #若初始化时文件为空，与非空时相比多了最后记录坐标的列表，长度需要减1
        file_len = self.len - 1 if self.len else self.len 
        #file_len = self.len
        file_x = range(file_len, file_len + len(file_list))
        key_word_y = map(lambda y: range(len(y['key_words'])), file_list)
        #pos_li = sorted(list(map(lambda x, y: [x, y], file_x, key_word_y)))
        pos_li = []
        for idx, x in enumerate(file_x):
            li_x = [x for i in key_word_y[idx]]
            pos_li += zip(li_x, key_word_y[idx])
        #print u'未提交文件坐标: ', pos_li
        return pos_li



    #显示未提交的文件内容列表
    def show_list(self, ):
        pos_li = self.file_list[-1]
        #new_pos_li = map(self.chg_pos, pos_li)
        #new_pos_li = self.chg_pos(pos_li)
        #print new_pos_li
        print u'尚未提交的内容列表(单项以"x.x"格式、空格为分隔符进行提交，全部提交时可输入"all"):'
        try:
            self.print_list(pos_li)
        except:
            exception.fallback(conf.reply)
            exit(1)
        #for idx, pos in enumerate(new_pos_li):
        #    if self.file_list[pos[0]]['key_words'][pos[1]]: 
        #        print idx, self.file_list[pos[0]]['file_path'], self.file_list[pos[0]]['key_words'][pos[1]] 
        #    else:
        #        print idx, self.file_list[pos[0]]['file_path'] 
        #des_pos_li = self.get_input(pos_li)

    #打印列表
    def print_list(self, pos_li):
        #print pos_li
        for idx_x, pos in enumerate(pos_li):
            if self.file_list[int(pos[0])]['author'] == conf.author:
                print pos[0], self.file_list[int(pos[0])]['file_path'] 
                if self.file_list[pos[0]]['key_words'][pos[1]]:
                    print '  ', pos[1], self.file_list[int(pos[0])]['key_words'][pos[1]], u'(%s)' % conf.author
                else:
                    print u'    (本条请输入%s.0)' % pos[0]
            #try:
            #    for idx_y in pos[1]:
            #        if self.file_list[pos[0]]['key_words'][idx_y]:
            #            print '  ', idx_y, self.file_list[pos[0]]['key_words'][idx_y]
            #except:
            #    continue

    #改变坐标显示方式
    #def chg_pos(self, pos_li):
    #    new_pos_li = []
    #    for pos in pos_li:
    #        li_x = [pos[0] for i in pos[1]]
    #        new_pos_li += (lambda x, y: zip(x, y))(li_x, pos[1])
    #    return new_pos_li

    #获取当前作者所有提交坐标
    def get_cur_author_all(self, pos_li):
        cur_author_pos = []
        for idx_x, pos in enumerate(pos_li):
            if self.file_list[int(pos[0])]['author'] == conf.author:
                cur_author_pos.append(pos)
        return cur_author_pos

    #获取输入
    def get_input(self, ):
        pos_li = self.file_list[-1]
        print u'请选择要提交的内容序号:'
        idx_str = raw_input()
        idx_li = idx_str.split(' ')
        #all表示全部提交
        if 'all' in idx_li or 'ALL' in idx_li:
            des_pos_li = self.get_cur_author_all(pos_li)
        #elif '-' in idx_li:
        #    print 'OK'
        else:
            des_pos_li = list(map(lambda idx: idx.split('.'), idx_li))
        print 'des_pos_li, ', sorted(des_pos_li)

        #des_file_li = map(lambda pos: self.file_list[int(pos[0])].values()[:-1], des_pos_li)
        #print des_file_li

        self.cur_pos_li = sorted(des_pos_li)

    #将同一文件下待提交的key_word坐标进行合并,即改变坐标的表示方式便于后续操作
    def merge_pos(self, ):
        des_pos_li = self.cur_pos_li
        new_pos_li = []
        count = 0
        for x, des_pos in enumerate(des_pos_li):
            file_idx_cur = des_pos[0]
            try:
                file_idx_next = des_pos_li[x+1][0]
            except:
                new_pos_li.append(des_pos_li[x-count:])
                continue
            #print count, x, file_idx_cur, file_idx_next

            if file_idx_cur == file_idx_next:
                count += 1
                continue
            else:
                new_pos_li.append(des_pos_li[x-count:x+1])
                count = 0
        return new_pos_li
    #根据选定的坐标列表提取内容
    def get_commit_info(self, ):
        pos_li = self.file_list[-1]
        self.get_input()
        des_pos_li = self.merge_pos()
        commit_info_li = []
        for pos in des_pos_li:
            #cur_info = self.file_list[pos_li[int(pos[0][0])][0]].values()
            cur_info = self.file_list[int(pos[0][0])].copy()
            #print 'cur_info, ', cur_info
            key_word_list = []
            try:
                for key_word in pos:
                    key_word_list.append(cur_info['key_words'][int(key_word[1])])
                cur_info['key_words'] = key_word_list
            except IndexError:
                cur_info['key_words'] = []
            commit_info_li.append(cur_info)

        #print u'返回的列表', map(lambda commit_info: commit_info.values(), commit_info_li)
        return map(lambda commit_info: commit_info.values(), commit_info_li)

    #更新提交内容的最后修改时间, 并删除已提交坐标
    def update_stat(self, ):
        #更新最后修改时间
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        pos_li = self.file_list[-1]
        des_pos_li = self.merge_pos()
        for pos in des_pos_li:
            cur_info = self.file_list[int(pos[0][0])]
            cur_info['last_update'] = now
        
        #删除已提交的坐标
        try:
            #print des_pos_li
            for des_pos in des_pos_li:
                for pos in des_pos:
                    pos = map(lambda x: int(x), pos)
                    pos_li.remove(pos)
        except:
            print u'删除已提交的坐标出错'
            exception.fallback(conf.reply)
            #exception.dat_fallback()
            #exception.unlock_dat_file()
            exit(1)

        #print self.file_list
        file_obj = open(self.des_path, 'w+b')
        try:
            json.dump(self.file_list, file_obj, indent = 2)
        except:
            print u'更新数据文件失败'
            exception.fallback(conf.reply)
            #exception.dat_fallback()
            #exception.unlock_dat_file()
            exit(1)

        finally:
            file_obj.close()

    #显示提交历史记录
    #reply = (2,3)
    #2为3天； 3为7天
    def show_history(self, reply):
        pass


if __name__ == '__main__':
    new_file_list = [['aaa', 'a:b:c:d', u'增加'], ['bbb.c', '', u'修改'], ['ccc', 'a:b:c:d', u'删除']]
    test = jsonProcess('test.json')
    #test.li_to_dict(new_file_list[0])
    test.add_file(new_file_list, 'test.json')
    test.show_list()
    test.get_commit_info()
    #test.update_stat()
