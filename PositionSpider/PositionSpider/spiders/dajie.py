# -*- coding: utf-8 -*-
import scrapy
import time
import random
import requests

from scrapy.selector import Selector
from scrapy.http import Request


class DajieSpider(scrapy.Spider):
    name = 'dajie'
    allowed_domains = ['www.dajie.com', 'so.dajie.com']
    start_urls = ['http://www.dajie.com/']


    def parse(self, response):
        """
        提取抓取的相关模块
        :param response:
        :return:
        """
        # it相关的只有一个分类
        it_classify_node = response.css('.hn-detail-con')[1]

        for it_classify_node_obj in it_classify_node:
            url_list = it_classify_node_obj.css('a::attr(href)').extract()
            job_classify_list = it_classify_node_obj.css('a::text').extract()

            for url_obj in url_list:
                # time.sleep(random.randint(2, 4))
                job_classify = job_classify_list[url_list.index(url_obj)]
                yield Request(url=url_obj, callback=self.parse_crawl_urls,
                              meta={'job_classify': job_classify})

    def parse_crawl_urls(self, response):
        """
        提取待抓取url
        :param response:
        :return:
        """
        'https://so.dajie.com/job/ajax/search/filter?keyword=&order=0&city=&recruitType=' \
        '&salary=&experience=&page=1&positionFunction=130202&_CSRFToken=&ajax=1'


        crawl_urls = response.css('.content_left .position_link::attr(href)').extract()
        for crawl_url in crawl_urls:
            time.sleep(random.randint(2, 4))
            yield Request(url=crawl_url, callback=self.parse_detail,
                          meta={'job_classify': response.meta['job_classify']})

        # 如果没有下一页直接return即可
        no_next_tag = response.css('.pager_next_disabled')
        if no_next_tag:
            return

        # 最后一个元素是下一页的标签
        next_url = response.css('.page_no::attr(href)').extract()[-1]
        yield Request(url=next_url, callback=self.parse_crawl_urls,
                      meta={'job_classify': response.meta['job_classify']})

        pass

    def parse_detail(self, response):
        """
        解析网页细节
        :param response:
        :return:
        """
        url = response.url
        pass
"""
 `url_object_id` varchar(64) NOT NULL COMMENT '对url做md5生成的ID',
  `url` varchar(512) NOT NULL,
  `position_name` varchar(128) NOT NULL COMMENT '岗位名称',
  `salary_min` int(11) NOT NULL DEFAULT '0' COMMENT '最低年薪',
  `salary_max` int(11) NOT NULL DEFAULT '0' COMMENT '最高年薪',
  `welfare` varchar(128) NOT NULL COMMENT '福利',
  `working_place` varchar(64) DEFAULT NULL COMMENT '工作地点',
  `working_exp` tinyint(4) DEFAULT NULL COMMENT '工作经验底限，由于是针对大学生，所以工作经验不要求',
  `education` varchar(32) DEFAULT NULL COMMENT '学历要求',
  `working_type` varchar(32) DEFAULT NULL COMMENT '工作性质，全职实习兼职等',
  `position_num` int(11) DEFAULT NULL COMMENT '招聘人数',
  abstract varchar(256) comment '摘要，包括岗位信息，办公环境，办公时间等'
  `Responsibility` text COMMENT '岗位职责',
  `data_source` varchar(32) NOT NULL COMMENT '数据来源',
  `publish_time` date NOT NULL DEFAULT '0000-00-00' COMMENT '发表日期',
  `other_message` text COMMENT '其他信息，如办公环境，办公时间等',
"""