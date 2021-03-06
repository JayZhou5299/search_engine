from django.db import models
from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch_dsl import DocType, Date, Nested, Boolean, \
    analyzer, InnerObjectWrapper, Completion, Keyword, Text, Integer, Float
from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer
from elasticsearch_dsl.connections import connections

from zhisou_search import settings

connections.create_connection(hosts=[settings.ES_ADDRESS])


# Create your models here.
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
    learner_nums = Integer()
    class_nums = Integer()
    category = Keyword()
    abstract = Text(analyzer='ik_max_word')
    data_source = Keyword()
    institution = Keyword()
    second_classify = Text(analyzer='ik_max_word')
    evaluation_score = Float()
    evaluation_person = Integer()
    fit_people = Text(analyzer='ik_max_word')
    first_classify = Text(analyzer='ik_max_word')
    evaluation_content = Keyword()

    # 用来初始化index以及type的名称
    class Meta:
        # 类比就是mysql的数据库名称
        index = 'learning_video'
        # 类比就是mysql的表名称
        doc_type = 'video'


class JobWantedInformationType(DocType):
    """
    求职信息类型
    """
    # 搜索建议的mapping设置
    suggest = Completion(analyzer=ik_analyzer)

    url_object_id = Keyword()
    url = Keyword()
    title = Text(analyzer='ik_max_word')
    publish_time = Date()
    content = Keyword()
    data_source = Keyword()
    abstract = Text(analyzer='ik_max_word')

    # 用来初始化index以及type的名称
    class Meta:
        # 类比到mysql就是数据库名
        index = 'job_help'
        # 类比到mysql就是表名
        doc_type = 'job_wanted_information'


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
    hot_score = Integer()
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
    pass

