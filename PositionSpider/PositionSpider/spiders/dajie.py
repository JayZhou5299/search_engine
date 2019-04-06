# -*- coding: utf-8 -*-
import scrapy
import requests

from scrapy.selector import Selector
from scrapy.http import Request


class DajieSpider(scrapy.Spider):
    name = 'dajie'
    allowed_domains = ['www.dajie.com', 'so.dajie.com']
    start_urls = ['http://www.dajie.com/']

    def parse(self, response):
        """
        获取等待爬取的对象
        :param response:
        :return:
        """
        referer_model = 'https://so.dajie.com/job/search?positionFunction=%s&positionName=%s'
        real_url_model = 'https://so.dajie.com/job/ajax/search/filter?keyword=&order=0&city=&' \
                         'recruitType=&salary=&experience=&page=%d&positionFunction=%s&' \
                         '_CSRFToken=&ajax=1'
        # 只需要抓取互联网相关的职位信息即可
        crawl_node = response.css('.hn-detail-con')[1]
        # 获取a标签的列表
        crawl_a_list = crawl_node.css('li')
        for crawl_a_obj in crawl_a_list:
            function = crawl_a_obj.css('a::attr(id)').extract_first()
            name = crawl_a_obj.css('a::text').extract_first().replace('\n', '').replace('\r', '').strip()
            yield Request(url=real_url_model % (1, name))

            self.start_urls.append(referer_model % (function, name))
        pass

    def parse_crawl_urls(self, response):
        """
        解析真正获取到数据的响应列表
        :param response:
        :return:
        """

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