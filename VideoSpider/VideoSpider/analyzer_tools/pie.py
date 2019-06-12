import pymysql
import redis
import pymysql.cursors


from VideoSpider import settings


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
    sql = "select classify, count(1) as num from tb_learning_video" \
          " group by classify order by num desc;"

    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    return data


def entrace():
    """
    函数入口
    :return:
    """
    redis_cli = redis.Redis(host=settings.REDIS_ADDRESS, port=6379)
    data_list = get_data()
    for data_obj in data_list:
        redis_cli.rpush('pie_list', data_obj['classify'])
        redis_cli.hset('pie_dict', data_obj['classify'], data_obj['num'])


if __name__ == '__main__':
    entrace()
