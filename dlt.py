# coding: utf-8
"""
大乐透

Created on 2019-5-27 09:11:17
@author: modabao
"""


from datetime import datetime

import pandas as pd

from tools import config, get_last_term, get_html, add2db, get_history


config = config["dlt"]


class DLT(object):
    """
    大乐透
    """
    table_name = config['table_name']
    field_names = config['field_names']
    front_balls = config['front_balls']
    back_balls = config['back_balls']
    award_prize = config['award_prize']
    all_balls = [['front'] * 35 + ['back'] * 12, front_balls + back_balls]
    all_balls = pd.MultiIndex.from_tuples(list(zip(*all_balls)),
                                          names=['part', 'ball'])
    win_balls = [['front'] * 5 + ['back'] * 2, field_names[1:]]
    win_balls = pd.MultiIndex.from_tuples(list(zip(*win_balls)),
                                          names=['part', 'ball'])
    url_template = (
        'https://datachart.500.com/ssq/history/newinc/history.php?'
        'start={start}&end={end}')
    xpath_records = '//*[@id="tdata"]/tr'
    xpath_record = './td[position()<=8]/text()'

    def __init__(self):
        """"""
        self.history = None
        self.update()

    @classmethod
    def update(cls):
        """
        更新大乐透数据
        :return:
        """
        # 读取上一期已保存的期号
        last_term = get_last_term(cls.table_name, cls.field_names)
        start_term = f'{int(last_term)+1:05d}'
        end_term = f'{datetime.now().year % 100}999'
        url = cls.url_template.format(start=start_term, end=end_term)
        html = get_html(url)
        records = [x.xpath(cls.xpath_record)
                   for x in html.xpath(cls.xpath_records)]
        if records:
            add2db(cls.table_name, cls.field_names, records)
            new_last_term = records[0][0]
        else:
            new_last_term = last_term
        return last_term, new_last_term

    def get_history(self, term=None, start_term='00000', end_term='99999', terms=None):
        """
        获取大乐透历史开奖纪录

        :param term:
        :param start_term:
        :param end_term:
        :param terms:
        :return:
        """
        self.history = get_history(self.table_name, self.field_names, term,
                                   start_term, end_term, terms)
        self.history.columns = self.win_balls

    def get_freq(self, history=None, terms=1, step=None):
        """
        求一段时间内各号出现次数
        """
        if not history and hasattr(self, 'history'):
            history = self.history
        elif not history:
            self.get_history()
            history = self.history
        index = history.index[:terms] if terms else history.index
        freq = []
        if step:
            for n, x in enumerate(index):
                freq.append(self.get_freq_core(history.iloc[n:n+step]))
        else:
            for n, x in enumerate(index):
                freq.append(self.get_freq_core(history.iloc[n:]))
        freq = pd.DataFrame(freq, index=index, columns=self.all_balls)
        return freq

    def check(self, predict_df, reality_df=None):
        """
        检查预测的获奖情况
        :param predict_df: DataFrame，index设为term
        :param reality_df: DataFrame，index设为term
        :return: <pd.DataFrame>中奖等级
        """
        if not reality_df and self.history:
            reality_df = self.history
        elif not reality_df:
            start_term = predict_df.index.min()
            end_term = predict_df.index.max()
            self.get_history(start_term, end_term)
            reality_df = self.history
        index = [x for x in predict_df.index if x in reality_df.index]
        if not index:
            return None
        predict_df = predict_df.loc[index]
        reality_df = reality_df.loc[index]
        records = []
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
            records.append([level, self.award_prize[level]])
        records = pd.DataFrame(records, index=index,
                               columns=['award', 'prize'])
        return records

    def get_freq_core(self, history):
        """
        """
        front_list = history['front'].values.flatten().tolist()
        back_list = history['back'].values.flatten().tolist()
        nums = len(history)
        front_freq = [front_list.count(x) / nums for x in self.front_balls]
        back_freq = [back_list.count(x) / nums for x in self.back_balls]
        freq = front_freq + back_freq
        return freq
