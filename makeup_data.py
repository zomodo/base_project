# Author : zmd
# Date : 2019/11/28 15:51
# Desc : 补全遗漏工商数据

import time
import requests
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor
import pymysql
from urllib import parse
import random
detail_url="https://gongshang.mingluji.com/hubei/name/"

def get_from_mysql():
    connection=pymysql.connect(host='172.16.3.92',port=3306,user='root',password='123456',db='picture',charset='utf8mb4')
    try:
        with connection.cursor() as f:
            sql="select companyName from zh_company  where foundingLocation='None'"
            f.execute(sql)
            allcompany=f.fetchall()
            getrepeat(allcompany)
            connection.commit()
    except:
        connection.close()

def getrepeat(allcompany):
    pool=ThreadPoolExecutor(2)
    for company in allcompany:
        new_url=detail_url+parse.quote(company)
        pool.submit(getdata,new_url)
        time.sleep(random.randint(3,5))
    pool.shutdown(wait=True)

def getdata(url):
    pass



