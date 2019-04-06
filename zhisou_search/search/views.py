import json
from django.shortcuts import render
from django.views.generic.base import View
from django.http.response import HttpResponse
from search.models import VideoType
from search.models import JobWantedInformationType
# elasticsearch-dsl是对elasticsearch做的更底层的封装
from elasticsearch import Elasticsearch


client = Elasticsearch(hosts=['60.205.224.136'])


# Create your views here.
class SearchSuggest(View):
    def handle_position_information(self, request):
        """
        处理岗位信息相关搜索建议
        :param request:
        :return:返回值为字典类型，html_object以及data_object，分别对应render函数的第二个和第三个参数
        """
        pass

    def handle_technical_article(self, request):
        """
        处理技术文章相关搜索建议
        :param request:
        :return:返回值为字典类型，html_object以及data_object，分别对应render函数的第二个和第三个参数
        """
        pass

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

        if keywords:
            # 根据不同的类型初始化不同的es查询对象
            suggest_type = request.GET.get('s_type', '')
            if suggest_type == 'article':
                pass
            elif suggest_type == 'position':
                pass
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
        pass

    def handle_technical_article(self, request):
        """
        处理技术文章相关搜索
        :param request:
        :return:返回值为字典类型，html_object以及data_object，分别对应render函数的第二个和第三个参数
        """
        pass

    def handle_learning_video(self, request):
        """
        处理学习视频相关搜索
        :param request:
        :return:返回值为字典类型，html_object以及data_object，分别对应render函数的第二个和第三个参数
        """
        keywords = request.GET.get('q', '')
        page = request.GET.get('p', '1')

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
            if 'class_name' in hit_obj['highlight']:
                hit_dict['class_name'] = ''.join(hit_obj['highlight']['class_name'])
            else:
                hit_dict['class_name'] = hit_obj['_source']['class_name']

            if 'abstract' in hit_obj['highlight']:
                hit_dict['abstract'] = ''.join(hit_obj['highlight']['abstract'])
            else:
                hit_dict['abstract'] = hit_obj['_source']['abstract']

            if 'first_classify' in hit_obj['highlight']:
                hit_dict['first_classify'] = hit_obj['highlight']['first_classify'][0]
            else:
                hit_dict['first_classify'] = hit_obj['_source']['first_classify']

            if 'second_classify' in hit_obj['highlight']:
                hit_dict['second_classify'] = hit_obj['highlight']['second_classify'][0]
            else:
                hit_dict['second_classify'] = hit_obj['_source']['second_classify']

            hit_dict['data_source'] = hit_obj['_source']['data_source']
            hit_dict['url'] = hit_obj['_source']['url']
            hit_dict['price'] = hit_obj['_source']['price']
            hit_dict['score'] = hit_obj['_score']
            hit_list.append(hit_dict)

        return {'html_obj': 'result_video.html', 'data_obj': {'page': page, 'all_hits': hit_list,
                                                              'key_words': keywords,
                                                              'total_nums': total_nums,
                                                              'page_nums': page_nums}}

    def handle_job_wanted_information(self, request):
        """
        处理求职信息相关搜索
        :return:返回值为字典类型，html_object以及data_object，分别对应render函数的第二个和第三个参数
        """
        keywords = request.GET.get('q', '')
        page = request.GET.get('p', '1')
        pass


if __name__ == '__main__':
    search_view = SearchView()
    search_view.get()

