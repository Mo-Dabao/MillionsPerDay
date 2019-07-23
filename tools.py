# coding: utf-8
"""
工具模块

@author: modabao
"""


import os
from glob import glob
import json
import requests
from lxml import etree
import pandas as pd
from sqlalchemy import create_engine


with open("config.json", 'r', encoding='utf-8') as json_file:
    config = json.load(json_file)
con = create_engine(config['database']['link_str'])
for sql in config['database']['sql_create']:
    con.execute(sql).close()
# print(con.table_names())


def get_html(url, headers=None):
    """
    根据传入的url获取对应的response
    :param url:
    :param headers:
    :return: response
    """
    if not headers:
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                 'AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/74.0.3729.131 Safari/537.36'}
    response = requests.get(url=url, headers=headers)
    if response.status_code == 200:
        response.encoding = response.apparent_encoding
        html = etree.HTML(response.text)
        return html
    else:
        return False


def add2db(table_name, field_names, records):
    """
    向table_name表中添加数据
    :param table_name: 表名
    :param field_names: 字段名
    :param records: <list>要添加的数据，顺序与field_names对应
    :return: None
    """
    data = pd.DataFrame(records, columns=field_names)
    data.to_sql(table_name, con, if_exists='append', index=False)


def get_last_term(table_name, field_names):
    """
    获取数据库中最新一期期号
    :param table_name: 表名
    :param field_names: 字段名
    :return: 最新一期期号
    """
    result = con.execute(f'SELECT MAX({field_names[0]}) FROM {table_name}')
    last_term = result.fetchone()[0]
    result.close()
    return last_term or '00000'


def get_history(table_name, field_names, term=None,
                start_term='00000', end_term='99999', terms=None):
    """
    从指定表获取历史数据
    :param table_name: 表名
    :param field_names: 字段名
    :param term: 要查找的某一期号
    :param start_term: 要查找的开始期号
    :param end_term: 要查找的结束期号
    :return: <pd.DataFrame>
    """
    if term:
        sql = f'SELECT * FROM {table_name} WHERE {field_names[0]} = {term};'
    elif not terms:
        sql = (f'SELECT * FROM {table_name} '
               f'WHERE {field_names[0]} BETWEEN {start_term} AND {end_term} '
               f'ORDER BY {field_names[0]} DESC;')
    else:
        sql = (f'SELECT * FROM {table_name} '
               f'WHERE {field_names[0]} BETWEEN {start_term} AND {end_term} '
               f'ORDER BY {field_names[0]} DESC '
               f'LIMIT {terms};')
    return pd.read_sql(sql, con, index_col=field_names[0])
