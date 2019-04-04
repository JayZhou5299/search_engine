# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
import pymysql.cursors
import traceback

# 将mysql插入变成异步化的包，由twisted提供
from twisted.enterprise import adbapi

class ArticlespiderPipeline(object):
    def process_item(self, item, spider):

        return item


# class MysqlPipeline(object):
#     """
#     将数据插入mysql中异步化
#     """
#     def __init__(self):
#         self.conn = pymysql.connect(host='60.205.224.136', user='root', password='123456',
#                                     db='search_engine_test', charset='utf8')
#         self.cursor = self.conn.cursor()
#
#     def process_item(self, item, spider):
#         insert_sql = """
#             insert into tb_technical_articles(url_object_id, url, title, article_type, data_source,
#             read_num, comment_num, praise_num, collection_num, publish_time, abstract, content)
#             values (%s, %s, %s, %s, %s, %d, %d, %d, %d, %s, %s, %s)
#         """
#         self.cursor.execute(insert_sql)

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
        host = settings['MYSQL_HOST'],
        db = settings['MYSQL_DB'],
        passwd = settings['MYSQL_PASSWORD'],
        user = settings['MYSQL_USER'],
        charset = 'utf8',
        cursorclass = pymysql.cursors.DictCursor,
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
            replace into tb_technical_articles(url_object_id, url, title, article_type, data_source,
            read_num, comment_num, praise_num, collection_num, publish_time, abstract, content, tags)
            values ('%s', '%s', '%s', '%s', '%s', %d, %d, %d, %d, '%s', '%s', '%s', '%s')
        """
        # print('test')
        final_sql = insert_sql % (item['url_object_id'], item['url'], item['title'], item['article_type'],
                                  item['data_source'], item['read_num'], item['comment_num'], item['praise_num'],
                                  item['collection_num'], item['publish_time'], item['abstract'],
                                  item['content'], item['tags'])
        # print(final_sql)
        cursor.execute(final_sql)
