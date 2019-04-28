import requests
import time
from urllib import request
from http import cookiejar
from selenium import webdriver

def get_cookies(url):
    cookie_dict = dict()
    browser = webdriver.Chrome('/Users/hanyuzhou/Downloads/chromedriver')
    browser.get(url)

    # 等待browser运行js，
    cookies = browser.get_cookies()
    # print(cookies)
    for cookie in cookies:
        cookie_dict[cookie.get('name')] = cookie.get('value')

    time.sleep(10)
    browser.quit()
    return cookie_dict


def get_json():
    payload = {
               'activityId': 0,
               'frontCategoryId': "480000003131009",
               'keyword': "",
               'orderType': 50,
               'pageIndex': 3,
               'pageSize': 50,
               'priceType': -1,
               'relativeOffset': 100,
               'searchTimeType': -1,
               }

    headers = {"Accept": "application/json",
               "Host": "study.163.com",
               "Origin": "https://study.163.com",
               "Content-Type": "application/json",
               "Referer": "https://study.163.com/category/480000003131009",
               "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
               }

    cookies = get_cookies('https://study.163.com/category/480000003131009/')
    try:
        # 请注意这个地方发送的是post请求
        res = requests.post(url="https://study.163.com/p/search/studycourse.json",
                            headers=headers,
                            data=payload,
                            cookies=cookies)
        print(res)

        # content_json = res.json()

    except Exception as e:
        print("出现BUG了")
        print(e)
    finally:
        time.sleep(1)
        # index += 1
        # get_json(index)

# def get_category():
#     """
#     获取目录信息
#     :return:
#     """
#     url = 'https://home.study.163.com/home/j/web/getFrontCategory.json?t=1551697844168'
#     response = requests.get(url)
#     print (response.text)


def test2():
    res = requests.get('https://study.163.com/category/480000003131009#/?p=4')
    pass

if __name__ == '__main__':
    # test2()
    get_json()
    # get_category()
    # get_json()
