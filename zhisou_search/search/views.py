import json
import redis
from django.shortcuts import render
from django.views.generic.base import View
from django.http.response import HttpResponse
# elasticsearch-dsl是对elasticsearch做的更底层的封装
from elasticsearch import Elasticsearch

from search.models import VideoType
from search.models import JobWantedInformationType
from search.models import PositionType
from search.models import ArticleType
from zhisou_search import settings


client = Elasticsearch(hosts=[settings.ES_ADDRESS])

# 创建一个连接池并从中获取redis连接
pool = redis.ConnectionPool(host='182.92.193.60', decode_responses=True)
redis_cli = redis.Redis(connection_pool=pool)


# Create your views here.
class SearchSuggest(View):
    def handle_position_information(self, keywords):
        """
        处理岗位信息相关搜索建议
        :param request:
        :return:返回值为字典类型，html_object以及data_object，分别对应render函数的第二个和第三个参数
        """
        ret_data = list()
        s = PositionType.search()
        s = s.suggest('my_suggest', keywords, completion={
            'field': 'suggest',
            'fuzzy': {
                'fuzziness': 2
            },
            'size': 10
        })
        suggestion = s.execute_suggest()
        for suggestion_obj in suggestion.my_suggest[0].options:
            source = suggestion_obj._source
            ret_data.append(source['position_name'])

        return ret_data

    def handle_technical_article(self, keywords):
        """
        处理技术文章相关搜索建议
        :param request:
        :return:返回值为字典类型，html_object以及data_object，分别对应render函数的第二个和第三个参数
        """
        ret_data = list()
        s = ArticleType.search()
        s = s.suggest('my_suggest', keywords, completion={
            'field': 'suggest',
            'fuzzy': {
                'fuzziness': 2
            },
            'size': 10
        })
        suggestion = s.execute_suggest()
        for suggestion_obj in suggestion.my_suggest[0].options:
            source = suggestion_obj._source
            ret_data.append(source['title'])

        return ret_data

    def handle_job_wanted_information(self, keywords):
        """
        处理求职帮助相关搜索建议
        :param request:
        :return:返回值为字典类型，html_object以及data_object，分别对应render函数的第二个和第三个参数
        """
        ret_data = list()
        s = JobWantedInformationType.search()
        s = s.suggest('my_suggest', keywords, completion={
            'field': 'suggest',
            'fuzzy': {
                'fuzziness': 2
            },
            'size': 10
        })
        suggestion = s.execute_suggest()
        for suggestion_obj in suggestion.my_suggest[0].options:
            source = suggestion_obj._source
            ret_data.append(source['title'])

        return ret_data

    def handle_learning_video(self, keywords):
        """
        处理学习视频相关搜索建议
        :param request:
        :return:返回值为字典类型，html_object以及data_object，分别对应render函数的第二个和第三个参数
        """
        ret_data = list()
        s = VideoType.search()
        s = s.suggest('my_suggest', keywords, completion={
            'field': 'suggest',
            'fuzzy': {
                'fuzziness': 2
            },
            'size': 10
        })
        suggestion = s.execute_suggest()
        for suggestion_obj in suggestion.my_suggest[0].options:
            source = suggestion_obj._source
            ret_data.append(source['class_name'])

        return ret_data

    def get(self, request):
        """
        处理搜索建议提示的总函数
        :param request:
        :return:
        """
        # 设置keywords的默认值为空
        keywords = request.GET.get('s', '')
        ret_data = list()

        # x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        # if x_forwarded_for:
        #     ip = x_forwarded_for.split(',')[0]  # 所以这里是真实的ip
        # else:
        #     ip = request.META.get('REMOTE_ADDR')  # 这里获得代理ip
        #
        # print(ip)
        if keywords:
            # 根据不同的类型初始化不同的es查询对象
            suggest_type = request.GET.get('s_type', '')
            if suggest_type == 'article':
                ret_data = self.handle_technical_article(keywords)
            elif suggest_type == 'position':
                ret_data = self.handle_position_information(keywords)
            elif suggest_type == 'job_help':
                ret_data = self.handle_job_wanted_information(keywords)
            else:
                ret_data = self.handle_learning_video(keywords)

        return HttpResponse(json.dumps(ret_data), content_type='application/json')


class SearchView(View):
    def get(self, request):
        """
        处理跳转请求的总函数
        :param request:
        :return:
        """
        search_type = request.GET.get('s_type', '')
        keywords = request.GET.get('q', '')
        if keywords == '':
            return render(request, 'index.html')
        if search_type == 'job_help':
            res_dict = self.handle_job_wanted_information(request)
        elif search_type == 'video':
            res_dict = self.handle_learning_video(request)
        elif search_type == 'position':
            res_dict = self.handle_position_information(request)
        else:
            res_dict = self.handle_technical_article(request)

        # 根据不同的搜索跳转到不同的html页面
        if 'html_obj' in res_dict.keys() and 'data_obj' in res_dict.keys():
            return render(request, res_dict['html_obj'], res_dict['data_obj'])
        else:
            return render(request, 'error.html')

    def handle_position_information(self, request):
        """
        处理岗位信息相关搜索
        :param request:
        :return:返回值为字典类型，html_object以及data_object，分别对应render函数的第二个和第三个参数
        """
        map_amount_list = list()
        map_min_amount = redis_cli.get('map_min_amount')
        map_max_amount = redis_cli.get('map_max_amount')

        map_amount_str_list = redis_cli.lrange('map_amount_list', 0, -1)
        for map_amount_str_obj in map_amount_str_list:
            map_amount_list.append(map_amount_str_obj.split('\t'))

        keywords = request.GET.get('q', '')
        page = request.GET.get('p', '1')

        # 转换可能报异常，报错默认为第一页
        try:
            page = int(page)
        except Exception as e:
            page = 1

        response = client.search(
            index='position_message',
            body={
                'query': {
                    "multi_match": {
                        'query': keywords,
                        # 只要这四个属性中任意一个属性包含keywords的分词结果列表中的词，该条doc就会被查出来
                        'fields': ['position_name', 'company_name', 'abstract', 'working_place']
                    }
                },
                'from': (page - 1) * 10,
                'size': 10,
                'highlight': {
                    # 高亮数据的标红样式，可以自己定义，前端设置的css样式为keyWord，
                    'pre_tags': ['<span class="keyWord">'],
                    'post_tags': ['</span>'],
                    'fields': {
                        'position_name': {},
                        'company_name': {},
                        'abstract': {},
                        'working_place': {}
                    }
                }
            }
        )
        total_nums = response['hits']['total']
        page_nums = int(total_nums / 10) + 1

        hit_list = []
        for hit_obj in response['hits']['hits']:
            hit_dict = dict()
            if 'highlight' in hit_obj.keys() and 'position_name' in hit_obj['highlight']:
                hit_dict['position_name'] = hit_obj['highlight']['position_name'][0]
            else:
                hit_dict['position_name'] = hit_obj['_source'].get('position_name', '这个岗位丢失了')

            if 'highlight' in hit_obj.keys() and 'abstract' in hit_obj['highlight']:
                hit_dict['abstract'] = hit_obj['highlight']['abstract'][0]
            else:
                hit_dict['abstract'] = hit_obj['_source'].get('abstract', '这个页面丢失了')

            if 'highlight' in hit_obj.keys() and 'company_name' in hit_obj['highlight']:
                hit_dict['company_name'] = hit_obj['highlight']['company_name'][0]
            else:
                hit_dict['company_name'] = hit_obj['_source'].get('company_name', '无')

            if 'highlight' in hit_obj.keys() and 'working_place' in hit_obj['highlight']:
                hit_dict['working_place'] = hit_obj['highlight']['working_place'][0]
            else:
                hit_dict['working_place'] = hit_obj['_source'].get('working_place', '无')
            try:
                hit_dict['data_source'] = hit_obj['_source']['data_source']
                hit_dict['url'] = hit_obj['_source']['url']
                hit_dict['working_exp'] = hit_obj['_source']['working_exp']
                hit_dict['salary_min'] = hit_obj['_source']['salary_min']
                hit_dict['salary_max'] = hit_obj['_source']['salary_max']
                hit_dict['welfare'] = hit_obj['_source']['welfare']
                hit_dict['education'] = hit_obj['_source']['education']
                hit_dict['score'] = hit_obj['_score']
            except Exception as e:
                continue
            hit_list.append(hit_dict)

        return {'html_obj': 'result_position.html', 'data_obj': {'page': page, 'all_hits': hit_list,
                                                                 'key_words': keywords,
                                                                 'total_nums': total_nums,
                                                                 'page_nums': page_nums,
                                                                 'map_amount_list': map_amount_list,
                                                                 'map_max_amount': map_max_amount,
                                                                 'map_min_amount': map_min_amount}}

    def handle_technical_article(self, request):
        """
        处理技术文章相关搜索
        :param request:
        :return:返回值为字典类型，html_object以及data_object，分别对应render函数的第二个和第三个参数
        """
        word_cloud_dict = dict()
        # 获取top的类别名称
        top_list = redis_cli.lrange('top_list', 0, 10)
        # 根据类别名称获取相应的top200词与频次
        for top_obj in top_list:
            word_cloud_dict[top_obj] = redis_cli.hgetall(top_obj)

        keywords = request.GET.get('q', '')
        page = request.GET.get('p', '1')

        # 转换可能报异常，报错默认为第一页
        try:
            page = int(page)
        except Exception as e:
            page = 1

        response = client.search(
            index='technology_article',
            body={
                'query': {
                    "multi_match": {
                        'query': keywords,
                        # 只要这四个属性中任意一个属性包含keywords的分词结果列表中的词，该条doc就会被查出来
                        'fields': ['title', 'article_type', 'abstract', 'tags']
                    }
                },
                'from': (page - 1) * 10,
                'size': 10,
                'highlight': {
                    # 高亮数据的标红样式，可以自己定义，前端设置的css样式为keyWord，
                    'pre_tags': ['<span class="keyWord">'],
                    'post_tags': ['</span>'],
                    'fields': {
                        'title': {},
                        'article_type': {},
                        'abstract': {},
                        'tags': {}
                    }
                }
            }
        )
        total_nums = response['hits']['total']
        page_nums = int(total_nums / 10) + 1

        hit_list = []
        for hit_obj in response['hits']['hits']:
            hit_dict = dict()
            if 'highlight' in hit_obj.keys() and 'title' in hit_obj['highlight']:
                hit_dict['title'] = ''.join(hit_obj['highlight']['title'])
            else:
                hit_dict['title'] = hit_obj['_source']['title']

            if 'highlight' in hit_obj.keys() and 'abstract' in hit_obj['highlight']:
                hit_dict['abstract'] = ''.join(hit_obj['highlight']['abstract'])
            else:
                hit_dict['abstract'] = hit_obj['_source'].get('abstract', '这个页面丢失了')

            if 'highlight' in hit_obj.keys() and 'article_type' in hit_obj['highlight']:
                hit_dict['article_type'] = hit_obj['highlight']['article_type'][0]
            else:
                hit_dict['article_type'] = hit_obj['_source'].get('article_type', '无')

            if 'highlight' in hit_obj.keys() and 'tags' in hit_obj['highlight']:
                hit_dict['tags'] = hit_obj['highlight']['tags'][0]
            else:
                hit_dict['tags'] = hit_obj['_source'].get('tags', '无')

            try:
                hit_dict['data_source'] = hit_obj['_source']['data_source']
                hit_dict['url'] = hit_obj['_source']['url']
                hit_dict['publish_time'] = hit_obj['_source']['publish_time']
                hit_dict['hot_score'] = hit_obj['_source']['hot_score']
                hit_dict['score'] = hit_obj['_score']
            except Exception as e:
                continue
            hit_list.append(hit_dict)

        return {'html_obj': 'result_article.html', 'data_obj': {'page': page, 'all_hits': hit_list,
                                                                'key_words': keywords,
                                                                'total_nums': total_nums,
                                                                'page_nums': page_nums,
                                                                'word_cloud_dict': word_cloud_dict}}

    def handle_learning_video(self, request):
        """
        处理学习视频相关搜索
        :param request:
        :return:返回值为字典类型，html_object以及data_object，分别对应render函数的第二个和第三个参数
        """
        keywords = request.GET.get('q', '')
        page = request.GET.get('p', '1')

        pie_dict = redis_cli.hgetall('pie_dict')
        pie_list = redis_cli.lrange('pie_list', 0, 30)

        # 转换可能报异常，报错默认为第一页
        try:
            page = int(page)
        except Exception as e:
            page = 1

        response = client.search(
            index='learning_video',
            body={
                'query': {
                    "multi_match": {
                        'query': keywords,
                        # 只要这四个属性中任意一个属性包含keywords的分词结果列表中的词，该条doc就会被查出来
                        'fields': ['class_name', 'first_classify', 'second_classify', 'abstract']
                    }
                },
                'from': (page - 1) * 10,
                'size': 10,
                'highlight': {
                    # 高亮数据的标红样式，可以自己定义，前端设置的css样式为keyWord，
                    'pre_tags': ['<span class="keyWord">'],
                    'post_tags': ['</span>'],
                    'fields': {
                        'class_name': {},
                        'abstract': {},
                        'first_classify': {},
                        'second_classify': {}
                    }
                }
            }
        )
        total_nums = response['hits']['total']
        page_nums = int(total_nums / 10) + 1

        hit_list = []
        for hit_obj in response['hits']['hits']:
            hit_dict = dict()
            if 'highlight' in hit_obj.keys() and 'class_name' in hit_obj['highlight']:
                hit_dict['class_name'] = ''.join(hit_obj['highlight']['class_name'])
            else:
                hit_dict['class_name'] = hit_obj['_source']['class_name']

            if 'highlight' in hit_obj.keys() and 'abstract' in hit_obj['highlight']:
                hit_dict['abstract'] = ''.join(hit_obj['highlight']['abstract'])
            else:
                hit_dict['abstract'] = hit_obj['_source'].get('abstract', '这个页面丢失了')

            if 'highlight' in hit_obj.keys() and 'first_classify' in hit_obj['highlight']:
                hit_dict['first_classify'] = hit_obj['highlight']['first_classify'][0]
            else:
                hit_dict['first_classify'] = hit_obj['_source'].get('first_classify', '无')

            if 'highlight' in hit_obj.keys() and 'second_classify' in hit_obj['highlight']:
                hit_dict['second_classify'] = hit_obj['highlight']['second_classify'][0]
            else:
                hit_dict['second_classify'] = hit_obj['_source'].get('second_classify', '无')
            try:
                hit_dict['data_source'] = hit_obj['_source']['data_source']
                hit_dict['url'] = hit_obj['_source']['url']
                hit_dict['price'] = hit_obj['_source']['price']
                hit_dict['score'] = hit_obj['_score']
                hit_dict['recommend_score'] = hit_obj['_source']['recommend_score']
            except Exception as e:
                continue
            hit_list.append(hit_dict)

        return {'html_obj': 'result_video.html', 'data_obj': {'page': page, 'all_hits': hit_list,
                                                              'key_words': keywords,
                                                              'total_nums': total_nums,
                                                              'page_nums': page_nums,
                                                              'pie_list': pie_list,
                                                              'pie_dict': pie_dict}}

    def handle_job_wanted_information(self, request):
        """
        处理求职信息相关搜索
        :return:返回值为字典类型，html_object以及data_object，分别对应render函数的第二个和第三个参数
        """
        col_list = redis_cli.lrange('bar_chart_col', 0, -1)
        row_list = redis_cli.lrange('bar_chart_row', 0, -1)
        bar_chart_interval = redis_cli.get('bar_chart_interval')
        bar_chart_max = redis_cli.get('bar_chart_max')

        keywords = request.GET.get('q', '')
        page = request.GET.get('p', '1')

        # 转换可能报异常，报错默认为第一页
        try:
            page = int(page)
        except Exception as e:
            page = 1

        response = client.search(
            index='job_help',
            body={
                'query': {
                    "multi_match": {
                        'query': keywords,
                        # 只要这两个属性中任意一个属性包含keywords的分词结果列表中的词，该条doc就会被查出来
                        'fields': ['title', 'abstract']
                    }
                },
                'from': (page - 1) * 10,
                'size': 10,
                'highlight': {
                    # 高亮数据的标红样式，可以自己定义，前端设置的css样式为keyWord，
                    'pre_tags': ['<span class="keyWord">'],
                    'post_tags': ['</span>'],
                    'fields': {
                        'title': {},
                        'abstract': {},
                    }
                }
            }
        )

        total_nums = response['hits']['total']
        page_nums = int(total_nums / 10) + 1

        hit_list = []
        for hit_obj in response['hits']['hits']:
            hit_dict = dict()
            if 'highlight' in hit_obj.keys() and 'title' in hit_obj['highlight']:
                hit_dict['title'] = ''.join(hit_obj['highlight']['title'])
            else:
                hit_dict['title'] = hit_obj['_source']['title']

            if 'highlight' in hit_obj.keys() and 'abstract' in hit_obj['highlight']:
                hit_dict['abstract'] = ''.join(hit_obj['highlight']['abstract'])
            else:
                hit_dict['abstract'] = hit_obj['_source'].get('abstract', '这个页面丢失了')
            try:
                hit_dict['data_source'] = hit_obj['_source']['data_source']
                hit_dict['url'] = hit_obj['_source']['url']
                hit_dict['publish_time'] = hit_obj['_source']['publish_time']
                hit_dict['score'] = hit_obj['_score']
            except Exception as e:
                continue
            hit_list.append(hit_dict)

        return {'html_obj': 'result_job_wanted_information.html',
                'data_obj': {'page': page, 'all_hits': hit_list, 'key_words': keywords,
                             'total_nums': total_nums, 'page_nums': page_nums,
                             'col_list': col_list, 'row_list': row_list,
                             'bar_chart_max': bar_chart_max,
                             'bar_chart_interval': bar_chart_interval}}


if __name__ == '__main__':
    search_view = SearchView()
    search_view.get()

