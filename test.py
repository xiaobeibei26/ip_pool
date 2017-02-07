import requests
from pymongo import MongoClient
import re
from bs4 import BeautifulSoup
from  mogodb_operate import mogo_queue
from proxy_request import  request
url_queue = mogo_queue('ip_database','ip_link_collection')
ip_queue = mogo_queue('ip_database','proxy_collection')

class ip_operator():
    @staticmethod
    def insert_xici_url(page):
        urls = ['http://www.xicidaili.com/nn/{}'.format(str(i)) for i in range(page)]#构造西刺网前面page页的URL
        for url in urls:
            #print(url)
            url_queue.push_ip_url(url)#插进URL数据库

    @staticmethod
    def catch_ip_xici():#爬取西刺网前面50页的免费IP
        ip_url=url_queue.find_url()
        for url in ip_url:
            data = request.get(url,3)
            all_data = BeautifulSoup(data.text, 'lxml')
            all_ip = all_data.find_all('tr', class_='odd')
            for i in all_ip:
                ip = i.find_all('td')[1].get_text()  # ip
                port = i.find_all('td')[2].get_text()  # 端口
                proxy = (ip + ':' + port).strip()  # 组成成proxy代理
                ip_queue.push_ip(ip,port,proxy)#插进数据库
    #ip_queue.find_one_ip()
    @staticmethod#本来还想把快代理的抓取也封装进来，然后测试了西刺之后，觉得免费IP就算了吧....，这段代码大家可以无视
    def insert_kuaidaili_url(page):
        urls=['http://www.kuaidaili.com/free/inha/{}/'.format(str(i)) for i in range(page)]
        for url in urls:
            url_queue.push_ip_url(url)
    #catch_url_ip()
    @staticmethod
    def insert_ip_text():#把txt文件里面的ip存进数据库
        f= open('C:\\Users\\admin\\Desktop\\ip_daili.txt',encoding='utf-8')
        data = f.read()
        proxy=data.split('\n')
        for i in proxy:
            proxie = i,
            ip =i.split(':')[0]# ip
            port =i.split(":")[1]   # 端口
            #proxie = str(ip)+':'+str(port),
            #print(ip,port,i)
            ip_queue.push_ip(ip,port,i)
        #print(proxy)
        f.close()



ip_operator.catch_ip_xici()
#爬西刺的代理，存进数据库以待检验
ip_operator().insert_ip_text()
#把txt文件里面保存的IP插进数数据库以待检验存进数据库以待检验

