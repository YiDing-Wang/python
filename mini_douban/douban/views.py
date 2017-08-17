# -*-coding:utf-8 -*-
import json
from collections import OrderedDict

import MySQLdb
import datetime
from django.http import HttpResponse
from django.shortcuts import render
from django.core.paginator import Paginator
from spider import start


from os import path

from scipy.misc import imread
import matplotlib.pyplot as plt

from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

# Create your views here.
menu_dict = OrderedDict()
menu_dict[u'电影抓取'] = u''
menu_dict[u'用户画像'] = u''
conn=MySQLdb.connect(host='10.0.4.117',user='root',passwd='QWERT!@#$%',db='test_spider',port=33066,charset='utf8')
cur=conn.cursor()
log_dict=OrderedDict()
log_dict['111']='test'
log_dict['222']='test222'

def index(request):
    return render(request, 'index.html', {'menu_dict': menu_dict})


def movie(request):
    return render(request, '../templates/movie.html', {'menu_dict': menu_dict})


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return json.JSONEncoder.default(self, obj)


def show_asset_in_table(request):
    '''
    :param request:
    :return:
    '''
    if request.method == "GET":
        product = request.GET.get('product')
        limit = request.GET.get('limit')
        offset = request.GET.get('offset')  # how many items in total in the DB
        search = request.GET.get('search')
        sort_column = request.GET.get('sort')   # which column need to sort
        order = request.GET.get('order')      # ascending or descending
        type=''
        if product=='wj':
            type='剧情'
        elif product=='uc':
            type='喜剧'
        elif product=='bc':
            type='恐怖'
        sql='select * from douban_movie WHERE movie_type="%s" limit 100 '%type
        cur.execute(sql)
        all_records =cur.fetchall()
        all_records_count=cur.rowcount
        if not offset:
            offset = 0
        if not limit:
            limit = 20    # 默认是每页20行的内容，与前端默认行数一致
        pageinator = Paginator(all_records, limit)   # 开始做分页

        page = int(int(offset) / int(limit) + 1)
        response_data = {'total': all_records_count, 'rows':[]}   # 必须带有rows和total这2个key，total表示总页数，rows表示每行的内容
        i = int(offset) + 1
        for asset in pageinator.page(page):
            response_data['rows'].append({
                "id": i,
                'movie_name': asset[1],
                "score": asset[2],
                "movie_url": asset[3],
                "movie_country": asset[5],
                "created": asset[6],
            })
            i = i+1

        return HttpResponse(json.dumps(response_data, cls=DateEncoder))


def image_detail(request):
    return render(request, 'datatime-test.html', {'menu_dict': menu_dict})

# 生成用户画像
def image_show(request):
    d = path.dirname(__file__)
    d=path.join(d,'\mini\douban\static\img\\')
    print d
    conn = MySQLdb.connect(host='10.0.4.117', user='root', passwd='QWERT!@#$%', db='test_spider', port=33066,
                           charset='utf8')
    cur = conn.cursor()
    if request.method == "GET":
        fromdate=request.GET.get('date1')
        enddate=request.GET.get('date2')
        # fromdate=datetime.datetime.ctime(fromdate)
        # enddate = datetime.datetime.ctime(enddate)
        sql='SELECT movie_country,count(*) FROM `douban_movie`  where created>"%s" and created<"%s" GROUP BY  movie_country'%(fromdate,enddate)
        print sql
        cur.execute(sql)
        dict = {}
        for words in cur.fetchall():
          dict[words[0]] = words[1]
        alice_coloring = imread(r"D:\untitled2\testpro\111.jpg")
        font = r'C:\Windows\Fonts\simfang.ttf'
        wc = WordCloud(background_color="white",  # 背景颜色max_words=2000,# 词云显示的最大词数
                   font_path=font,
                   mask=alice_coloring,  # 设置背景图片
                   stopwords=STOPWORDS.add("said"),
                   max_font_size=40,  # 字体最大值
                   random_state=42)
        wc.generate_from_frequencies(dict)

        image_colors = ImageColorGenerator(alice_coloring)
          # 以下代码显示图片
        plt.imshow(wc)
        plt.axis("off")
          # 绘制词云
        plt.figure()
    # recolor wordcloud and show
    # we could also give color_func=image_colors directly in the constructor
        plt.imshow(wc.recolor(color_func=image_colors))
        plt.axis("off")
    # 绘制背景图片为颜色的图片
        plt.figure()
        plt.imshow(alice_coloring, cmap=plt.cm.gray)
        plt.axis("off")
    #plt.show()
    # 保存图片
        img_src=path.join(d,'123.png')
        print img_src
        wc.to_file( img_src)
        menu_dict['img']='123.png'

    return render(request, 'datatime-test.html', {'menu_dict': menu_dict})


def spider(request):
    return render(request, 'spider.html', {'menu_dict': menu_dict})


def start_spider(request):
    log_dict=start.main()
    return render(request, 'spider.html', {'log_dict': log_dict})


def stop_spider(request):
    menu_dict1=start.stop_thread(menu_dict)
    print menu_dict1
    return render(request, 'spider.html', {'menu_dict': menu_dict1})
    # return HttpResponse(json.dumps(menu_dict, cls=DateEncoder))