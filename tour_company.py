# Author : zmd
# Date : 2019/12/17 17:13
# Desc :
import pandas as pd
import numpy as np
import pymysql
import jieba
import jieba.analyse
from PIL import Image
import csv
from wordcloud import WordCloud,STOPWORDS
import matplotlib.pyplot as plt
from collections import Counter

#创建搜索词处理类
class keyword:
    def __init__(self):
        self.writer=pd.ExcelWriter(r"C:\Users\Administrator\Desktop\tour_company.xlsx") # 写入Excel表路径，全局变量，需关闭

    # 主函数
    def getmain(self):
        sql_last="select keywordname from keywords_last where consume>0"
        sql_this="select keywordname from keywords_this where consume>0"
        data_last=self.get_data(sql_last)
        data_this=self.get_data(sql_this)
        cut_word_last=self.get_cutword(data_last)
        cut_word_this=self.get_cutword(data_this)
        hand_result=self.get_differ(cut_word_last,cut_word_this)    # 区分相同词和不同词
        process_same=self.get_same_word(hand_result[0],hand_result[1],hand_result[2],hand_result[3],hand_result[4])
        process_unsame=self.get_unsame_word(hand_result[5],cut_word_this)
        self.getwordcloud(process_same,'关键词-增长词-切词')          # 绘制词云-相同词-切词
        self.getwordcloud(process_unsame[0],'关键词-新增词-切词')     # 绘制词云-不同词-切词
        unsame_word_more=self.get_word_more(process_unsame[1])      # 把新增词的切词进行拓词
        self.getwordcloud(unsame_word_more,'关键词-新增词-拓展词',collocat=True)    # 绘制词云-不同词-拓展词
        self.writer.close() # 关闭Excel表


    #从数据库提取原始数据，并转化成列表形式
    def get_data(self,sql):
        connect_get_data=pymysql.connect(host='172.16.3.92',user='root',password='123456',port=3306,db='picture',charset='utf8mb4')
        try:
            with connect_get_data.cursor() as f:
                f.execute(sql)
                all_data=f.fetchall()
                connect_get_data.commit()
        finally:
            connect_get_data.close()

        all_data=[i[0] for i in all_data]
        return all_data

    #数据传进来进行jieba分词,统计各词出现的频次
    def get_cutword(self,word):
        cnt = Counter()
        word=' '.join(word)
        cut_word=jieba.cut(word,cut_all=False)
        for i in cut_word:
            cnt[i] +=1

        return cnt

    #切词完了之后，筛选两个时间段的相同词和不同词
    def get_differ(self,word_last,word_this):
        same_word=[]
        unsame_word=[]
        freq_last=[]
        freq_this=[]
        all_cha=[]
        all_ratio=[]
        for w in word_this.keys():
            if w in word_last.keys():   # 相同词
                cha=word_this[w]-word_last[w]   # 计算差值
                ratio=word_this[w]/word_last[w] # 计算比率
                same_word.append(w)
                freq_last.append(word_last[w])
                freq_this.append(word_this[w])
                all_cha.append(cha)
                all_ratio.append(ratio)

            else:         # 不同词，导入列表进行后续处理
                unsame_word.append(w)

        return same_word,freq_last,freq_this,all_cha,all_ratio,unsame_word

    # 处理相同的词
    def get_same_word(self,same_word,freq_last,freq_this,all_cha,all_ratio):
        dict_data={'same_word':same_word,'freq_last':freq_last,'freq_this':freq_this,'all_cha':all_cha,'all_ratio':all_ratio}
        my_data=pd.DataFrame(dict_data)
        my_data.to_excel(self.writer,sheet_name='增长词')  # 存入Excel表中
        my_data_process=my_data[(my_data['all_ratio']>=1)&(my_data['freq_this']>=500)]
        # 增长词的切词做词云
        word_cloud=[]
        for i,v in my_data_process.iterrows():
            word=(v['same_word']+',')*v['freq_this']
            word_cloud.append(word)
        word_cloud=''.join(word_cloud)

        return word_cloud

    # 处理不同的词
    def get_unsame_word(self,unsame_word,cut_word_this):
        all_unsame_word=[]
        all_freq=[]
        for i in unsame_word:
            all_unsame_word.append(i)
            all_freq.append(cut_word_this[i])
        dict_data={'unsame_word':all_unsame_word,'time':all_freq}
        my_data=pd.DataFrame(dict_data)
        my_data=my_data.sort_values(by='time',ascending=False)      #    按照time字段做降序排列
        my_data.to_excel(self.writer,sheet_name='新增词')  # 存入Excel表中
        my_data_process=my_data[my_data['time']>=10]
        # 新增词的切词做词云
        word_cloud=[]
        for n,k in my_data_process.iterrows():
            cut_word_one=(k['unsame_word']+',')*k['time']
            word_cloud.append(cut_word_one)
        word_cloud=''.join(word_cloud)

        # 新增词 先拓词 再做词云
        unsame_word_more=list(my_data_process['unsame_word'])

        return word_cloud,unsame_word_more

    # 将不同词进行拓词的函数
    def get_word_more(self,cut_word):
        new_word_more=[]
        connect_sel_data = pymysql.connect(host='172.16.3.92', user='root', password='123456', port=3306, db='picture',charset='utf8mb4')
        try:
            with connect_sel_data.cursor() as f:
                for i in cut_word:
                    if len(i)>1:
                        sql="select keywordname from keywords_this where keywordname like '%{}%' and consume>0".format(i)
                        f.execute(sql)
                        connect_sel_data.commit()
                        all_data=f.fetchall()
                        for new_word in all_data:
                            new_word_more.append(new_word[0])
        finally:
            connect_sel_data.close()

        new_word_more=' '.join(new_word_more)
        cut_word_more=jieba.cut(new_word_more,cut_all=False)
        cut_word_more=' '.join(cut_word_more)

        return cut_word_more


    # 绘制词云的函数
    def getwordcloud(self,word,pic_name,collocat=False):
        font=r"C:\Windows\Fonts\SIMYOU.TTF"   # 导入中文字体
        bg=np.array(Image.open(r"C:\Users\Administrator\Desktop\ti.jpg")) # 导入背景图片
        stopwords=set(STOPWORDS)
        stopwords.update(['如何','怎么办','怎样','价格','什么','多少','怎么','培训','公司','学校'])
        wc=WordCloud(font_path=font,background_color='white',stopwords=stopwords,mask=bg,collocations=collocat)
        wc.generate(word)
        wc.to_file(r"C:\Users\Administrator\Desktop\%s.jpg" %pic_name)
        plt.imshow(wc,interpolation='bilinear')
        plt.axis('off')
        plt.show()


begin=keyword()
begin.getmain()
