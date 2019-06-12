import pymysql
from DBUtils.PooledDB import PooledDB

from VideoSpider import settings
from elasticsearch import Elasticsearch


pool = PooledDB(pymysql, 5, host=settings.MYSQL_HOST,
                user=settings.MYSQL_USER, passwd=settings.MYSQL_PASSWORD,
                db=settings.MYSQL_DB, port=3306, charset='utf8mb4')  # 5为连接池里的最少连接数


def update_data(id, classify):
    """
    获取数据
    :return:返回值为list包dict类型
    """
    # 连接db并获取游标
    conn = pool.connection()
    cursor = conn.cursor()
    sql = 'update tb_learning_video set classify="%s" where url_object_id="%s"' % (classify, id)

    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()


# def entrace():
#     """
#     函数入口
#     :return:
#     """
#     es_client = Elasticsearch(hosts=[settings.ES_ADDRESS], timeout=80,
#                               max_retries=10, retry_on_timeout=True)
#     for i in range(11, 20):
#         res = es_client.search(index='learning_video', doc_type='video', body={
#             "query": {
#                 "match_all": {}
#             },
#             "_source": ['first_classify'],
#             "from": 500 * (i - 1),
#             "size": 500 * i
#         })
#
#         data_list = res['hits']['hits']
#         for data_obj in data_list:
#             id = data_obj['_id']
#             print('%s   %d' % (id, i))
#             try:
#                 classify = data_obj['_source']['first_classify']
#                 update_data(id, classify)
#             except Exception as e:
#                 with open('/Users/hanyuzhou/fail.txt', 'a') as f:
#                     f.write('%s\n' % id)

def get_id():
    conn = pool.connection()
    cursor = conn.cursor()
    sql = 'select url_object_id from tb_learning_video';

    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data


def entrance():
    es_client = Elasticsearch(hosts=[settings.ES_ADDRESS], timeout=80,
                              max_retries=10, retry_on_timeout=True)
    data_list = get_id()
    for data_obj in data_list:
        url_object_id = data_obj[0]
        res = es_client.get(index='learning_video', doc_type='video', id=url_object_id)
        update_data(url_object_id, res['_source']['first_classify'])


def delete_es(id):
    """
    删除es的数据
    :return:
    """
    es_client = Elasticsearch(hosts=[settings.ES_ADDRESS], timeout=80,
                              max_retries=10, retry_on_timeout=True)
    es_client.delete(index='learning_video', doc_type='video', id=id)


def count_es():
    """
    统计es中数据的条数
    :return:
    """
    es_client = Elasticsearch(hosts=[settings.ES_ADDRESS], timeout=80,
                              max_retries=10, retry_on_timeout=True)

    res = es_client.search(index='learning_video', doc_type='video', body={
        "query":{
            'bool':{
                'must_not':{
                    'exists': {
                        'field': 'recommend_score'
                    }
                }
            }
        },
        'from': 0,
        'size': 200
    })
    res_list = res['hits']['hits']
    # for res_obj in res_list:
    #     delete_es(res_obj['_id'])
    pass


if __name__ == '__main__':
    # data = get_id()
    es_client = Elasticsearch(hosts=[settings.ES_ADDRESS], timeout=80, max_retries=10,
                              retry_on_timeout=True)
    with open('result.txt', 'r') as f:
        data_list = f.readlines()

    for data_obj in data_list:
        split_list = data_obj.split('\t')
        recommend_score = float(split_list[1].replace('\n', ''))
        es_client.update(index='learning_video', doc_type='video', id=split_list[0],
                         body={'doc': {'recommend_score': recommend_score}})
    # for data_obj in data:
    #     res = es_client.get(index='learning_video', doc_type='video', id=data_obj)
    #     print(res['_source']['class_name'])
    # count_es()
    # entrance()
    pass
