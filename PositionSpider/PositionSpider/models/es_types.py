# -*- coding: utf-8 -*-

from datetime import datetime
from elasticsearch_dsl import DocType, Date, Nested, Boolean, \
    analyzer, InnerObjectWrapper, Completion, Keyword, Text, Integer, Float

from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer
from elasticsearch_dsl.connections import connections

from PositionSpider import settings

connections.create_connection(hosts=[settings.ES_ADDRESS])


class CustomAnalyzer(_CustomAnalyzer):
    """
    用来解决搜索建议相关源码报错问题的类
    """
    def get_analysis_definition(self):
        return []


ik_analyzer = CustomAnalyzer('ik_max_word', filter=['lowercase'])


class PositionType(DocType):
    """
    学习视频类型
    """
    # 搜索建议的mapping设置
    suggest = Completion(analyzer=ik_analyzer)

    url_object_id = Keyword()
    url = Keyword()
    position_name = Text(analyzer='ik_max_word')
    salary_min = Float()
    salary_max = Float()
    welfare = Keyword()
    working_place = Keyword()
    working_exp = Keyword()
    education = Keyword()
    abstract = Text(analyzer='ik_max_word')
    data_source = Keyword()
    company_name = Text(analyzer='ik_max_word')

    # 用来初始化index以及type的名称
    class Meta:
        # 类比到mysql就是数据库名
        index = 'position_message'
        # 类比到mysql就是表名
        doc_type = 'position'


if __name__ == '__main__':
    # 初始化后可以直接连接到相应的es服务器进行
    PositionType.init()
