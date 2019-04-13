import requests
import time

from selenium import webdriver
import time


# python3.6环境
from urllib import request
from http import cookiejar

# if __name__ == '__main__':
#     cookie_dict = dict()
#
#     headers = {"Accept": "application/json",
#                "Content-Type": "application/json",
#                "Referer": "https://ke.qq.com/course/185189",
#                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
#                }
#
#     # 声明一个CookieJar对象实例来保存cookie
#     cookie = cookiejar.CookieJar()
#     # 利用urllib.request库的HTTPCookieProcessor对象来创建cookie处理器,也就CookieHandler
#     handler = request.HTTPCookieProcessor(cookie)
#     # 通过CookieHandler创建opener
#     opener = request.build_opener(handler)
#     # 此处的open方法打开网页
#     response = opener.open('https://ke.qq.com/course/185189')
#     # 打印cookie信息
#     for item in cookie:
#         cookie_dict[item.name] = item.value
#
#     res = requests.get("https://ke.qq.com/cgi-bin/comment_new/course_comment_stat?cid=185189&bkn=&r=0.6285281582125787",
#         headers=headers, cookies=cookie_dict)
#     print(res.text)

# def get_json():
#     headers = {"Accept": "application/json",
#                "Content-Type": "application/json",
#                "Referer": "https://ke.qq.com/webcourse/frame.html?r=%d",
#                # "Referer": "https://ke.qq.com/course/185189",
#                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
#                }
#     try:
#         t = time.time()
#         headers['Referer'] = headers['Referer'] % round(t * 1000)
#         res = requests.get("https://ke.qq.com/cgi-bin/course/get_terms_detail?cid=337833&term_id_list=%5B100147308%5D&bkn=&t=0.6918", headers=headers)
#         print(res.text)
#         # content_json = res.json()
#
#     except Exception as e:
#         print("出现BUG了")
#         print(e)
#     finally:
#         time.sleep(1)
        # index += 1
        # get_json(index)


if __name__ == '__main__':
    driver = webdriver.Chrome("/Users/hanyuzhou/Downloads/chromedriver")
    driver.get('https://www.dajie.com')
    # driver.get('http://www.bejson.com/')
    cookies_dict = driver.get_cookies()
    time.sleep(2)
    cookie_str = ''
    for cookies_obj in cookies_dict:
        # print(cookies_obj)
        cookie_str += '%s=%s; ' % (cookies_obj['name'], cookies_obj['value'])
    print(type(cookies_dict))
    print(cookies_dict)
    print(cookie_str)
    # with open('/home/yuzhou/cookie.txt', 'a') as f:
    #     f.write(cookie_str)
    driver.close()
    # cookie_str = ''
    # # 声明一个CookieJar对象实例来保存cookie
    # cookie = cookiejar.CookieJar()
    # # 利用urllib.request库的HTTPCookieProcessor对象来创建cookie处理器,也就CookieHandler
    # handler = request.HTTPCookieProcessor(cookie)
    # # 通过CookieHandler创建opener
    # opener = request.build_opener(handler)
    # # 此处的open方法打开网页
    # response = opener.open('https://www.dajie.com/')
    # # 打印cookie信息
    # for item in cookie:
    #     cookie_str += '%s:%s;' % (item.name, item.value)
    #
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cookie': cookie_str,
        'Connection': 'keep-alive',
        'Host': 'so.dajie.com',
        'Referer': 'https://so.dajie.com/job/search?positionFunction=130202&positionName=UI%E8%AE%BE%E8%AE%A1&from=job',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:66.0) Gecko/20100101 Firefox/66.0',
    }
    res = requests.get('https://so.dajie.com/job/ajax/search/filter?keyword=&order=0&city=&recruitType=&salary=&experience=&page=3&positionFunction=130202&_CSRFToken=&ajax=1', headers=headers)
    pass
