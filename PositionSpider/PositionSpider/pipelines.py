# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
import pymysql.cursors

# 将mysql插入变成异步化的包，由twisted提供
from twisted.enterprise import adbapi
from elasticsearch_dsl.connections import connections

es = connections.create_connection(hosts=['60.205.224.136'])


class PositionspiderPipeline(object):
    def process_item(self, item, spider):
        return item
