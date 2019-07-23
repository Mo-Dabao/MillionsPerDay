# coding: utf-8
"""
# 用pyside2-uic.exe把ui转换成py
用pyuic5.exe把ui转换成py
"""


import os
from glob import glob


def ui2py(ui_dir):
    uis = glob(ui_dir)  # 列出目录下的所有ui文件
    pys = [x[:-2] + "py" for x in uis]
    for ui, py in zip(uis, pys):
        os.system(f"pyuic5 -o {py} {ui}")


if __name__ == "__main__":
    ui_dir = "./*.ui"  # UI文件所在的路径
    ui2py(ui_dir)
