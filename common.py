# coding: utf-8
"""
工具模块

@author: modabao
"""


import json
import requests
import pandas as pd
from lxml import etree
from sqlalchemy import create_engine


with open("config_.json") as json_file:
    config = json.load(json_file)
link_str = config['link_str']
con = create_engine(link_str)

if not con.has_table('dlt'):
    con.execute('''CREATE TABLE dlt (
                   term char(5), f1 char(2), f2 char(2), f3 char(2), 
                   f4 char(2), f5 char(2), b1 char(2), b2 char(2)
                   );''').close()
    


def get_html(url):
    """
    根据传入的url获取对应的XPath解析对象
    没有进行header伪装和异常处理
    """
    headers = {
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Mobile Safari/537.36',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'max-age=0',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
    }
    response = requests.get(url=url, headers=headers)
    if response.status_code == 200:
        response.encoding = response.apparent_encoding
        return etree.HTML(response.text)
    else:
        return False


def add2db(tablename, fields, records, con=con):
    """
    在kind表中添加数据
    """
    data = pd.DataFrame(records, columns=fields)
    data.to_sql(tablename, con, if_exists='append', index=False)


def get_last_term(table_name, fields, con=con):
    """
    获取数据库中最新一期期号
    :param table_name: 目标表名
    :param fieldname: 目标字段名
    :param con: sqlalchemy的Engine
    :return: 最后一次的期号
    """
    result = con.execute(f'select max({fields[0]}) from {table_name}')
    last_term = result.fetchone()[0]
    return last_term or '00000'


def get_history(tablename, fields, term=None, start_term='00000', end_term='99999', con=con):
    """

    :param tablename:
    :param from_term:
    :param fieldname:
    :param con:
    :return: DataFrame
    """
    if term:
        sql = f'select * from {tablename} where {fields[0]} = {term}'
    else:
        sql = (f'select * from {tablename} '
               f'where {fields[0]} between {start_term} and {end_term} '
               'order by term desc')
    return pd.read_sql(sql, con, index_col='term')
