# coding: utf-8
"""
大乐透分析

@file: dlt.py
@author: modabao
@software: PyCharm
"""


import random
import pandas as pd
from dlt_tools import (update, get_history, check_awards, fields, get_freq,
                       history_columns, all_columns, front_balls, back_balls,
                       get_winning_rate)


# %% 读取数据
table_name = 'dlt'
update()
history = get_history(table_name, fields)
history.columns = history_columns


# %% 盲猜
blind_guess = [random.sample(front_balls, 5) + random.sample(back_balls, 2)
               for x in range(len(history.index))]
blind_guess = pd.DataFrame(blind_guess, index=history.index,
                           columns=history_columns)
awards_blind_guess = check_awards(blind_guess, history)
profit_blind_guess = awards_blind_guess['prize'].sum() - len(history.index) * 2


# %% 最大、最小频率
history_frq = get_freq(history, terms=None)
max_frq = []
min_frq = []
terms = []
for n, x in enumerate(history_frq.index):
    if n == 0:
        terms.append(f'{int(x)+1:05d}')
    else:
        terms.append(history_frq.index[n-1])
    f = history_frq.loc[x]['front'].sort_values(0)
    b = history_frq.loc[x]['back'].sort_values(0)
    min_frq.append(f.index[:5].tolist() + b.index[:2].tolist())
    max_frq.append(f.index[-5:].tolist() + b.index[-2:].tolist())
min_frq = pd.DataFrame(min_frq, index=terms, columns=history_columns)
max_frq = pd.DataFrame(max_frq, index=terms, columns=history_columns)
awards_min_frq = check_awards(min_frq, history)
profit_min_frq = awards_min_frq['prize'].sum() - len(history.index) * 2
awards_max_frq = check_awards(max_frq, history)
profit_max_frq = awards_max_frq['prize'].sum() - len(history.index) * 2


# %% 滑动最大、最小频率
history_frq = get_freq(history, terms=200, step=50)
max_frq = []
min_frq = []
terms = []
for n, x in enumerate(history_frq.index):
    if n == 0:
        terms.append(f'{int(x)+1:05d}')
    else:
        terms.append(history_frq.index[n-1])
    f = history_frq.loc[x]['front'].sort_values(0)
    b = history_frq.loc[x]['back'].sort_values(0)
    min_frq.append(f.index[:5].tolist() + b.index[:2].tolist())
    max_frq.append(f.index[-5:].tolist() + b.index[-2:].tolist())
min_frq = pd.DataFrame(min_frq, index=terms, columns=history_columns)
max_frq = pd.DataFrame(max_frq, index=terms, columns=history_columns)
awards_min_frq = check_awards(min_frq, history)
profit_min_frq = awards_min_frq['prize'].sum() - len(min_frq.index) * 2
awards_max_frq = check_awards(max_frq, history)
profit_max_frq = awards_max_frq['prize'].sum() - len(max_frq.index) * 2
winning_rate_min_frq = get_winning_rate(awards_min_frq)
winning_rate_max_frq = get_winning_rate(awards_max_frq)


# %% 探索求频率的步长
max_records = []
min_records = []
index = history.index[0:200]
columns = list(range(1, 201))
for term, next_term in zip(history.index[1:201], index):
    max_records.append([])
    min_records.append([])
    for step in columns:
        print(term, step)
        frq = get_freq(history.loc[term:], step=step)
        max_frq = []
        min_frq = []
        f = frq['front'].iloc[0].sort_values(0)
        b = frq['back'].iloc[0].sort_values(0)
        min_frq.append(f.index[:5].tolist() + b.index[:2].tolist())
        max_frq.append(f.index[-5:].tolist() + b.index[-2:].tolist())
        min_frq = pd.DataFrame(min_frq, index=[next_term],
                               columns=history_columns)
        max_frq = pd.DataFrame(max_frq, index=[next_term],
                               columns=history_columns)
        awards_min_frq = check_awards(min_frq, history)
        awards_max_frq = check_awards(max_frq, history)
        max_records[-1].append(awards_max_frq.at[next_term, 'prize'])
        min_records[-1].append(awards_min_frq.at[next_term, 'prize'])
max_records = pd.DataFrame(max_records, index=index, columns=columns)
min_records = pd.DataFrame(min_records, index=index, columns=columns)









