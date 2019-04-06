# -*- coding: utf-8 -*-

from datetime import datetime
from elasticsearch_dsl import DocType, Date, Nested, Boolean, \
    analyzer, InnerObjectWrapper, Completion, Keyword, Text, Integer, Float

from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer

from elasticsearch_dsl.connections import connections
connections.create_connection(hosts=['60.205.224.136'])


class CustomAnalyzer(_CustomAnalyzer):
    """
    用来解决搜索建议相关源码报错问题的类
    """
    def get_analysis_definition(self):
        return []


ik_analyzer = CustomAnalyzer('ik_max_word', filter=['lowercase'])


class ArticleType(DocType):
    """
    技术文章类型，此处会影响搜索打分结果
    """
    # 搜索建议的mapping设置
    suggest = Completion(analyzer=ik_analyzer)

    url_object_id = Keyword()
    url = Keyword()
    title = Text(analyzer='ik_max_word')
    article_type = Text(analyzer='ik_max_word')
    data_source = Keyword()
    # 热度预留字段，由阅读数，评论数，点赞数，收藏数组成
    # hot_score = Float()
    publish_time = Date()
    abstract = Text(analyzer='ik_max_word')
    tags = Text(analyzer='ik_max_word')

    # 用来初始化index以及type的名称
    class Meta:
        # 类比到mysql就是数据库名
        index = 'technology_article'
        # 类比到mysql就是表名
        doc_type = 'article'


if __name__ == '__main__':
    # 初始化后可以直接连接到相应的es服务器进行
    ArticleType.init()
