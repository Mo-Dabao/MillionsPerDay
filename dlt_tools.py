# coding: utf-8
"""
大乐透

@author: modabao
"""


from datetime import datetime
import pandas as pd
from common import get_html, add2db, get_last_term, config, get_history


fields = config['dlt_fields']
table_name = config['dlt_table']
front_balls = [f'{x:02d}' for x in range(1, 36)]
back_balls = [f'{x:02d}' for x in range(1, 13)]
all_columns = [['front'] * 35 + ['back'] * 12, front_balls + back_balls]
all_columns = pd.MultiIndex.from_tuples(list(zip(*all_columns)), 
                                        names=['part', 'ball'])
history_columns = [['front'] * 5 + ['back'] * 2,
                   ['f1', 'f2', 'f3', 'f4', 'f5', 'b1', 'b2']]
history_columns = pd.MultiIndex.from_tuples(list(zip(*history_columns)),
                                            names=['part', 'ball'])
award_prize = {'一等奖': 1000000,
               '二等奖': 500000,
               '三等奖': 10000,
               '四等奖': 3000,
               '五等奖': 300,
               '六等奖': 200,
               '七等奖': 100,
               '八等奖': 15,
               '九等奖': 5,
               '血亏': 0}

# 默认url和xpath
url_template = ('http://www.lottery.gov.cn/historykj/history.jspx?'
                'page=false&_ltype=dlt&termNum=0&'
                'startTerm={startTerm}&endTerm={endTerm}')
xpath_records = '/html/body/div[3]/div[2]/div[2]/table/tbody/tr'
xpath_record = './td[position()<=8]/text()'


def update():
    """
    更新大乐透数据
    :return: None
    """
    last_term = get_last_term(table_name, fields)  # 读取上一期已保存的期号
    print(f'数据库中最新一期为{last_term}')
    start_term = f'{int(last_term)+1:05d}'
    end_term = f'{datetime.now().year % 100}999'
    url = url_template.format(startTerm=start_term, endTerm=end_term)
    html = get_html(url)
    records = [x.xpath(xpath_record) for x in html.xpath(xpath_records)]
    if records:
        add2db(table_name, fields, records)
        print(f'数据库中更新到{records[0][0]}')
    else:
        print('没有更新')


def check_awards(predict_df, reality_df):
    """
    检查预测的获奖情况
    :param predict_df: DataFrame，index设为term
    :param reality_df: DataFrame，index设为term
    :return: DataFrame，中奖等级
    """
    index = [x for x in predict_df.index if x in reality_df.index]
    if not index:
        return None
    predict_df = predict_df.loc[index]
    reality_df = reality_df.loc[index]
    awards = []
    for n in range(len(index)):
        f = len(set(predict_df.iloc[n]['front']) &
                set(reality_df.iloc[n]['front']))
        b = len(set(predict_df.iloc[n]['back']) &
                set(reality_df.iloc[n]['back']))
        if f == 5 and b == 2:
            level = '一等奖'
        elif f == 5 and b == 1:
            level = '二等奖'
        elif f == 5 and b == 0:
            level = '三等奖'
        elif f == 4 and b == 2:
            level = '四等奖'
        elif f == 4 and b == 1:
            level = '五等奖'
        elif f == 3 and b == 2:
            level = '六等奖'
        elif f == 4 and b == 0:
            level = '七等奖'
        elif (f == 3 and b == 1) or (f == 2 and b == 2):
            level = '八等奖'
        elif ((f == 3 and b == 0) or (f == 1 and b == 2) or
              (f == 2 and b == 1) or (f == 0 and b == 2)):
            level = '九等奖'
        else:
            level = '血亏'
        awards.append([level, award_prize[level]])
    awards = pd.DataFrame(awards, index=index, columns=['level', 'prize'])
    return awards


def get_freq(history, terms=1, step=None):
    """
    求一段时间内各号出现次数
    """
    index = history.index[:terms] if terms else history.index
    freq = []
    if step:
        for n, x in enumerate(index):
            freq.append(get_freq_core(history.iloc[n:n+step]))
    else:
        for n, x in enumerate(index):
            freq.append(get_freq_core(history.iloc[n:]))
    freq = pd.DataFrame(freq, index=index, columns=all_columns)
    return freq
    

def get_freq_core(history):
    """
    """
    front_list = history['front'].values.flatten().tolist()
    back_list = history['back'].values.flatten().tolist()
    nums = len(history)
    front_freq = [front_list.count(x) / nums for x in front_balls]
    back_freq = [back_list.count(x) / nums for x in back_balls]
    freq = front_freq + back_freq
    return freq

    
def get_winning_rate(award):
    """
    计算中奖率
    """
    winning_rate = award['level'].value_counts(normalize=True)
    winning_rate['所有奖'] = 1 - winning_rate['血亏']
    winning_rate = winning_rate.reindex(['九等奖', '八等奖', '七等奖', '六等奖',
                                         '五等奖', '四等奖', '三等奖', '二等奖',
                                         '一等奖', '所有奖'], fill_value=0)
    return winning_rate
    
    
    
    
    