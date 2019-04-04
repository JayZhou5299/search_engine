import requests
import time


def get_json():
    payload = {"activityId": 0,
               "pageIndex": 1,
               "pageSize": 50,
               "relativeOffset": 0,
               "frontCategoryId": 480000003129019,
               "searchTimeType": -1,
               "orderType": 50,
               "priceType": -1,
               "activityId": 0,
               "keyword": ""
               }
    headers = {"Accept": "application/json",
               "Host": "study.163.com",
               "Origin": "https://study.163.com",
               "Content-Type": "application/json",
               # "Referer": "https://study.163.com/category/480000003129019",
               "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
               }
    try:
        # 请注意这个地方发送的是post请求
        # CSDN 博客 梦想橡皮擦
        res = requests.post("https://study.163.com/p/search/studycourse.json", json=payload,
                            headers=headers)
        print(res)

        # content_json = res.json()

    except Exception as e:
        print("出现BUG了")
        print(e)
    finally:
        time.sleep(1)
        # index += 1
        # get_json(index)


def get_category():
    """
    获取目录信息
    :return:
    """
    url = 'https://chuanke.baidu.com/'
    response = requests.get(url)
    print (response.text)


if __name__ == '__main__':
    get_category()
    # get_json()
