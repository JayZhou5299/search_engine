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


class VideoType(DocType):
    """
    学习视频类型
    """
    # 搜索建议的mapping设置
    suggest = Completion(analyzer=ik_analyzer)

    url_object_id = Keyword()
    url = Keyword()
    class_name = Text(analyzer='ik_max_word')
    price = Float()
    abstract = Text(analyzer='ik_max_word')
    data_source = Keyword()
    second_classify = Text(analyzer='ik_max_word')
    first_classify = Text(analyzer='ik_max_word')
    # recommend_score = Float()

    # 用来初始化index以及type的名称
    class Meta:
        # 类比到mysql就是数据库名
        index = 'learning_video'
        # 类比到mysql就是表名
        doc_type = 'video'


if __name__ == '__main__':
    # 初始化后可以直接连接到相应的es服务器进行
    VideoType.init()
