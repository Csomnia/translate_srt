#-*- coding:utf-8 -*-
import threading
import urllib2
import bs4
import re
import sys  
reload(sys)
sys.setdefaultencoding('utf-8')


class getWord:
    def __init__(self, srt_file, dict_file):
        self.srt_file = srt_file
        dict_book = open(dict_file, 'r')
        dict_list = []
        for line in dict_book.xreadlines():
            cur_line = line.split()
            if len(cur_line) >= 2:
                dict_list.append(cur_line[0])
        self.dict_set = set(dict_list)

    def get_word(self):
        """
        get words in srt file.
        """
        srt = open(self.srt_file, 'r+')
        jump_mark = 0
        queryed_words = []
        start_mark = False

        replace_dict = {}
        unknow_words = []
        for line_number, line in enumerate(srt.readlines()):
            if '-->' in  line:
                start_mark = True
                continue
            elif not line.split():
                start_mark = False
                continue
            #print("now in line:", line_number," line: ", line)

            if start_mark:
                # in words line
                line_unknow_words = []
                for word in line.split():
                    formated_word = self._word_format(word)

                    if formated_word not in unknow_words:
                        # word not in unkown_words list
                        if formated_word in queryed_words:
                            # we know the word
                            continue
                        elif not self._word_filter(formated_word):
                            # qerery this word and we unknow it
                            unknow_words.append(formated_word)
                            queryed_words.append(formated_word)
                            line_unknow_words.append(word)
                        else:
                            # know it
                            queryed_words.append(formated_word)
                    else:
                        line_unknow_words.append(word)
                if line_unknow_words:
                    replace_dict[line_number] = line_unknow_words

        print("replace_dict: !", replace_dict)
        print("unknow_words: !", unknow_words)
        self.replace_dict = replace_dict
        srt.close()
        return unknow_words
    
    def _word_format(self, word):
        abc = 'abcdefghijklmnopqrstuvwxyz'
        word = word.lower()
        while word[-1] not in abc and len(word) > 1:
            word = word[:-1]
        if '.' in word:
            word = ''.join(word.split('.'))
        return word
        
    
    def _word_filter(self, word):
        """
        return true: if the word in dict set.
        """
        if "'" in word or len(word) <= 2:
            return True
        
        word = word.lower()
        if word[-1:] == 's':
            return (word in self.dict_set or
                    word[:-1] in self.dict_set or
                    word[:-2] in self.dict_set)
        elif word[-2:] == 'ed':
            return (word in self.dict_set or
                    word[:-1] in self.dict_set or
                    word[:-2] in self.dict_set or
                    word[:-3]+'y' in self.dict_set)
        elif word[-3:] == 'ing':
            return (word in self.dict_set or
                    word[:-3] in self.dict_set or
                    word[:-3]+'e' in self.dict_set or
                    word[:-4] in self.dict_set)
        else:
            return (word in self.dict_set)

    def word_replacement(self, translated_dict):
        """
        replaces unknown word.
        """
        abc = 'abcdefghijklmnopqrstuvwxyz'
        srt = open(self.srt_file, 'r')
        trans_srt = open("trans_"+self.srt_file, 'w')
        start_mark = False
        for line_number, line in enumerate(srt.readlines()):
            if '-->' in  line:
                start_mark = True
                trans_srt.writelines(line)
                continue
            elif not line.split():
                start_mark = False
                trans_srt.writelines(line)
                continue
            if start_mark:
                if self.replace_dict.has_key(line_number):
                    for word in self.replace_dict[line_number]:
                        trans = translated_dict.get(self._word_format(word))
                        format_trans = u"<font color='red'>" + word + u"(" + trans + u")" + u"</font>"
                        line = line.replace(word, format_trans)
                        print(line)
            trans_srt.write(line)
                
    # def get_unkonw_words(self):
    #     """
    #     filter words that probably unknown
    #     """
    #     pass

DICT_URL = 'http://dict.youdao.com/w/'
class subDictProcess:
    def __init__(self, selected_field, word):
        #threading.Thread.__init__(self)
        self.field = u'计算机科学技术' if selected_field == 0 else None
        self.word = word

    def get_translated_word(self):
        """
        get tanslated text that in selected field
        """
        translation = ''
        req = urllib2.Request(DICT_URL + self.word)
        respone = urllib2.urlopen(req)
        html = respone.read()
        soup = bs4.BeautifulSoup(html, "html.parser")
        
        plist = soup.html.body.find_all(class_="p-type")
        for i in plist:
            if i.string == self.field:
                marker = i['rel']
                try:
                    pTrans = soup.html.body.find(id='tPETrans').find(class_=marker).find('span').string.strip()
                except AttributeError:
                    pTrans = ""
                #print(u'专业释意: ' + pTrans)
                translation = pTrans
        if not translation:
            try:
                webTrans = soup.html.body.find(class_="wt-container").find("span").string.strip()
            except AttributeError:
                webTrans = ""
            #print(u'网络释意： ' + webTrans)
            translation = webTrans
        return translation if translation else u"找不到解释"

    def run(self):
        """
        start thread.
        """
        pass


class unknowWords:
    def __init__(self, unknow_words):
        pass

    def search_words(self):
        pass


if __name__ == '__main__':
    test = getWord('example.srt', '4ji.txt')
    tans = {}
    for word in test.get_word():
        test1 = subDictProcess(0, word)
        tans[word] = test1.get_translated_word()
        
    #test.word_replacement(tans)
    # test1 =subDictProcess(0, 'softwares')
    # test1.get_translated_word()
    
