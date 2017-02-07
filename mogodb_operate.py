from pymongo import MongoClient,errors
from _datetime import datetime,timedelta

class mogo_queue(object):
    OUTSTANDING = 1  ##初始状态
    PROCESSING = 2  ##测试过后的状态

    def __init__(self, db, collection):
        self.client = MongoClient()
        self.database = self.client[db]  # 链接数据库
        self.db = self.database[collection]  # 链接数据库里面这个表
    def __bool__(self):
        """
        这个函数，我的理解是如果下面的表达为真，则整个类为真
        至于有什么用，后面我会注明的（如果我的理解有误，请指点出来谢谢，我也是Python新手）
        $ne的意思是不匹配
        """
        record = self.db.find_one(
            {'status': {'$ne': self.PROCESSING}}
        )
        return True if record else False
    def push_ip_url(self,url):
        self.db.insert({'_id':url})
        print('IP链接{}插入成功'.format(url))
    def find_url(self):#找到所有代理的url
        url_list=[]
        for i in self.db.find():
            url= i['_id']
            url_list.append(url)
        return url_list
    def find_proxy(self):
        proxy_list = []  # 用来接收从数据库查找到的所有代理
        for i in self.db.find():
            proxy = i['proxy']
            proxy_list.append(proxy)
        return proxy_list
    def push_ip(self,ip,port,proxy):#把代理插进数据库的操作
        try:
            self.db.insert({'_id':ip,'port':port,'proxy':proxy,'status':self.OUTSTANDING})
            print(proxy,'代理插入成功')
        except errors.DuplicateKeyError as e:#对于重复的ip不能插入
            print(proxy,'已经存在队列中')
    def find_one_ip(self):
        record = self.db.find_and_modify(
            query={'status': self.OUTSTANDING},#改变状态，防止另外的进程也车市同一个ip
            update={'$set': {'status': self.PROCESSING,}}
        )
        if record:
            return record['proxy']
        else:
            raise KeyError
    def status_setting(self):
        record = self.db.find({'status':self.PROCESSING})#找到所有状态为2的代理，就是之前测试过的
        #print(record)
        for i in record:
            print(i)
            id=i["_id"]
            #query={'status':self.PROCESSING},
            self.db.update({'_id':id},{'$set': {'status': self.OUTSTANDING }})#该状态为1，重新测试
            print('代理',id,'更改成功')
        # if record:
        #     return record
    def delete_proxy(self,proxy):
        """这个函数是更新已完成的URL完成"""
        self.db.delete_one({'proxy': proxy})
        print('无效代理{}删除成功'.format(proxy))

