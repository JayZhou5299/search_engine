import requests
import time

from selenium import webdriver

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
    cookie_str = ''
    # 声明一个CookieJar对象实例来保存cookie
    cookie = cookiejar.CookieJar()
    # 利用urllib.request库的HTTPCookieProcessor对象来创建cookie处理器,也就CookieHandler
    handler = request.HTTPCookieProcessor(cookie)
    # 通过CookieHandler创建opener
    opener = request.build_opener(handler)
    # 此处的open方法打开网页
    response = opener.open('https://www.dajie.com/')
    # 打印cookie信息
    for item in cookie:
        cookie_str += '%s:%s;' % (item.name, item.value)

    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cookie': "DJ_UVID=MTU1MzI0NDI2Mzc3MzMzODUw; Hm_lvt_6822a51ffa95d58bbe562e877f743b4f=1553244271,1554518025,1554897087,1554974880; _ga=GA1.2.1224385216.1553244271; _gid=GA1.2.976055477.1554897088; _close_autoreg=1554974886799; _close_autoreg_num=4; DJ_RF=empty; DJ_EU=http%3A%2F%2Fso.dajie.com%2Fjob%2Fsearch%3FpositionFunction%3D130201%26positionName%3D%25E7%25BD%2591%25E9%25A1%25B5%25E8%25AE%25BE%25E8%25AE%25A1; SO_COOKIE_V2=3b2fArhROjPV7KLHz3tgHDnQrxBlBRfPOzs4RM14AzoUKV7m2Re/I4xL772izIEWLXfeh8Wi4cEYVn1RaEgkuPTfioJaPJa4nLk0; Hm_lpvt_6822a51ffa95d58bbe562e877f743b4f=1554975233; _gat_gtag_UA_117102476_1=1",
        'Connection': 'keep-alive',
        'Host': 'so.dajie.com',
        'Referer': 'https://so.dajie.com/job/search?positionFunction=130202&positionName=UI%E8%AE%BE%E8%AE%A1&from=job',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:66.0) Gecko/20100101 Firefox/66.0',
    }
    res = requests.get('https://so.dajie.com/job/ajax/search/filter?keyword=&order=0&city=&'
                       'recruitType=&salary=&experience=&page=1&positionFunction=130202&'
                       '_CSRFToken=&ajax=1', headers=headers)
    pass
