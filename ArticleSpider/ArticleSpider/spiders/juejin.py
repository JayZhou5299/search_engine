# -*- coding: utf-8 -*-
import scrapy
import re
import time
import random
import datetime
import json
import requests

from scrapy.http import Request
from w3lib.html import remove_tags

from ArticleSpider.items import TechnicalArticleItem
from ArticleSpider.utils.common import get_md5


class JuejinSpider(scrapy.Spider):
    name = 'juejin'
    allowed_domains = ['juejin.im', 'web-api.juejin.im']
    start_urls = ['https://juejin.im']

    def parse(self, response):
        """
        解析具体网页
        :param response:
        :return:
        """
        headers = {
            'Host': 'web-api.juejin.im',
            'Referer': 'https://juejin.im',
            'Origin': 'https://juejin.im',
            'X-Agent': 'Juejin/Web',
            # 此处一定要设置为json格式，然后在post的data中为json的字符串(str)类型
            'Content-Type': 'application/json'
        }

        # 与post_data相对应的目录list
        category_data_list = ["5562b419e4b00c57d9b94ae2", "5562b415e4b00c57d9b94ac8",
                              "5562b410e4b00c57d9b94a92", "5562b405e4b00c57d9b94a41",
                              "57be7c18128fe1005fa902de", "5562b422e4b00c57d9b94b53"]
        category_data_list = [category_data_list[1]]
        post_data_list = ['{"operationName":"","query":"","variables":{"category":"5562b419e4b00c57'
                          'd9b94ae2","limit":15},"extensions":{"query":{"id":"801e22bdc908798e1c828'
                          'ba6b71a9fd9"}}}',
                          '{"operationName":"","query":"","variables":{"category":"5562b415e4b00c57'
                          'd9b94ac8","limit":15},"extensions":{"query":{"id":"801e22bdc908798e1c828'
                          'ba6b71a9fd9"}}}',
                          '{"operationName":"","query":"","variables":{"category":"5562b410e4b00c57'
                          'd9b94a92","limit":15},"extensions":{"query":{"id":"801e22bdc908798e1c828'
                          'ba6b71a9fd9"}}}',
                          '{"operationName":"","query":"","variables":{"category":"5562b405e4b00c57'
                          'd9b94a41","limit":15},"extensions":{"query":{"id":"801e22bdc908798e1c828'
                          'ba6b71a9fd9"}}}',
                          '{"operationName":"","query":"","variables":{"category":"57be7c18128fe100'
                          '5fa902de","limit":15},"extensions":{"query":{"id":"801e22bdc908798e1c828'
                          'ba6b71a9fd9"}}}',
                          '{"operationName":"","query":"","variables":{"category":"5562b422e4b00c57'
                          'd9b94b53","limit":15},"extensions":{"query":{"id":"801e22bdc908798e1c828'
                          'ba6b71a9fd9"}}}']
        post_data_list = [post_data_list[1]]
        post_data_model = '{"operationName":"","query":"","variables":{"tags":["%s"],' \
                          '"category":"%s","first":20,"after":"%s","order":"POPULAR"},' \
                          '"extensions":{"query":{"id":"653b587c5c7c8a00ddf67fc66f989d42"}}}'

        for post_data_obj in post_data_list:
            res = requests.post(url='https://web-api.juejin.im/query',
                                data=post_data_obj,
                                headers=headers)

            res_dict = json.loads(res.text)
            item_list = res_dict['data']['tagNav']['items']
            category = category_data_list[post_data_list.index(post_data_obj)]
            for item_obj in item_list:
                post_data = post_data_model % (item_obj['tagId'], category, random.random())
                yield Request(method='post', url='https://web-api.juejin.im/query',
                              body=post_data, headers=headers, callback=self.parse_crawl_urls,
                              meta={'headers': headers, 'post_data': post_data,
                                    'article_type': item_obj['title']})

    def parse_crawl_urls(self, response):
        """
        解析待爬取网页
        :param response:
        :return:
        """
        post_data = response.meta['post_data']
        headers = response.meta['headers']
        article_type = response.meta['article_type']

        res_dict = json.loads(response.text)
        item_list = res_dict['data']['articleFeed']['items']['edges']
        has_next = res_dict['data']['articleFeed']['items']['pageInfo']['hasNextPage']
        for item_obj in item_list:
            url = item_obj['node']['originalUrl']
            title = item_obj['node']['title']
            tags = [tag['title'] for tag in item_obj['node']['tags']]
            praise_num = item_obj['node']['likeCount']
            comment_num = item_obj['node']['commentsCount']
            publish_time = item_obj['node']['createdAt']
            yield Request(url=url, meta={'title': title, 'tags': ','.join(tags),
                                         'praise_num': praise_num, 'comment_num': comment_num,
                                         'article_type': article_type,
                                         'publish_time': publish_time}, callback=self.parse_detail)

        if has_next:
            time.sleep(3)
            post_data = re.sub(r'"after":"(.*)","order"',
                               '"after":"%s","order"' % random.random(),
                               post_data)
            yield Request(method='post', url='https://web-api.juejin.im/query',
                          body=post_data, headers=headers, callback=self.parse_crawl_urls,
                          meta={'headers': headers, 'post_data': post_data,
                                'article_type': article_type})

    def parse_detail(self, response):
        """
        解析网页细节
        :param response:
        :return:
        """
        juejin_item = TechnicalArticleItem()
        url = response.url
        read_num = response.css('.views-count::text').extract_first()
        if read_num:
            read_num = int(re.findall(r'(\d+)', read_num)[0])
        else:
            read_num = 0

        publish_time = re.findall(r'\d{4}-\d{2}-\d{2}', response.meta['publish_time'])[0]
        if publish_time:
            publish_time = datetime.datetime.strptime(publish_time, '%Y-%m-%d').date()

        abstract = response.css('.article-content').extract_first()
        juejin_item['url_object_id'] = get_md5(url)
        juejin_item['url'] = url
        juejin_item['title'] = response.meta['title']
        juejin_item['article_type'] = response.meta['article_type']
        juejin_item['data_source'] = '掘金'
        juejin_item['read_num'] = read_num
        juejin_item['comment_num'] = response.meta['comment_num']
        juejin_item['praise_num'] = response.meta['praise_num']
        juejin_item['collection_num'] = 0
        juejin_item['publish_time'] = publish_time
        juejin_item['abstract'] = remove_tags(abstract)[:300].replace('\t', '').replace('\r', '').replace('\n', '')
        juejin_item['tags'] = response.meta['tags']

        yield juejin_item
