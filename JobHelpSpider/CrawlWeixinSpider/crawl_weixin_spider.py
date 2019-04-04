import json
import requests
import time
import random
import pymysql

from selenium import webdriver

WEIXIN_URL = 'https://mp.weixin.qq.com/'
COOKIE_FILE = '/home/yuzhou/python_file/ArticleSpider/CrawlWeixinSpider/cookie.txt'
TOKEN_FILE = '/home/yuzhou/python_file/ArticleSpider/CrawlWeixinSpider/token.txt'


def get_cookie_and_token():
    """
    从文件中获取token和cookie
    :return:
    """
    with open(COOKIE_FILE, 'r') as f:
        cookie = json.load(f)
    with open(TOKEN_FILE, 'r') as f:
        token = f.readline()

    return cookie, token


def get_fake_id(token, cookie):
    """
    获取fake_id
    :param token:
    :return:
    """
    # searchbiz接口的相关信息
    searchbiz_url = 'https://mp.weixin.qq.com/cgi-bin/searchbiz'
    searchbiz_data = {
        'action': 'search_biz',
        'token': token,
        'lang': 'zh_CN',
        'f': 'json',
        'ajax': '1',
        'random': '0.544464898363296',
        'query': query_word,
        'begin': '',
        'count': '5',
    }

    searchbiz_response = requests.get(url=searchbiz_url, cookies=cookie, params=searchbiz_data)
    print(searchbiz_response.json())
    time.sleep(4)
    fake_id = searchbiz_response.json()['list'][0].get('fakeid')
    return fake_id


def get_db_conn():
    return pymysql.connect(host='60.205.224.136',
                           user='root',
                           passwd='123456',
                           db='wyf_sql',
                           port=3306,
                           charset="utf8")


def insert_franky_fm(conn, id, title, url):
    sql = "insert into franky_fm(title, url) values '%s', '%s'" % (title, url)
    try:
        cursor = conn.cursor()
        cursor.excute(sql)
        conn.commit()
    except Exception as e:
        print('error')


def entrance(query_word):
    """
    抓取脚本的入口
    :param query_word:
    :return:
    """
    cookie, token = get_cookie_and_token()
    fake_id = get_fake_id(token, cookie)

    appmsg_data = {
        'token': token,
        'lang': 'zh_CN',
        'f': 'json',
        'ajax': '1',
        'random': '0.5150533231730943',
        'action': 'list_ex',
        'begin': '0',
        'count': '5',
        'query': '',
        'fakeid': fake_id,
        'type': '9',
    }
    # appmsg接口的相关接口
    appmsg_url = 'https://mp.weixin.qq.com/cgi-bin/appmsg'
    appmsg_response = requests.get(url=appmsg_url, cookies=cookie, params=appmsg_data)
    # 翻页的次数
    page_count = int(int(appmsg_response.json()['app_msg_cnt']) / 5)
    begin = -5

    conn = get_db_conn()
    while begin < page_count:
        appmsg_data['begin'] = str(int(appmsg_data['begin']) + 5)
        appmsg_data['random'] = random.random()
        begin += 1
        # 停10s后再爬取，爬取过快会被ban掉
        time.sleep(10)
        appmsg_response = requests.get(url=appmsg_url, cookies=cookie, params=appmsg_data)
        app_msg_list = appmsg_response.json()['app_msg_list']
        # 遍历文章列表，进行存取
        for app_msg_obj in app_msg_list:
            title = app_msg_obj['title']
            url = app_msg_obj['link']
            id = app_msg_obj['appmsgid']
            print('id:{0}  title:{1}  url:{2}'.format(id, title, url))
            insert_franky_fm(conn, id, title, url)


if __name__ == '__main__':
    query_word = input('请输入要爬取的微信公众号:')
    entrance(query_word)
