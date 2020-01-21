# Author : zmd
# Date : 2019/12/18 17:09
# Desc :
import pandas as pd
import numpy as np
import pymysql
import jieba
from PIL import Image
from wordcloud import WordCloud,STOPWORDS
import matplotlib.pyplot as plt
def getword():
    connection=pymysql.connect(host='172.16.3.92',port=3306,user='root',password='123456',db='picture',charset='utf8')
    #sql="select keywordname,sum(consume) from two_hangye where 1_indus='建筑及装修' and 2_indus='{}' group by keywordname order by sum(consume) desc limit 10000".format(indus)
    sql="select keywordname from gui_keywords where 1_department='武汉直销' and 1_indus='旅游服务'"
    data=pd.read_sql(sql,connection)
    #print(data.head())
    connection.close()
    word=data['keywordname']
    allword=list(word)
    allword=' '.join(allword)
    #print(allword)
    cut_word=jieba.cut(allword,cut_all=False)
    string=' '.join(cut_word)
    #print(string)
    getcloud(string)

def getcloud(word):
    font=r'C:\Windows\Fonts\SIMYOU.TTF'
    bg=np.array(Image.open(r'C:\Users\Administrator\Desktop\ti.jpg'))
    stopwords=set(STOPWORDS)
    #stopwords.update(['旅游','武汉','多少','价格'])
    wc=WordCloud(font_path=font,background_color='white',stopwords=stopwords,mask=bg,collocations=False) ##是否包括两个词的搭配
    wc.generate_from_text(word)
    wc.to_file(r'C:\Users\Administrator\Desktop\tour_picture\%s.png' %"wuhan")
    plt.imshow(wc,interpolation='bilinear')
    plt.axis('off')
    plt.show()
    print('行业完成！')

getword()

