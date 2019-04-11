import json
import pymysql
import random
import numpy as np
import pymysql.cursors
import time
import matplotlib.pyplot as plt
from snownlp import SnowNLP
from aip import AipNlp
from sklearn import preprocessing
from elasticsearch import Elasticsearch


client = Elasticsearch(hosts=['60.205.224.136'])


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
                               charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)
        cursor = conn.cursor()
        sql = "select evaluation_content, url_object_id, learner_nums from tb_learning_video"

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
                # 如果没有评论就给一个默认的空即可
                evaluation_list = ['{"": 0}']

            # 1.清洗数据，将没有意义的数据去除掉，如没有评论内容或者评论内容过少的内容
            for evaluation_obj in evaluation_list:
                json_dict = json.loads(evaluation_obj)
                for key, value in json_dict.items():
                    text = key
                    score = value

                # 2.对数据进行情感分析，如果文本内容不能分析的取0.5这个中间值
                if text and len(text) > 5:
                    # 如果score=-1代表该评论没有score这个属性，所以需要将flag置为1
                    if score == -1:
                        sentiments, score = self.sentiment_data(text, 1)
                    else:
                        sentiments = self.sentiment_data(text)

                    # with open('sentiments_baidu.txt', 'a') as f:
                    #     f.write('%s\t%s\n' % (text, sentiments))
                else:
                    sentiments = 0.5

                # 对于一些只有评论内容的数据，其score分数为情感分析的数值*10
                sentiment_score = sentiments * float(score)
                sentiment_score_list.append(sentiment_score)

            avg_score = np.mean(sentiment_score_list)
            # 3.将情感分析结果进行加权平均求得分析后的得分
            res_list.append({'url_object_id': data_obj['url_object_id'],
                             'sentiment_score': np.mean(sentiment_score_list),
                             'learner_nums': data_obj['learner_nums']})
            # time.sleep(random.randint(4, 5))

        return res_list

    def sentiment_data(self, text, flag=0):
        """
        进行情感打分
        :param text: 情感打分文本
        :param flag:表示该评论是否有score这个属性，如果没有需要返回score和setiment两个值(1代表没有score)
        :return: 返回值为情感打分的结果
        """
        if isinstance(text, str):
            text = text.encode("utf-8").decode("utf-8")

        s = SnowNLP(text)
        with open('sentiments.txt', 'a') as f:
            f.write('%s\t%s\n' % (text, s.sentiments))

        if flag == 0:
            return s.sentiments

        # 如果该评论没有score这个属性，需要多返回一个score属性
        else:
            return s.sentiments, s.sentiments * 10

    def calculate_recommend_score(self, unhandled_data):
        """
        计算推荐度
        :return:
        """
        unhandled_list = list()
        url_object_id_list = list()
        for handled_data_obj in unhandled_data:
            temp_tuple = (handled_data_obj['sentiment_score'], handled_data_obj['learner_nums'])
            url_object_id_list.append(handled_data_obj['url_object_id'])
            unhandled_list.append(temp_tuple)

        handled_list = np.array(unhandled_list)

        # 由于学习人数没有明显的边界，就用均值方差归一化
        handled_list = preprocessing.scale(unhandled_list)

        # 绘制图，看一下点的分布情况
        plt.scatter(handled_list[:, 0], handled_list[:, 1])
        plt.show()

        recommend_score_list = list()
        # 遍历计算推荐度，并更新到es中
        for handled_obj in handled_list:

            # 以5为起始标准，因为归一化的结果有负数
            recommend_score = handled_obj[0] * 0.3 + handled_obj[1] * 0.7 + 5
            recommend_score_list.append(recommend_score)

        plt.scatter(np.ones(len(recommend_score_list)), recommend_score_list)
        plt.show()
        pass
            # client.update(index='learning_video', doc_type='video',
            #               id=url_object_id_list[handled_list.index(handled_obj)],
            #               body={'recommend_score': recommend_score})

    def normal_li(self):
        """
        由于学习人数没有明显的边界，就用均值方差归一化
        """
        pass

    def save_data(self, unsaved_data):
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
        # 获取原始数据
        raw_data = self.get_data()
        # 进行数据的预处理
        handled_data = self.handle_data(raw_data)
        # 计算相应的推荐度指标
        self.calculate_recommend_score(handled_data)

        pass

    def sentiment_data_by_baidu(self, text, flag=0):
        """
        通过百度ai平台进行情感打分
        :param text:
        :param flag:表示该评论是否有score这个属性，如果没有需要返回score和setiment两个值(1代表没有score)
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
        try:
            res_dict = client.sentimentClassify(text)['items'][0]
            positive_prob = res_dict['positive_prob']
        except Exception as e:
            positive_prob = 0.5
            print(e)

        if flag == 0:
            return positive_prob

        # 如果该评论没有score这个属性，需要多返回一个score属性
        else:
            return positive_prob, positive_prob * 10

if __name__ == '__main__':
    sentiment_analyzer = SentimentAnalyzer()
    sentiment_analyzer.entrance()