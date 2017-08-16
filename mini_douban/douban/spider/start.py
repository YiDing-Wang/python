# -*- coding:utf-8 -*-
import ctypes
import inspect
import json
import os
import urllib
from collections import OrderedDict
import MySQLdb
import requests
import sys
import Queue
import threading
from bs4 import BeautifulSoup
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))
try:
    from PIL import Image
    import pytesseract
except ImportError:
    print '模块导入错误,请使用pip安装,pytesseract依赖以下库：'
    raise SystemExit

conn=MySQLdb.connect(host='10.0.4.117',user='root',passwd='QWERT!@#$%',db='test_spider',port=33066,charset='utf8')
conn.ping(True)
cur=conn.cursor()

#代理IP
cookie=''
proxy = {'http':'http://115.215.50.218:8118'}
login_cookie = 'bid=W_PCLo9VXfs; ll="118254"; ps=y; ue="1774291949@qq.com"; ' \
               '_vwo_uuid_v2=205A58EB10468CADA7C7F9091912B29B|20eba64ecc03d8fd0980d8780c2779bb;' \
               ' SHOULD_DISPLAY_SURVEY="0"; push_noty_num=0; push_doumail_num=0; ap=1; ' \
               '__utma=30149280.381426802.1497424925.1502696753.1502700624.36; ' \
               '__utmb=30149280.0.10.1502700624; __utmc=30149280;' \
               ' __utmz=30149280.1502246825.27.19.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; ' \
               '__utmv=30149280.16457; as="https://movie.douban.com/"'
UA = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
headers = {'User-Agent': UA}
cookies = {'cookie': login_cookie}


# cookie登录豆瓣
def login_douban(movie_url):
    r = requests.get(movie_url, cookies=cookies, headers=headers,proxies =proxy).content
   # r = requests.get(movie_url, proxies=proxy).content
    bsObj = BeautifulSoup(r, 'html.parser')
    return bsObj


# 获取要爬取网页的内容
def get_movie_url(url):
    movies_content = requests.get(url,cookies=cookie, proxies =proxy).content
    mjson = json.loads(movies_content)
    return mjson,url

# 检验proxy是否成功
def test_proxy():
    res =urllib.urlopen('http://ip.chinaz.com/getip.aspx', proxies=proxy)
    print res.content

def get_movie(mjson,url):
    log_dict = OrderedDict()
    global log_dict
    log_dict['111'] = 'test'
    log_dict['222'] = 'test222'
    # movies_content= requests.get(url,cookies=cookie, proxies =proxy).content
    # mjson=json.loads(movies_content)
    print u'当前抓取的url为：'+url
    for lis in mjson['subjects']:
        # 找出评分大于8.0的电影
        if lis['rate'] >= '8.0':
            movie_name=lis['title']

            score=lis['rate']
            movie_url=lis['url']
            # 进入电影详情页，获取电影类型与所属的国家
            #bsObj=BeautifulSoup(requests.get(movie_url,cookies=cookie,  proxies =proxy).content,'html.parser')
            bsObj = BeautifulSoup(requests.get(movie_url, proxies=proxy).content, 'html.parser')
            infos = bsObj.find('div', {'id': 'info'}).text.split('\n')
            for t in infos:
                if t.startswith(u'类型'):
                    movie_type = t[4:]
                elif t.startswith(u'制片国家/地区'):
                    movie_country = t[9:]
            conn.ping(True)
            cur = conn.cursor()
            cur.execute('select * from douban_movie where movie_name="%s"'%(movie_name))
            if cur.rowcount==0:
                sql='insert into douban_movie(movie_name,score,movie_url,movie_type,movie_country,created)' \
                    ' VALUES ("%s","%s","%s","%s","%s",CURRENT_TIMESTAMP )'\
                    %(movie_name,score,movie_url,movie_type,movie_country)

                print movie_name+':'+sql
                log_dict[movie_name]=sql
                cur.execute(sql)
            else:
                movies=cur.fetchone()
                if movies[2]!=score:
                    sql='update douban_movie set score="%s",updated=CURRENT_TIMESTAMP  where movie_name="%s"'%(score,movie_name)
                    print movie_name+':'+sql
                    log_dict[movie_name] = sql
                    cur.execute(sql)
            print movie_name+':'+'no update'
            log_dict[movie_name] = 'no update'
    sort_type = txt_wrap_by('tag=', '&sort=', url)
    page = url.split('page_start=')[1]
    cur.execute('update douban_url set state=state+1 where sort_type="%s" and page=%s' % (sort_type, page))
    return log_dict



# 取字符串中两个符号之间的字符串
def txt_wrap_by( start_str, end, html):
    start = html.find(start_str)
    if start >= 0:
        start += len(start_str)
        end = html.find(end, start)
        if end >= 0:
            return html[start:end].strip()


# 读取可爬取的urls
def get_available_url(sql):
    cur.execute(sql)
    # testing
    urls=[]
    for url in cur.fetchall():
        sort_type = url[1]
        page = url[2]
        real_url = 'https://movie.douban.com/j/search_subjects?type=movie&' \
                   'tag=%s' % sort_type + '&sort=recommend&page_limit=20&page_start=%s' % page
        urls.append(real_url)
    return urls


# 读取数据库中的url值，判断这个url是否已经读取过
def get_url():
    max_state_sql='SELECT MAX(state) FROM douban_url  '
    cur.execute(max_state_sql)
    max_state=cur.fetchone()[0]
    print max_state
    urls_sql = 'select *  from douban_url where state<%s '%max_state
    cur.execute(urls_sql)
    if cur.rowcount ==0:
        all_urls_sql='select *  from douban_url '
        return get_available_url(all_urls_sql)
    else:
        all_urls_sql = 'select *  from douban_url where state<%s '%max_state
        return get_available_url(all_urls_sql)

# get_url()

# 多进程
# def main(urls):
#     pool = multiprocessing.Pool(multiprocessing.cpu_count())
#     for url in urls:
#         pool.apply_async(get_movie, (url, ))
#     pool.close()
#     pool.join()
#
# if __name__ == "__main__":
#     login_douban('https://movie.douban.com/')
#     urls = get_url()
#     # main(urls)
#     for url in urls:
#         get_movie(url)

# 多线程
queue=Queue.Queue()
out_queue=Queue.Queue()


class ThreadUrl(threading.Thread):
    def __init__(self,queue,out_queue):
        threading.Thread.__init__(self)
        self.queue=queue
        self.out_queue=out_queue

    def run(self):
        while True:
            url=self.queue.get()
            self.out_queue.put(get_movie_url(url))
            self.queue.task_done()


class DatamineThread(threading.Thread):
    def __init__(self,out_queue):
        threading.Thread.__init__(self)
        self.out_queue=out_queue

    def run(self):
        while True:
            mjson, url=self.out_queue.get()
            # url=self.out_queue.get()
            # print '--------------------'
            # print mjson,url
            # print '--------------------'
            get_movie(mjson,url)
            self.out_queue.task_done()

def main():
    urls = get_url()
    login_douban('https://movie.douban.com')
    for i in range(5):
        t=ThreadUrl(queue,out_queue)
        t.setDaemon(True)
        t.start()
    for url in urls:
        queue.put(url)

    for i in range(5):
        dt=DatamineThread(out_queue)
        dt.setDaemon(True)
        dt.start()
    queue.join()
    out_queue.join()
    cur.close()
    conn.close()
    return log_dict


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(menu_dict):
    # thread=ThreadUrl(queue,out_queue)
    # _async_raise(thread.ident, SystemExit)
    os.system("pause")
    menu_dict['stop']='stop'
    return menu_dict




