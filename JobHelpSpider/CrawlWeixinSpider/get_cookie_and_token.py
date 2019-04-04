"""
获取cookie和token写入cookie.txt和token.txt
"""
import requests
import time
import json
import re

from selenium import webdriver


def entrance():
    """
    函数入口
    :return:
    """
    url = 'https://study.163.com/category/480000003121005/'
    cookie_dict = dict()
    browser = webdriver.Chrome('/Users/hanyuzhou/Downloads/chromedriver')
    browser.get(url)

    # 等待browser运行js，
    time.sleep(30)
    cookies = browser.get_cookies()
    # print(cookies)
    for cookie in cookies:
        cookie_dict[cookie.get('name')] = cookie.get('value')
    with open('cookie.txt', "w") as f:
        json.dump(cookie_dict, f)

    real_url = browser.current_url
    # print(real_url)
    # 将token提取并写入token.txt
    # token = re.findall(r'.*token=(\d*)', real_url)[0]
    # with open('token.txt', 'w') as f:
    #     f.write(token)
    # 等待10s关闭chrome
    time.sleep(10)
    browser.quit()


if __name__ == '__main__':
    entrance()
