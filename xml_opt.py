#!/usr/bin/python
# coding=utf-8

import conf
import sys
import os
import re
import exception
import shutil

#读取文件内容
def get_file_text(path):
    try:
        file_obj = open(path, 'r')
        file_text = file_obj.read()
    except:
        print u'读取文件' + path + u'失败'
        exception.fallback(conf.reply)
        exit(1)
    else:
        return file_text
    finally:
        file_obj.close()

#获取要关键字列表
#def get_key_words(key_words_str):
#    key_word_list = key_words_str.split(':')
#    return key_word_list

class RecNumError(Exception):
    pass

class TextError(Exception):
    pass


#按照关键字符串分割文件
def split_text(file_text, tag_a, *tags):
    #tmp = '\s*' + tag_a
    #rep_tag = re.search(tmp, file_text).group()
    #print rep_tag
    new_file_text = file_text.split(tag_a, 1)
    if tags:
        #pattern = '\s+' + tags[0] 
        #tag_b = re.search(pattern, new_file_text[1]).group().encode('utf-8')
        tag_b = tags[0]
        new_file_text[1:] = new_file_text[1].split(tag_b, 1)
    return new_file_text



#def chg_rec_num(src_file_text, des_file_text, format_str_b):
#    pattern = format_str_b[0] +'"[0-9]*">'
#    src_num_line = re.search(pattern, src_file_text).group()
#    return re.sub(pattern, src_num_line, des_file_text, 1)

class file_opt():
    def __init__(self, commit_info, src_dir, des_dir, reply):
        #要提交的目标文件路径
        self.des_path = des_dir + commit_info[-1]
        #备份要提交的目标文件
        shutil.copy(self.des_path, self.des_path + '.bak')
        #获取要提交内容的文件路径
        if reply == '0':
            self.src_path = src_dir + os.path.basename(commit_info[-1])
        elif reply == '1':
            self.src_path = src_dir + commit_info[-1]
        #操作类型：增加、修改、删除
        self.opt = commit_info[0]
        #要修改的属性名称
        self.key_word_list = commit_info[1]
        #要修改的文件状态
        #self.stat = commit_info
        #关键行内容列表，详见conf.py
        self.format_str_list = ()

    #将关键字组合成分割字符串
    #def get_key_text_list(self, format_str_list):
    #    key_text_list = []
    #    for key_word in self.key_word_list:
    #        key_text = format_str_list[0][0] + key_word.decode('utf-8') + '"'
    #        key_text_list.append(key_text)
    #    return key_text_list

    #获取关键字所在行的完整字符串
    def get_key_text(self, file_text, key_word):
        #pattern = '^\s+<.*' + key_word +".*>"
        pattern = '\s+<.[^<>]*'+ self.format_str_list + '="' + key_word + '.[^<>]*>'
        #print pattern
        #包含关键字的起始标签,不包括结束标签
        tag_text = re.search(pattern, file_text, re.S).group()
        #print tag_text
        tag_name = self.get_tag_name(tag_text)
        new_pattern = pattern + '.*?</' + tag_name + '>'
        key_text = re.search(new_pattern, file_text, re.S).group()
        #print key_text
        return key_text, tag_name
    #获取关键字的标签名
    def get_tag_name(self, tag_str):
        tag_name = tag_str.split(' ')[0].split('<')[-1]
        return tag_name
    
    #替换增加或删除造成的计数变化的行
    def chg_rec_num(self, des_file_text, p_tag_name):
        pattern = '(<' + p_tag_name + '.*)'
        num_line = re.search(pattern, des_file_text).groups()[-1]
        #print num_line
        rec_num = int(num_line.split('"')[1])
        if self.opt == u'增加':
            rec_num += 1
        elif self.opt == u'删除':
            rec_num -= 1

        #确定只有唯一一条匹配，否则抛异常
        count = len(re.findall(num_line, des_file_text))
        if count > 1:
            raise RecNumError

        new_num_line = re.sub('\d+', str(rec_num), num_line, 1)
        des_file_text = re.sub(num_line, new_num_line, des_file_text, 1)
        return des_file_text


    #删除指定属性项
    #def del_from_file(self, src_file_text, des_file_text, key_text_list):
    #    des_text = des_file_text
    #    des_text_list = []
    #    for key_text in key_text_list:
    #        des_text_list = split_text(des_text, key_text.encode('utf-8'), self.format_str_list[0][1])
    #        del des_text_list[1]
    #        #[:-2]去掉因分割产生的多余换行符
    #        des_text = des_text_list[0][:-2] + self.format_str_list[0][1].join(des_text_list[1:])
    #    #替换计数行
    #    des_text = chg_rec_num(src_file_text, des_text, self.format_str_list[1])
    #    return des_text

    #删除指定属性项
    def del_from_file(self, des_file_text, key_text, tag_name):
        #若父级标签规律不一致可改用字典来对应
        p_tag_name = tag_name + 'Tab'
        des_text_list = split_text(des_file_text, key_text)

        des_text_list[0] = self.chg_rec_num(des_text_list[0], p_tag_name)

        des_file_text = ''.join(des_text_list)
        #print des_file_text
        
        #del des_text_list[1]
        #des_file_text = des_text_list[0] + self.format_str_list[0][1].join(des_text_list[1:])
        return des_file_text

    #添加指定属性项
    #def insert_to_file(self, src_file_text, des_file_text, key_text_list):
    #    des_text = des_file_text
    #    for key_text in key_text_list:
    #        tmp_src_text_list = split_text(src_file_text, key_text.encode('utf-8'), self.format_str_list[0][1])
    #        src_text = key_text.encode('utf-8') + tmp_src_text_list[1] + self.format_str_list[0][1]
    #        #print src_text
    #        tmp_des_text_list = split_text(des_text, self.format_str_list[1][1])
    #        print tmp_des_text_list
    #        #不严谨需要修改
    #        des_text = tmp_des_text_list[0] + src_text + self.format_str_list[1][1]

    #    #替换计数行
    #    des_text = chg_rec_num(src_file_text, des_text, self.format_str_list[1])
    #    return des_text

    #添加指定属性项
    def add_to_file(self, des_file_text, key_text, tag_name):
        des_text = des_file_text
        #print des_text
        #若父级标签规律不一致可改用字典来对应
        p_tag_name = tag_name + 'Tab'
        #print u'增加, ', p_tag_name
        #若有多个相同标签则暂时无法处理，抛异常
        pattern = re.compile('\s+</' + p_tag_name + '>\s*')
        count = len(pattern.findall(des_text))
        if count > 1:
            print u'多个相同标签暂时无法处理'
            raise TextError

        try:
            p_end_tag = pattern.search(des_text).group()
        except:
            print u'增加时未搜索到结束标签'
            raise Exception
        tmp_des_text_list = split_text(des_text, p_end_tag)
        tmp_des_text_list[0] = self.chg_rec_num(tmp_des_text_list[0], p_tag_name)
        #print tmp_des_text_list[0]
        des_text = tmp_des_text_list[0] + key_text + tmp_des_text_list[1] + p_end_tag
        #print des_text

        return des_text
           
    #修改指定属性项
    def rep_file(self, des_file_text, des_key_text, src_key_text):
        #aaa = open('bbb.xml', 'w+b')
        #aaa.write(des_key_text)
        #des_text = re.sub(des_key_text, src_key_text, des_file_text, re.S)
        des_text = des_file_text.replace(des_key_text, src_key_text)
        #aaa = open('ccc.xml','w+b')
        #aaa.write(des_text)
        #print des_text
        return des_text

    #文件修改
    def text_opt(self, src_file_text, des_file_text, key_word_list):
        des_text = des_file_text
        if self.opt == u'增加':
            for key_word in key_word_list:
                print u'当前处理：%s' % key_word
                key_text, tag_name = self.get_key_text(src_file_text, key_word)
                try:
                    self.get_key_text(des_file_text, key_word)
                except:
                    pass
                else:
                    print u'目标文件中已存在"%s"' % key_word
                    exception.file_fallback(self.des_path)
                    exception.fallback(conf.reply)
                    sys.exit(1)
                des_text = self.add_to_file(des_text, key_text, tag_name)
                print u'增加%s成功' % key_word
            #替换计数行
            #des_text = self.chg_rec_num(src_file_text, des_text, self.format_str_list[1])
        elif self.opt == u'删除':
            for key_word in key_word_list:
                print u'当前处理：%s' % key_word
                key_text, tag_name = self.get_key_text(des_file_text, key_word)
                des_text = self.del_from_file(des_text, key_text, tag_name)
            #替换计数行
            #des_text = chg_rec_num(src_file_text, des_text, self.format_str_list[1])
        elif self.opt == u'修改':
            for key_word in key_word_list:
                print u'当前处理：%s' % key_word
                src_key_text = self.get_key_text(src_file_text, key_word)[0]
                des_key_text = self.get_key_text(des_file_text, key_word)[0]
                des_text = self.rep_file(des_text, des_key_text, src_key_text)
        else:
            print u'选项设置错误，请检查'
            exit(1)
        return des_text

    #文件修改顶层逻辑
    def file_chg(self):
        des_file_text = get_file_text(self.des_path)
        src_file_text = get_file_text(self.src_path)
        #key_text_list = self.get_key_text_list(self.format_str_list)

        try:
            new_text =  self.text_opt(src_file_text, des_file_text, self.key_word_list)
        except RecNumError:
            print u'计数行有多个相同项无法处理'
            exception.file_fallback(self.des_path)
            exception.fallback(conf.reply)
            #exception.dat_fallback()
            #exception.unlock_dat_file()
            exit(1)
        except TextError:
            print u'有多个相同标签，无法处理'
            exception.file_fallback(self.des_path)
            exception.fallback(conf.reply)
            #exception.dat_fallback()
            #exception.unlock_dat_file()
            exit(1)
        except:
            print self.des_path + u' 操作失败，请检查确认操作内容是否填写错误'
            exception.file_fallback(self.des_path)
            exception.fallback(conf.reply)
            #exception.dat_fallback()
            #exception.unlock_dat_file()
            exit(1)
        else:
            #写入新文件
            new_des_file_obj = open(self.des_path, 'w+b')
            try:
                new_des_file_obj.write(new_text)
            except:
                print u'写入新文件\n' + self.des_path + u'失败'
                exception.file_fallback(self.des_path)
                exception.fallback(conf.reply)
                #exception.dat_fallback()
                #exception.unlock_dat_file()
                exit(1)
            finally:
                new_des_file_obj.close()
                #os.remove(self.des_path + '.bak')

if __name__ == '__main__':
    #file_text = get_file_text('src/')
    #src_xls = excel.xl_rd('test1.xlsx')
    #commit_info = src_xls.get_commit_info()
    #map(lambda x: x.reverse(), commit_info)
    #print commit_info
    #commit_info = [u'删除', [u'FLOW_JUDGE_ACCT'], u'Flow.xml']
    #commit_info = [u'增加', [u'EMU_path_5', u'EMU_path_6'], u'DataElement.xml']
    commit_info = [u'修改', [u'FMT_CRDL033_BODY_OUT'], u'Format.xml']

    file = file_opt(commit_info, conf.cur_src_dir, conf.cur_code_dir + 'etc\COMM\EMU_XML_SVR\\')
    #file.format_str_list = conf.format_str_dict['DataElement']
    file.file_chg()
