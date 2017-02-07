import requests
from pymongo import MongoClient
import threading
from bs4 import BeautifulSoup
import time
import re
from  mogodb_operate import mogo_queue
url = 'http://ip.chinaz.com/getip.aspx'#这个是用于测试IP有效性的网站，IP正常情况下会返回IP，以及IP所在地址
import multiprocessing
ip_queue = mogo_queue('ip_database','proxy_collection')#链接到储存IP的数据库
def ip_catch(max_threads=9):

    def test_effictive_ip():
        while True:#不断循环，找到数据进行测试
            try:
                proxy = ip_queue.find_one_ip()
                        #ip_queue = mogo_queue('ip_database','proxy_collection')#链接数据库，把有用的代理插进去
                try:
                    proxies = {'http':'http://{}'.format(proxy),
                                            'https':'http://{}'.format(proxy),}
                    html = requests.get(url,proxies=proxies,timeout=1)

                    status_number = re.findall(r'\d\d\d', str(html))[0]#提取网页返回码
                    re_ip = re.findall(r'\{ip',html.text)#游戏ip极其恶心，虽然返回的是200数字，表示正常，实则是bad request，这里去除掉
                    #print(re_ip)
                    if status_number==str(200):
                        if re_ip:

                            #检验代理是否能正常使用
                            print('网页返回状态码:',html,proxy,'代理有效,地址是：',html.text)
                        else:
                            ip_queue.delete_proxy(proxy)
                    else:
                        ip_queue.delete_proxy(proxy)
                except:
                    ip_queue.delete_proxy(proxy)
            except KeyError:

                print('队列没有数据了')
                break
                #print(proxy,'代理无效')
    threads = []
    while threads or ip_queue:
        """
                这儿crawl_queue用上了，就是我们__bool__函数的作用，为真则代表我们MongoDB队列里面还有IP没检测完，
                也就是状态依然是没有改变，还有没被测试过的IP
                threads 或者 为真都代表我们还没下载完成，程序就会继续执行
        """
        for thread in threads:
            if not thread.is_alive():  ##is_alive是判断是否为空,不是空则在队列中删掉
                    threads.remove(thread)
        while len(threads) < max_threads :  ##线程池中的线程少于max_threads 或者 crawl_qeue时
            thread = threading.Thread(target=test_effictive_ip)  ##创建线程
            thread.setDaemon(True)  ##设置守护线程
            thread.start()  ##启动线程
            threads.append(thread)  ##添加进线程队列
        time.sleep(5)
def process_crawler():
    process = []
    num_cpus = multiprocessing.cpu_count()
    print('将会启动进程数为：', num_cpus)
    for i in range(num_cpus):
        p = multiprocessing.Process(target=ip_catch)  ##创建进程
        p.start()  ##启动进程
        process.append(p)  ##添加进进程队列
    for p in process:
        p.join()  ##等待进程队列里面的进程结束


if __name__ == "__main__":
    ip_queue.status_setting()#重置状态，以便测试
    process_crawler()