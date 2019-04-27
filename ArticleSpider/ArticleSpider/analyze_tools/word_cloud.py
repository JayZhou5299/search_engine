import jieba
import os
import redis
import pymysql
import collections

from ArticleSpider import settings

conn = pymysql.connect(host=settings.MYSQL_HOST,
                       user=settings.MYSQL_USER,
                       passwd=settings.MYSQL_PASSWORD,
                       db=settings.MYSQL_DB,
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

# 创建一个连接池并从中获取redis连接
pool = redis.ConnectionPool(host='60.205.224.136', decode_responses=True)
redis_cli = redis.Redis(connection_pool=pool)


def get_data(article_type):
    """
    获取数据
    :return:
    """
    conn.ping(reconnect=True)
    cursor = conn.cursor()

    # 假设入库时已经完成了明确的分类
    sql = "select title, tags from tb_technical_articles where article_type='%s'" % article_type
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    return data


def load_stop_words():
    """
    获取停用词列表
    :return:
    """
    with open(os.path.join(os.path.abspath('.'), 'stop_words.txt'), 'r') as f:
        stop_words = f.readlines()

    return tuple(stop_word.strip() for stop_word in stop_words)


# 直接加载停用词列表
stop_words_list = load_stop_words()


def remove_stop_words(seg_list):
    """
    去除列表中的停用词
    :return:
    """
    res_list = list()
    for seg_obj in seg_list:
        if seg_obj != ' ' and seg_obj not in stop_words_list:
            res_list.append(seg_obj)

    return res_list


def cal_top_article_type():
    """
    获取数据量最多（即最热）的6个文章类别，打算制作6个词云
    ps：假设数据库中的article类别已经处理过
    :return:
    """
    top_article_type = list()

    cursor = conn.cursor()
    sql = "select count(1) as num, article_type from tb_technical_articles " \
          "group by article_type order by num desc limit 6"
    cursor.execute(sql)
    data_list = cursor.fetchall()
    cursor.close()
    conn.close()

    # 取出top6的文章类别
    for data_obj in data_list:
        top_article_type.append(data_obj['article_type'])

    # 计算一次很耗时，所以计算一次后将数据存到txt中
    with open(os.path.join(os.path.abspath('.'), 'top_article_type.txt'), 'w') as f:
        f.write('\t'.join(top_article_type))


def entrance():
    """
    函数入口
    :return:
    """
    # 1.加载top的文章类别
    with open(os.path.join(os.path.abspath('.'), 'top_article_type.txt'), 'r') as f:
        top_list = f.readline().split('\t')

    # 2.取相应article_type的数据制作词云
    for top_obj in top_list:
        data_list = get_data(top_obj)

        top_obj_all_words = list()
        for data_obj in data_list:
            seg_list = jieba.cut(data_obj['title'], cut_all=False)
            # seg_list = remove_stop_words(list(seg_list))
            # 将标签也添加进分词处理后的词列表中
            top_obj_all_words.extend(list(seg_list))
            top_obj_all_words.extend(data_obj['tags'].split(','))

        # 计算词语的频次(top200)，返回结果为list包tuple类型
        res_list = collections.Counter(remove_stop_words(top_obj_all_words)).most_common(200)

        # 3.将频次放进redis中
        for res_obj in res_list:
            redis_cli.hset(top_obj, res_obj[0], res_obj[1])

        # 4.将top6的文章类别也写入redis中
        redis_cli.lpush('top_list', top_obj)


if __name__ == '__main__':
    # cal_top_article_type()
    entrance()

