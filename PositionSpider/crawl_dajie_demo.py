import requests
import time
from urllib import request
from http import cookiejar

def get_json():
    cookie_dict = dict()
    headers = {
               "Referer": 'https://so.dajie.com/job/search?positionFunction=130108&positionName=%E7%A1%AC%E4%BB%B6%E4%BA%A7%E5%93%81',
               "Host": "so.dajie.com",
               "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
               }
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
        cookie_dict[item.name] = item.value

    try:
        res = requests.get("https://so.dajie.com/job/ajax/search/filter?keyword=&order=0&city=&recruitType=&salary=&experience=&page=1&positionFunction=130108&_CSRFToken=&ajax=1",
                           headers=headers, cookies=cookie_dict)
        print(res.text)

    except Exception as e:
        print("出现BUG了")
        print(e)
    finally:
        time.sleep(1)
        # index += 1
        # get_json(index)


if __name__ == '__main__':
    get_json()
