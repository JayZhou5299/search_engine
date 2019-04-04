import requests
import time
import pymysql

from scrapy.selector import Selector


def crawl_xici_ip():
    """
    爬取西刺代理的ip
    :return:
    """
    db = pymysql.connect("localhost", "root", "root", "search_engine")
    cursor = db.cursor()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:64.0) Gecko/20100101 Firefox/64.0'
    }
    ip_list = list()

    for index in range(1, 20):
        response = requests.get(url='https://www.xicidaili.com/nn/{0}'.format(index), headers=headers)
        selector = Selector(text=response.text)
        all_proxy = selector.css('#ip_list tr')

        for tr_obj in all_proxy[1:]:
            all_text = tr_obj.css('td::text').extract()
            ip = all_text[0]
            port = all_text[1]
            proxy_type = all_text[5]
            speed_str = tr_obj.css('.bar::attr(title)').extract_first()
            if speed_str:
                speed = float(speed_str.split('秒')[0])

            ip_list.append((ip, port, proxy_type, speed))
        time.sleep(20)
        sql = "INSERT INTO ip_proxy(ip, port, proxy_type, speed) " \
              "VALUES ('{0}', '{1}', '{2}', '{3}')".format(ip, port, proxy_type, speed)
        try:
            cursor.execute(sql)
            db.commit()
        except Exception as e:
            db.rollback()
            print('[Error]:{0}'.format(e))

    db.close()


class GetIp(object):
    def __init__(self):
        db = pymysql.connect("localhost", "root", "root", "search_engine")
        self.cursor = db.cursor()

    @classmethod
    def judge_ip(self, proxy_url):
        """
        判断ip是否合法
        :param ip:
        :param port:
        :return:
        """
        http_url = 'http://www.baidu.com'
        try:
            print('enter')
            proxy_dict = {
                "http": proxy_url,
                # "https": proxy_url,
            }
            response = requests.get(http_url, proxies=proxy_dict)
            return True
        except Exception as e:
            print('invail ip and port')
            return False
        else:
            code = response.status_code
            if code >= 200 and code <300:
                print('effective ip and port')
                return True
            else:
                print('invail ip and port')
                self.del_ip_proxy()
                return False

    def get_random_ip(self):
        random_sql = "select ip, port, proxy_type from ip_proxy order by rand() limit 1"
        self.cursor.execute(random_sql)
        ip_list = self.cursor.fetchall()

        for ip_info in ip_list:
            proxy_url = "{0}://{1}:{2}".format(ip_info[2], ip_info[0], ip_info[1])

            # if self
            #     return

    def del_ip(self):
        pass


if __name__ == '__main__':
    # crawl_xici_ip()
    GetIp.judge_ip('http://117.88.49.48:9999')
