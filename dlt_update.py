# coding: utf-8
import datetime
import requests
from lxml import etree


def get_html(url):
    r = requests.get(url)
    return etree.HTML(r.text)


def add_one(html, newest_num):
    """
    在历史数据中添加一行新数据
    html为etree
    """
    # xpath_order = "//div[@class='ball_box01']/../../../tr[2]/td[2]/text()"
    newest = html.xpath(xpath_order)
    if not newest:
        return True  ####？可能不对
    row = [newest_num]
    row.extend(newest)
    with open('dlt.csv', 'a') as f:
        f.write(','.join(row) + '\n')
    with open("dlt_log.txt", 'w') as f:
        f.write(newest_num)
    print(f"新增第{newest_num}期")


with open("./dlt_log.txt", 'r') as f:
    last_num = f.read()
print(f"上一条历史记录为第{last_num}期")
url = "http://kaijiang.500.com/dlt.shtml"
xpath_newest_num = "//font[@class='cfont2']/strong/text()"
xpath_order = "//div[@class='ball_box01']/ul/li/text()"
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
        flag = add_one(html, last_num)
        if newest_num[:3] > last_num[:3] and flag:
            last_num = newest_num[:3] + "000"


