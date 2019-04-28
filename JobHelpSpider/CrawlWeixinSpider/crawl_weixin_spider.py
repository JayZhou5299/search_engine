import json
import os
import re
import datetime
import requests
import time
import random
import pymysql
from scrapy import Selector
from elasticsearch_dsl.connections import connections
from w3lib.html import remove_tags


from JobHelpSpider.utils.common import get_md5
from JobHelpSpider.utils.common import remove_t_r_n
from JobHelpSpider.models.es_types import JobWantedInformationType
from JobHelpSpider import settings

es = connections.create_connection(hosts=[settings.ES_ADDRESS])

WEIXIN_URL = 'https://mp.weixin.qq.com/'
COOKIE_FILE = os.path.join(os.path.abspath('.'), 'cookie.txt')
TOKEN_FILE = os.path.join(os.path.abspath('.'), 'token.txt')


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
        'random': random.random(),
        'query': query_word,
        'begin': '',
        'count': '5',
    }

    searchbiz_response = requests.get(url=searchbiz_url, cookies=cookie, params=searchbiz_data)
    print(searchbiz_response.json())
    time.sleep(4)
    fake_id = searchbiz_response.json()['list'][0].get('fakeid')
    return fake_id


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
        'random': random.random(),
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
            res = requests.get(app_msg_obj['link'])
            selector = Selector(text=res.text)
            title = selector.css('#activity-name::text').extract_first()
            content = remove_t_r_n(remove_tags(selector.css('#js_content').extract_first()))
            str_time = re.findall(r'var publish_time = "(\d{4}-\d{2}-\d{2})"', res.text)[0]
            publish_time = datetime.datetime.strptime(str_time, '%Y-%m-%d').date()
            data_source = selector.css('#js_name::text').extract_first()
            if not title or not data_source:
                continue
            temp_item = dict()
            temp_item['url'] = res.url
            temp_item['url_object_id'] = get_md5(res.url)
            temp_item['abstract'] = content[:300]
            temp_item['publish_time'] = publish_time
            temp_item['title'] = remove_t_r_n(title)
            temp_item['data_source'] = remove_t_r_n(data_source)
            es_save(temp_item)


def gen_suggests(index, info_tuple):
    """
    根据字符串生成搜索建议数组
    :param index:
    :param info_tuple:
    :return:
    """
    used_words = set()
    suggests = []
    for text, weight in info_tuple:
        if text:
            # 调用es的analyze接口分析字符串
            words = es.indices.analyze(index=index, analyzer='ik_max_word',
                                        params={'filter':['lowercase']}, body=text)

            # 将长度为小于等于1的词过滤掉，这种词没有意义
            analyzed_words = set([r['token'] for r in words['tokens'] if len(r['token']) > 1])

            # 将之前用过的词去掉
            new_words = analyzed_words - used_words
        else:
            new_words = set()

        # 如果存在新词就将其添加到建议数组中，在used_words中添加这些词(做并集)
        if new_words:
            suggests.append({'input': list(new_words), 'weight': weight})
            used_words = used_words.union(new_words)

    return suggests


def es_save(item):
    """
    将item转换为es的数据格式
    :return:
    """
    # 初始化一个es的document
    job_wanted_information = JobWantedInformationType()
    # 将该条document的id设置为url_object_id
    job_wanted_information.meta.id = item['url_object_id']
    job_wanted_information.url = item['url']
    job_wanted_information.title = item['title']
    job_wanted_information.data_source = item['data_source']
    job_wanted_information.abstract = item['abstract']
    job_wanted_information.publish_time = item['publish_time']
    job_wanted_information.suggest = gen_suggests(JobWantedInformationType._doc_type.index,
                                                       ((job_wanted_information.title, 10),
                                                        (job_wanted_information.abstract, 6)))

    # 调用save方法直接存储到es中
    job_wanted_information.save()


if __name__ == '__main__':
    query_word = input('请输入要爬取的微信公众号:')
    entrance(query_word)
