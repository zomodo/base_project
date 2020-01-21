import schedule
import time
import pymysql
import requests
import re
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor
import get_more_ip as getip

class check_data:

    def __init__(self):
        self.test_url='https://www.baidu.com/'

    def select_data(self):
        try:
            connection = pymysql.connect(host='172.16.3.92',user='root',password='123456',port=3306,db='picture',charset='utf8mb4')
            try:
                with connection.cursor() as f:
                    sql="select ip,port from zh_proxy"
                    f.execute(sql)
                    data=f.fetchall()
                    connection.commit()
            finally:
                connection.close()

            return data

        except Exception as e:
            print('连接数据库出错！',e)


    def delete_data(self,ip):
        try:
            connection = pymysql.connect(host='172.16.3.92',user='root',password='123456',port=3306,db='picture',charset='utf8mb4')
            try:
                with connection.cursor() as f:
                    sql="delete from zh_proxy where ip='{}'".format(ip)
                    f.execute(sql)
                    print("删除数据：%s" %ip)
                    connection.commit()
            finally:
                connection.close()
        except Exception as e:
            print('连接数据库出错！',e)


    def update_data(self,ip,speed):
        try:
            connection = pymysql.connect(host='172.16.3.92',user='root',password='123456',port=3306,db='picture',charset='utf8mb4')
            try:
                with connection.cursor() as f:
                    sql="update zh_proxy set speed='%s' where ip='%s'" %(speed,ip)
                    f.execute(sql)
                    print("更新数据：%s" %ip)
                    connection.commit()
            finally:
                connection.close()
        except Exception as e:
            print('连接数据库出错！',e)


    def check_ip(self,ip,port):
        proxy={"http":"http://"+ip+":"+port,"https":"https://"+ip+":"+port}
        print(proxy)
        try:
            t1=time.time()
            response=requests.get(url=self.test_url,headers={"User-Agent":UserAgent(verify_ssl=False).random},proxies=proxy,timeout=10)
            t2=time.time()
            speed=round(t2-t1,2)

            if response.status_code==200:
                self.update_data(ip,speed)

            else:
                self.delete_data(ip)

        except Exception as e:
            self.delete_data(ip)



def start():
    check=check_data()
    data=check.select_data()    # 获取数据库全部ip信息
    print("---当前共有%s条数据---" %len(data))
    pool=ThreadPoolExecutor()
    for proxy in data:
        ip=proxy[0]
        port=proxy[1]
        pool.submit(check.check_ip,ip,port)
    pool.shutdown(wait=True)
    count=len(check.select_data())
    print("---处理完成后剩下%s条数据---" %count)
    if count<100:
        getip.main()
        print("---当前有%s条数据---" %len(check.select_data()))
    else:
        print("---当前有%s条数据---" %count)

start()

schedule.every(20).minutes.do(start)
while True:
    schedule.run_pending()
    time.sleep(1)


