import json
import pymysql
import numpy as np
import pymysql.cursors
from snownlp import SnowNLP
from aip import AipNlp

from VideoSpider import settings

""" 你的 APPID AK SK """
APP_ID = '15869518'
API_KEY = '3MEcyzqMcDul8OUKHIYmfngB'
SECRET_KEY = 'KDzSqoWS0ZnCtDB5XbiRyVL0TFSqnXlf'

client = AipNlp(APP_ID, API_KEY, SECRET_KEY)


class SentimentAnalyzer(object):
    """
    情感分析
    """
    def get_data(self):
        """
        获取数据
        :return:返回值为list包dict类型
        """
        # 连接db并获取游标
        conn = pymysql.connect(host=settings.MYSQL_HOST,
                               user=settings.MYSQL_USER,
                               passwd=settings.MYSQL_PASSWORD,
                               db=settings.MYSQL_DB,
                               charset='utf8',
                               cursorclass=pymysql.cursors.DictCursor)
        cursor = conn.cursor()
        sql = "select evaluation_content, url_object_id from tb_learning_video"

        cursor.execute(sql)
        data = cursor.fetchall()
        cursor.close()
        conn.close()

        return data

    def handle_data(self, data):
        """
        处理数据
        步骤：
        1.先对数据进行清洗，去掉垃圾数据
        2.对数据进行情感分析
        3.将分析结果进行加权平均求得分析后的得分
        :param data:入参为list包dict类型
        :return:
        """
        res_list = list()
        sentiment_score_list = list()
        for data_obj in data:
            if data_obj['evaluation_content'] and len(data_obj['evaluation_content']) > 0:
                # 有的数据里面带换行符，会导致json.loads报错，所以需要去掉
                evaluation_list = data_obj['evaluation_content'].replace('\n', '，').split('\t')
            else:
                continue

            # 1.清洗数据，将没有意义的数据去除掉，如评论内容过少的内容
            for evaluation_obj in evaluation_list:
                json_dict = json.loads(evaluation_obj)
                for key, value in json_dict.items():
                    text = key
                    score = value

                # 2.对数据进行情感分析，如果文本内容不能分析的取0.5这个中间值
                if text and len(text) >= 5:
                    # sentiments = self.sentiment_data(text)
                    sentiments = self.sentiment_data_by_baidu(text)
                    with open('sentiments_baidu.txt', 'a') as f:
                        f.write('%s\t%s\n' % (text, sentiments))
                else:
                    sentiments = 0
                sentiment_score = sentiments * float(score)
                sentiment_score_list.append(sentiment_score)

            # 3.将分析结果进行加权平均求得分析后的得分
            res_list.append({'url_object_id': data_obj['url_object_id'],
                             'sentiment_score': np.mean(sentiment_score_list)})
        return res_list

    def sentiment_data(self, text):
        """
        进行情感打分
        :param text: 情感打分文本
        :return: 返回值为情感打分的结果
        """
        if isinstance(text, str):
            text = text.encode("utf-8").decode("utf-8")

        s = SnowNLP(text)
        with open('sentiments.txt', 'a') as f:
            f.write('%s\t%s\n' % (text, s.sentiments))
        return s.sentiments

    def sentiment_data_by_baidu(self, text):
        """
        通过百度ai平台进行情感打分
        :param text:
        :return:返回的范围为[-1,1]，负数代表消极的
        """
        """
        res_dict的返回类型：
        {
            "text":"苹果是一家伟大的公司",
            "items":[
                {
                    "sentiment":2,    //表示情感极性分类结果，0:负向，1:中性，2:正向
                    "confidence":0.40, //表示分类的置信度
                    "positive_prob":0.73, //表示属于积极类别的概率
                    "negative_prob":0.27  //表示属于消极类别的概率
                }
            ]
        }
        """
        if len(text) >= 256:
            text = text[:255]
        res_dict = client.sentimentClassify(text)['items'][0]
        negative_prob = res_dict['negative_prob']
        positive_prob = res_dict['positive_prob']

        # 消极情感
        if negative_prob > 0.5:
            return (0.5 - negative_prob) * 2

        # 积极情感
        else:
            return (positive_prob - 0.5) * 2

    def save_data(self):
        """
        保存数据
        :return:
        """
        pass

    def entrance(self):
        """
        入口函数
        :return:
        """
        analyze_data = self.get_data()
        self.handle_data(analyze_data)

        pass


if __name__ == '__main__':
    sentiment_analyzer = SentimentAnalyzer()
    sentiment_analyzer.entrance()