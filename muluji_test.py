# Author:zmd
# Date:2019/8/22 9:22
# desc:
import requests
import time
from lxml import etree
from fake_useragent import UserAgent
from urllib import parse
import json

head={"User-Agent":UserAgent().random}
d_url="https://gongshang.mingluji.com/hubei/name/"


def getproxy(url):
    api_url='http://127.0.0.1:8000/api'
    req=requests.get(api_url)
    ip=json.loads(req.text)
    try:
        response=requests.get(url,headers=head,proxies=ip,timeout=10)
        if response.status_code==200:
            print("success",ip)
            return response
        else:
            print("error",ip)
            getproxy(url)
    except:
        print("error",ip)
        getproxy(url)

def getpage():
    all=[]
    for page in range(1):
        url='https://gongshang.mingluji.com/hubei/riqi/2019-08-19?page={}'.format(page)
        req=requests.get(url,headers=head)
        tree=etree.HTML(req.text)
        title=tree.xpath(r"//table[@class='views-table cols-2']/tbody/tr")
        for i in title:
            all.append(i)
    getde(all)

def getde(all):

    for i in all:
        t=i.xpath(r"./td[1]/a/text()")[0]
        new_url=d_url+parse.quote(t)
        res=getproxy(new_url)
        te=etree.HTML(res.text)
        # html=requests.get(new_url,headers=head)
        # te=etree.HTML(html.text)
        name=te.xpath(r"//span[@class='field-item']/span[@itemprop='name']/a/text()")[0]
        address=te.xpath(r"//span[@class='field-item']/span[@itemprop='address']/text()")[0]
        identifier=te.xpath(r"//span[@class='field-item']/span[@itemprop='identifier']/a/text()")[0]
        foundingDate=te.xpath(r"//span[@class='field-item']/span[@itemprop='foundingDate']/a/text()")[0]
        makesOffer=te.xpath(r"//span[@class='field-item']/span[@itemprop='makesOffer']/text()")[0]
        founder = te.xpath(r"//span[@class='field-item']/span[@itemprop='founder']/a/text()")[0]
        registerMoney = te.xpath(r"//li[7]/span[@class='field-item']/text()")[0]
        foundingLocation=te.xpath(r"//span[@class='field-item']/span[@itemprop='foundingLocation']/a/text()")[0] if te.xpath(r"//span[@itemprop='foundingLocation']") else None
        companyType = te.xpath(r"//span[@class='field-item']/span[@itemprop='']/text()")[0]
        companyStatus = te.xpath(r"//span[@class='field-item']/span[@itemprop='company_status']/text()")[0]
        print(name,address,identifier,foundingDate,makesOffer,founder,registerMoney,foundingLocation,companyType,companyStatus)
        print('-----')

getpage()