# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
import pymysql.cursors

# 将mysql插入变成异步化的包，由twisted提供
from twisted.enterprise import adbapi
from elasticsearch_dsl.connections import connections
from PositionSpider.models.es_types import PositionType
from PositionSpider import settings

es = connections.create_connection(hosts=[settings.ES_ADDRESS])


class PositionspiderPipeline(object):
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
        # 将错误的信息写入log文件中
        with open('insert_error_position.log', 'a') as f:
            f.write(failure)

    def do_insert(self, cursor, item):
        """
        执行jobbole数据的具体插入
        :param cursor:
        :param item:
        :return:
        """
        insert_sql = """
            replace into tb_position_information(url_object_id, working_place, job_classify)
            values ('%s', '%s', '%s')
        """
        final_sql = insert_sql % (item['url_object_id'], item['working_place'], item['job_classify'])
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
                # 调用es的analyze接口分析字符串(主要作用是分词)
                words = es.indices.analyze(index=index, analyzer='ik_max_word',
                                            params={'filter':['lowercase']}, body=text)

                # 将长度为小于等于1的词过滤掉，这种词没有意义
                analyzed_words = set([r['token'] for r in words['tokens'] if len(r['token']) > 1])

                # 将之前用过的词去掉
                new_words = analyzed_words - used_words
            else:
                new_words = set()

            # 如果存在新词就将其添加到建议数组中，在used_words中添加这些词
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
        position = PositionType()
        # 将该条document的id设置为url_object_id
        position.meta.id = item['url_object_id']

        position.url = item['url']
        position.position_name = item['position_name']
        position.salary_min = item['salary_min']
        position.salary_max = item['salary_max']
        position.welfare = item['welfare']
        position.working_place = item['working_place']
        position.working_exp = item['working_exp']
        position.education = item['education']
        position.abstract = item['abstract']
        position.data_source = item['data_source']
        position.company_name = item['company_name']

        # 传入的元组需要按权值从大到小排列
        position.suggest = self.gen_suggests(PositionType._doc_type.index,
                                          ((position.position_name, 10), (position.company_name, 8)))

        # 调用save方法直接存储到es中
        position.save()

        return item
