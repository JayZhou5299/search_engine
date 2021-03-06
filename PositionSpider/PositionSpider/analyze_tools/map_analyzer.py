import json
import os
import pymysql
import random
import pymysql.cursors
import time
import redis
import re
import datetime

from PositionSpider import settings


# 创建一个连接池并从中获取redis连接
pool = redis.ConnectionPool(host='60.205.224.136', decode_responses=True)
redis_cli = redis.Redis(connection_pool=pool)


def get_province_city_mappping():
    """
    获取省市对应关系
    :return:返回值为字典形式，基于hash table实现，取数据的时间复杂度为o(1)
    """
    with open(os.path.abspath('province_city.txt'), 'r') as f:
        ret_data = f.readline()

    return json.loads(ret_data)


def get_data():
    """
    获取数据
    :return:返回值为list包dict类型
    """
    # 连接db并获取游标
    conn = pymysql.connect(host=settings.MYSQL_HOST,
                           user=settings.MYSQL_USER,
                           passwd=settings.MYSQL_PASSWORD,
                           db=settings.MYSQL_DB,
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()

    # 假设入库时已经完成了明确的分类
    sql = "select job_classify, working_place from tb_position_information"
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    return data


def classify_province():
    """
    按省份对数据进行分类
    :return:
    """
    # 获取待处理的数据
    data_list = get_data()

    # 直接初始化城市省份映射供后面函数使用
    province_city_mapping = get_province_city_mappping()

    for data_obj in data_list:
        province_name = province_city_mapping.get(data_obj['working_place'].strip())
        print(province_name)

        # 不能解析的省份写入，后续人为添加相关信息
        if province_name is None:
            with open('wrong_city_name.txt', 'a') as f:
                f.write('%s\t%s\n' % (data_obj['working_place'], datetime.datetime.now()))
        else:
            redis_cli.zincrby(province_name, 1, data_obj['job_classify'])
            # 对省份的总体数量进行记录
            redis_cli.incr('%s_' % province_name, 1)


def handle_and_formate_map():
    """
    对地图数据进行处理和整理
    :return:
    """
    province_list = ['北京', '天津', '上海', '重庆', '河北', '河南', '云南', '辽宁', '黑龙江', '湖南',
                     '安徽', '山东', '新疆', '江苏', '浙江', '江西', '湖北', '广西', '甘肃', '山西',
                     '内蒙古', '陕西', '吉林', '福建', '贵州', '广东', '青海', '西藏', '四川',
                     '宁夏', '海南', '台湾', '香港', '澳门']

    # 记录最大最小省份职位的数量
    min_amount = 10000000
    max_amount = 0

    for province_obj in province_list:
        # 如果没有amount_province就赋值为0
        amount_province = redis_cli.get('%s_' % province_obj)
        if not amount_province:
            amount_province = 0

        if min_amount > int(amount_province):
            min_amount = int(amount_province)

        if max_amount < int(amount_province):
            max_amount = int(amount_province)

        # 构造top3职位显示的字符串
        # 返回值eg:<class 'list'>: [('后端开发', 47.0), ('HTML5', 40.0), ('包装设计', 25.0)]
        top_list = redis_cli.zrevrange(province_obj, 0, 2, True)
        top_str = ''
        if top_list:
            for top_obj in top_list:
                top_str += '%s:%s\\n' % (top_obj[0], top_obj[1])
            # [: -2]是去掉最后一个换行符
            top_str = top_str[: -2]

        redis_cli.lpush('map_amount_list', '\t'.join([province_obj, str(amount_province), top_str]))

    redis_cli.set('map_min_amount', min_amount)
    redis_cli.set('map_max_amount', max_amount)


def entrance():
    """
    函数入口
    :return:
    """
    # classify_province()
    handle_and_formate_map()


if __name__ == '__main__':
    entrance()

