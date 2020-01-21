# Author:zmd
# Date:2019/8/9 16:14
# desc:
import requests
import time
import asyncio
import re
from lxml import etree
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor
import pymysql
import schedule

#   https://www.baidu.com/ 测试ip是否可用
#   http://httpbin.org/ip 判断是否高匿
#   https://www.ip.cn/    判断网络位置

class getip_from_xiladaili:     # http://www.xiladaili.com/
    def __init__(self):
        self.nm_url="http://www.xiladaili.com/gaoni/"
        self.tm_url="http://www.xiladaili.com/putong/"

    def getdata(self,url):
        proxies=[]
        response=requests.get(url,headers={"User-Agent": UserAgent(verify_ssl=False).random})
        tree=etree.HTML(response.text)
        content=tree.xpath(r"//table[@class='fl-table']/tbody/tr")
        for data in content:
            ip=data.xpath(r"./td[1]/text()")[0]
            proxy = {"http":"http://"+ip,"https":"https://"+ip}
            proxies.append(proxy)

        return proxies

    def getip(self):
        pool=ThreadPoolExecutor()
        all_url=[]
        all_ip=[]
        for page in range(1,6):
            all_url.append(self.nm_url+str(page))
            all_url.append(self.tm_url+str(page))
        for url in all_url:
            res=pool.submit(self.getdata,url)
            time.sleep(2)        # 多线程导致服务器过载，报503错误，温柔访问加sleep
            all_ip +=res.result()
        pool.shutdown(wait=True)

        return all_ip


class getip_from_89ip:      # http://www.89ip.cn/
    def __init__(self):
        self.page_url=[]

    def getpage(self,page):
        begin_url = "http://www.89ip.cn/index_{}.html".format(page)
        response=requests.get(begin_url,headers={"User-Agent":UserAgent(verify_ssl=False).random})
        tree=etree.HTML(response.text)
        if tree.xpath("//table/tbody/tr"):
            self.page_url.append(begin_url)
            page +=1
            self.getpage(page)
        else:
            pass
            #print("共有%s页" %(page-1))

        return self.page_url

    def get_all_ip(self,url):
        proxies = []
        response=requests.get(url,headers={"User-Agent":UserAgent(verify_ssl=False).random})
        tree=etree.HTML(response.text)
        content=tree.xpath(r"//table/tbody/tr")
        for d in content:
            ip=d.xpath("./td[1]/text()")[0].strip()
            port=d.xpath("./td[2]/text()")[0].strip()
            proxy={"http":"http://"+ip+":"+port,"https":"https://"+ip+":"+port}
            proxies.append(proxy)

        return proxies

    def getip(self):
        page_url=self.getpage(1)
        pool=ThreadPoolExecutor()
        all_ip=[]
        for url in page_url:
            res=pool.submit(self.get_all_ip,url)
            time.sleep(2)
            all_ip +=res.result()
            #result.add_done_callback(self.test_ip)
        pool.shutdown(wait=True)

        return all_ip

class getip_from_kuaidaili:     # https://www.kuaidaili.com
    def __init__(self):
        self.nm_url="https://www.kuaidaili.com/free/inha/"  # 匿名url
        self.tm_url="https://www.kuaidaili.com/free/intr/"  # 透明url

    def getdata(self,url):
        proxies = []
        req = requests.get(url,headers={"User-Agent":UserAgent(verify_ssl=False).random})
        tree = etree.HTML(req.text)
        content = tree.xpath(r'//div[@id="list"]/table/tbody/tr')
        for data in content:
            ip = data.xpath(r"./td[1]/text()")[0]
            port = data.xpath(r"./td[2]/text()")[0]
            proxy = {"http": "http://" + ip + ":" + port, "https": "https://" + ip + ":" + port}
            proxies.append(proxy)
        return proxies

    def getip(self):
        all_url=[]
        all_ip=[]
        for page in range(1,11):
            all_url.append(self.nm_url+str(page))
            all_url.append(self.tm_url+str(page))
        pool=ThreadPoolExecutor()
        for url in all_url:
            res=pool.submit(self.getdata,url)
            time.sleep(2)       # 多线程导致服务器过载，报503错误，温柔访问加sleep
            all_ip +=res.result()
        pool.shutdown(wait=True)

        return all_ip


class save_to_mysql:
    def __init__(self):
        self.test_url = "https://www.baidu.com/"
        self.type_url = "http://httpbin.org/ip"
        self.address_url = "https://www.ip.cn/"

    def check(self,ip):
        try:
            begin_time=time.time()
            response=requests.get(url=self.test_url,headers={"User-Agent":UserAgent(verify_ssl=False).random},proxies=ip,timeout=10)
            end_time=time.time()
            speed=round(end_time-begin_time,2)
            now=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        except Exception as e:
            pass
        else:
            if response.status_code==200:
                #print("valid_ip:%s" %ip)
                http=re.search(r"http://(.*)", ip['http']).group(1).split(":")
                address_response=requests.get(url=self.address_url,headers={"user-agent":UserAgent(verify_ssl=False).random},params={"ip":http[0]},timeout=10)
                address=re.search(r"<p>所在地理位置：<code>(.*?)</code></p>",address_response.text).group(1)
                type_response=requests.get(url=self.type_url,headers={"User-Agent":UserAgent(verify_ssl=False).random},proxies=ip,timeout=10)
                if re.search("origin",type_response.text):
                    type_text=re.search('"origin": "(.*)"',type_response.text).group(1).split(", ")
                    if type_text[0]==type_text[1] and type_text[0] !="27.17.62.186":
                        type="高匿"
                        print('--->',type,http[0],http[1],address,speed,now)
                    else:
                        type="透明"
                        print('--->',type,http[0],http[1],address,speed,now)
                else:
                    type="-"
                    print('--->',type,http[0],http[1],address,speed,now)

                data=[http[0],http[1],address,type,speed,now]

                self.save(data)
            else:
                pass



    def save(self,data):
        try:
            connection=pymysql.connect(host='172.16.3.92',user='root',password='123456',port=3306,db='picture',charset='utf8mb4')
            try:
                with connection.cursor() as f:
                    sql='replace into zh_proxy values("%s","%s","%s","%s","%s","%s")' %(data[0],data[1],data[2],data[3],data[4],data[5])
                    f.execute(sql)
                    connection.commit()
            finally:
                connection.close()

        except Exception as e:
            print("连接数据库出错",e)

# if __name__ == "__main__":
#     p1=getip_from_89ip()
#     data1=p1.getip()
#     #print(data1)
#     p2=getip_from_kuaidaili()
#     data2=p2.getip()
#     #print(data2)
#     p3=getip_from_xicidaili()
#     data3=p3.getip()
#     #print(data3)
#     data=data1+data2+data3
#     print(data,len(data))
#
#     pool=ThreadPoolExecutor()
#     for ip in data:
#         result=pool.submit(save_to_mysql().check,ip)
#     pool.shutdown(wait=True)

def main():
    p1=getip_from_xiladaili()
    data1=p1.getip()
    #print(data1)
    p2=getip_from_89ip()
    data2=p2.getip()
    #print(data2)
    p3=getip_from_kuaidaili()
    data3=p3.getip()
    #print(data3)
    data=data1+data2+data3
    #print(data,len(data))
    print("---共收集%s个ip---" %len(data))

    pool=ThreadPoolExecutor()
    for ip in data:
        result=pool.submit(save_to_mysql().check,ip)
    pool.shutdown(wait=True)

main()
# schedule.every(10).minutes.do(main)
# while True:
#     schedule.run_pending()
#     time.sleep(1)
