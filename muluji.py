# Author:zmd
# Date:2019/8/22 15:10
# desc:
import requests
import time
from lxml import etree
from fake_useragent import UserAgent
from urllib import parse
import json
import random
from concurrent.futures import ThreadPoolExecutor
import pymysql
import datetime

class muluji:
    def __init__(self):
        self.detail_url="https://gongshang.mingluji.com/hubei/name/"

    def getpage(self,date,page=0):
        allName=[]
        head={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Host": "gongshang.mingluji.com",
            "Referer": "https://gongshang.mingluji.com/hubei/riqi",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent":UserAgent().random,
        }

        if page==0:
            new_head=head
            begin_url='https://gongshang.mingluji.com/hubei/riqi/{}'.format(date)

        elif page==1:
            head["Referer"]="https://gongshang.mingluji.com/hubei/riqi/{}".format(date)
            new_head=head
            begin_url='https://gongshang.mingluji.com/hubei/riqi/{}?page={}'.format(date,page)

        else:
            head["Referer"]="https://gongshang.mingluji.com/hubei/riqi/{}?page={}".format(date,page-1)
            new_head=head
            begin_url='https://gongshang.mingluji.com/hubei/riqi/{}?page={}'.format(date,page)

        try:
            req=requests.get(begin_url,headers=new_head)
            # req.raise_for_status()        # requests请求不能捕获403异常，这里加上raise_for_status()可判断status_code是否正常
            if req.status_code==404:        # 404错误是，还没有当前链接，没有当前数据
                print('---%s号没有当前页数：%s' % (date, begin_url))
                time.sleep(random.randint(2, 3))
            else:
                req.raise_for_status()          # requests请求不能捕获403异常，这里加上raise_for_status()可判断status_code是否正常

        except Exception as e:
            print('---%s号的第%s页访问失败---' %(date,page),e)
            time.sleep(random.randint(40,60))           # 由于网络问题无法解析，需等待五秒，回调重新解析
            self.getpage(date,page)

        else:
            tree=etree.HTML(req.text)
            companyNames=tree.xpath(r"//table[@class='views-table cols-2']/tbody/tr")
            for name in companyNames:
                companyName=name.xpath(r"./td[1]/a/text()")

                # 临时块
                # keyword='合作社'
                # if keyword in companyName[0]:
                #     allName.append(companyName[0])
                # else:
                #     pass

                allName.append(companyName[0])
            print("%s号-第%s页-%s条数据--" %(date,page,len(allName)),allName)

            # 开启多线程，但是要限速，并没有什么用
            pool=ThreadPoolExecutor(2)
            for company in allName:
                new_url = self.detail_url + parse.quote(company)
                pool.submit(self.getprocess,new_url,date,page)
                time.sleep(random.randint(3,5))
            pool.shutdown(wait=True)

            # for company in allName:
            #     new_url = self.detail_url + parse.quote(company)
            #     self.getprocess(new_url)
            #     time.sleep(random.randint(4,6))

            if tree.xpath(r"//li[@class='pager-next last']/a"):
                page +=1
                time.sleep(random.randint(2,3))  # 翻页的时候停顿几秒
                self.getpage(date,page)

            elif len(allName)==0:
                print("-- %s号没有数据！" %(date))

            else:
                print("-- %s号共有%s页数据！" %(date,page+1))

    # def getdata(self,data):
    #     pool=ThreadPoolExecutor()
    #     for company in data:
    #         new_url=self.detail_url+parse.quote(company)
    #         pool.submit(self.getprocess,new_url)
    #         time.sleep(2)
    #     pool.shutdown(wait=True)

    def getprocess(self,url,date,page):
        head={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Host": "gongshang.mingluji.com",
            "Referer": "https://gongshang.mingluji.com/hubei/riqi/{}".format(date),
            "Upgrade-Insecure-Requests": "1",
            "User-Agent":UserAgent().random,
        }
        # head={"User-Agent":UserAgent().random}

        if page==0:
            new_head=head
        else:
            head['Referer']="https://gongshang.mingluji.com/hubei/riqi/{}?page={}".format(date,page)
            new_head=head

        try:
            req=requests.get(url,headers=new_head)
            # req.raise_for_status()      # requests请求不能捕获403异常，这里加上raise_for_status()可判断status_code是否正常
            if req.status_code==404:        # 404错误是，还没有当前链接，没有当前数据
                print('页面未找到：%s' %url)
                time.sleep(random.randint(2, 3))
            else:
                req.raise_for_status()          # requests请求不能捕获403异常，这里加上raise_for_status()可判断status_code是否正常

        except Exception as e:      # 访问过快可能导致请求异常，这里选择抛出异常，等待五秒后再次访问
            print('页面访问失败:%s' %e)
            time.sleep(random.randint(40,60))
            self.getprocess(url,date,page)

        else:
            tree=etree.HTML(req.text)
            #获取指标数据
            name=tree.xpath(r"//span[@class='field-item']/span[@itemprop='name']/text()")[0]
            address=tree.xpath(r"//span[@class='field-item']/span[@itemprop='address']/text()")[0]
            identifier=tree.xpath(r"//span[@class='field-item']/span[@itemprop='identifier']/a/text()")[0]
            foundingDate=tree.xpath(r"//span[@class='field-item']/span[@itemprop='foundingDate']/a/text()")[0]
            makesOffer=tree.xpath(r"//span[@class='field-item']/span[@itemprop='makesOffer']/text()")[0]
            founder = tree.xpath(r"//span[@class='field-item']/span[@itemprop='founder']/a/text()")[0]

            try:
                if tree.xpath(r"//li[7]/span[@class='field-label']/text()")[0]=='注册资金':
                    registerMoney = tree.xpath(r"//li[7]/span[@class='field-item']/text()")[0]
                elif tree.xpath(r"//li[8]/span[@class='field-label']/text()")[0]=='注册资金':
                    registerMoney = tree.xpath(r"//li[8]/span[@class='field-item']/text()")[0]
                else:
                    registerMoney = None
            except:
                registerMoney = None

            #registerMoney = tree.xpath(r"//li[7]/span[@class='field-item']/text()")[0] if tree.xpath(r"//li[7]/span[@class='field-label']/text()")[0]=='注册资金' else None
            foundingLocation=tree.xpath(r"//span[@class='field-item']/span[@itemprop='foundingLocation']/a/text()")[0] if tree.xpath(r"//span[@itemprop='foundingLocation']") else None
            companyType = tree.xpath(r"//span[@class='field-item']/span[@itemprop='']/text()")[0] if tree.xpath(r"//span[@class='field-item']/span[@itemprop='']") else None
            companyStatus = tree.xpath(r"//span[@class='field-item']/span[@itemprop='company_status']/text()")[0] if tree.xpath(r"//span[@itemprop='company_status']") else None

            data=[name,identifier,foundingDate,foundingLocation,founder,registerMoney,address,companyType,companyStatus,makesOffer]
            # print(data)
            self.getsave(data)


    def getsave(self,data):
        connection = pymysql.connect(host='172.16.3.92', port=3306, user='root', password='123456', db='picture',charset='utf8mb4')
        try:
            with connection.cursor() as w:
                sql="replace into zh_company values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" %(data[0],data[1],data[2],data[3],data[4],data[5],data[6],data[7],data[8],data[9])
                w.execute(sql)
                connection.commit()

        finally:
            connection.close()


    def main(self,begin_date,page=0):
        # self.getpage(begin_date)
        now=datetime.date.today()   #当前日期
        str_now=now.strftime(r'%Y-%m-%d')   #将当前日期转化成字符串格式，后面进行比较
        one_day=datetime.timedelta(days=1)  #设置间隔天数 1天
        dt_begin_date=datetime.datetime.strptime(begin_date,r"%Y-%m-%d")    #传入的begin_date为字符串格式，将他转化成日期格式

        if str_now>=begin_date:    # 字符串格式进行比较
            print('---正在处理%s号数据---' %begin_date)
            self.getpage(begin_date,page)

            dt_begin_date +=one_day     # 用日期格式进行加减日期天数
            next_date=dt_begin_date.strftime(r'%Y-%m-%d')   #再将日期格式转化成字符串格式，带入回调函数

            self.main(next_date)

        else:
            end_date=dt_begin_date-one_day
            end_date=end_date.strftime(r"%Y-%m-%d")
            print('数据截止到%s号！' %end_date)


muluji=muluji()
muluji.main('2020-01-10')