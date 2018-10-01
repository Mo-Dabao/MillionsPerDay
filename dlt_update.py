# coding: utf-8
"""
更新大乐透历史数据
默认网址为http://kaijiang.500.com/dlt.shtml

@author: modabao
"""

import requests
from lxml import etree


def get_html(url):
    """
    根据传入的url获取对应的XPath解析对象
    没有进行header伪装和异常处理
    """
    r = requests.get(url)
    return etree.HTML(r.text)

def add_one(html, newest_num):
    """
    在历史数据中添加一行新数据
    html为etree
    """
    # xpath_order = "//div[@class='ball_box01']/../../../tr[2]/td[2]/text()"
    newest = html.xpath(xpath_order)  # 如果新的一期不存在则newest为空
    if not newest:
        return True  # 如果新的一期不存在则返回True
    row = [newest_num]
    row.extend(newest)
    # 保存到.csv中
    with open('dlt.csv', 'a') as f:
        f.write(','.join(row) + '\n')
    # 更新保存进度
    with open("dlt_log.txt", 'w') as f:
        f.write(newest_num)
    print(f"新增第{newest_num}期")


# 读取上一期已保存的期号
with open("./dlt_log.txt", 'r') as f:
    last_num = f.read()
print(f"上一条历史记录为第{last_num}期")

# 默认url和xpath
url = "http://kaijiang.500.com/dlt.shtml"
xpath_newest_num = "//font[@class='cfont2']/strong/text()"
xpath_order = "//div[@class='ball_box01']/ul/li/text()"

# 获取最新一期
html = get_html(url)
newest_num = html.xpath(xpath_newest_num)[0]  # 最新一期的期号
print(f"最新一期为第{newest_num}期")

if newest_num == last_num:
    print("历史数据已是最新")
elif newest_num < last_num:
    print("历史数据新于http://kaijiang.500.com/dlt.shtml\n**请排查**")
else:
    while newest_num > last_num:
        last_num = str(int(last_num) + 1)
        # print(last_num)
        url = f"http://kaijiang.500.com/shtml/dlt/{last_num}.shtml"
        html = get_html(url)
        # 考虑跨年，认为当新的一期不存在即为该年所有期都已保存
        flag = add_one(html, last_num)  # 如果新的一期不存在则返回True
        if newest_num[:3] > last_num[:3] and flag:
            last_num = str(int(last_num[:3])) + "000"


