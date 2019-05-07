# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import time
import pymysql
import pymysql.cursors
# 将mysql插入变成异步化的包，由twisted提供
from twisted.enterprise import adbapi
from elasticsearch_dsl.connections import connections


from JobHelpSpider.models.es_types import JobWantedInformationType
from JobHelpSpider import settings

es = connections.create_connection(hosts=[settings.ES_ADDRESS])


class JobhelpspiderPipeline(object):
    def process_item(self, item, spider):
        return item


class MysqlTwistPipeline(object):
    """
    数据异步插入mysql
    """
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        """
        spider会自动调用该方法，并且将settings作为参数传递进来
        :param settings:
        :return:
        """
        dbparams = dict(
        host=settings['MYSQL_HOST'],
        db=settings['MYSQL_DB'],
        passwd=settings['MYSQL_PASSWORD'],
        user=settings['MYSQL_USER'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        )
        dbpool = adbapi.ConnectionPool('pymysql', **dbparams)

        # 调用构造函数
        return cls(dbpool)

    def process_item(self, item, spider):
        # 会将插入变成异步的
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)

    def handle_error(self, failure, item, spider):
        """
        错误处理函数
        :param failure:
        :param item:
        :return:
        """
        print(failure)

    def do_insert(self, cursor, item):
        """
        执行jobbole数据的具体插入
        :param cursor:
        :param item:
        :return:
        """
        insert_sql = """
            replace into tb_job_wanted_information(url_object_id, content) values ('%s', '%s')
        """

        final_sql = insert_sql % (item['url_object_id'], item['content'].replace("'", '').replace('"', ''))
        # print(final_sql)
        cursor.execute(final_sql)


class ElasticSearchPipeline(object):
    """
    将数据写入到es中
    """
    def gen_suggests(self, index, info_tuple):
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

    def process_item(self, item, spider):
        """
        将item转换为es的数据格式
        :param item:
        :param spider:
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
        job_wanted_information.suggest = self.gen_suggests(JobWantedInformationType._doc_type.index,
                                                           ((job_wanted_information.title, 10),
                                                            (job_wanted_information.abstract, 6)))

        # 调用save方法直接存储到es中
        job_wanted_information.save()

        # 将相关的信息写入文件中查看分布式部署是否正常
        # with open('/home/yuzhou/scrapy_redis.txt', 'a') as f:
            # f.write('url:%s,title:%s\n' % (item['url'], item['title']))

        # 处理完后需要return这个item，让后面的pipeline进行处理
        return item

