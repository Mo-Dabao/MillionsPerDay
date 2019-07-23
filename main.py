# coding: utf-8
"""

@file: main.py
@author: modabao
@time: 2019/7/4 19:05
@software: PyCharm
"""


import sys

from PyQt5 import QtCore, QtGui, QtWidgets
# from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
import numpy as np

from GUI_PyQT5 import Ui_GUI_PyQT5
from dlt import DLT


class UI(QtWidgets.QMainWindow, Ui_GUI_PyQT5):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.dlt = DLT()
        self.statusbar.showMessage('正在更新数据库……')
        last_term, new_last_term = self.dlt.update()
        self.statusbar.showMessage(f'数据库大乐透表原有到{last_term}期，现更新到{new_last_term}期')
        self.dlt.get_history(terms=50)
        self.hitory_table()
        self.frq_bars()

    def frq_bars(self):
        """

        :return:
        """
        freq = self.dlt.get_freq()
        dpi = 100
        canvas = FigureCanvas(Figure(figsize=((self.graphicsView.width()-2)/dpi, (self.graphicsView.height()-2)/dpi)))
        # axes = canvas.figure.subplots(2, 1)
        # ax_front = axes[1]
        # ax_back = axes[0]
        # ax_front = canvas.figure.subplots()
        ax_front = canvas.figure.add_axes([0.1, 0, 0.9, 1])
        # position = ax_front.get_position()
        # bbox = position  #[*position[0], *[x-y for x, y in zip(*position)]]
        # ax_back = canvas.figure.add_axes(bbox)
        ax_back = canvas.figure.add_axes([0, 0, 0.9, 1])
        ax_front.xaxis.set_visible(False)
        ax_back.xaxis.set_visible(False)
        ax_back.invert_xaxis()
        ax_back.yaxis.set_ticks_position('right')
        ax_back.patch.set_alpha(0)
        # ax_back.patch.set_facecolor('w')
        ax_front_data = np.sort(freq['front'].values[0])
        ax_front_labels = [self.dlt.front_balls[x] for x in np.argsort(freq['front'].values[0])]
        ax_back_data = np.sort(freq['back'].values[0])[::-1]
        ax_back_labels = [self.dlt.back_balls[x] for x in np.argsort(freq['back'].values[0])][::-1]
        rects_front = ax_front.barh(ax_front_labels, ax_front_data, color=(1, 1, 0, 1))
        rects_back = ax_back.barh(ax_back_labels, ax_back_data, color=(0, 1, 0, 1))
        rect_length = 1  # ax_front_data.max() + ax_back_data.max()
        ax_back.set_xlim([rect_length, 0])
        ax_front.set_xlim([0, rect_length])
        for rect in rects_front:
            width = rect.get_width()
            ax_front.annotate(f'{width:.2f}',
                              xy=(width, rect.get_y() + rect.get_height() / 2),
                              xytext=(3, 0),
                              textcoords="offset points",
                              ha='left', va='center_baseline')
        for rect in rects_back:
            width = rect.get_width()
            ax_back.annotate(f'{width:.2f}',
                             xy=(width, rect.get_y() + rect.get_height() / 2),
                             xytext=(-3, 0),  # 3 points vertical offset
                             textcoords="offset points",
                             ha='right', va='center')
        graphic_scene = QtWidgets.QGraphicsScene()
        graphic_scene.addWidget(canvas)
        self.graphicsView.setScene(graphic_scene)
        self.graphicsView.show()

    def hitory_table(self):
        """

        :return:
        """
        self.tableView.setModel(DataFrameModel(self.dlt.history))
        self.tableView.resizeColumnsToContents()  # 自动调整列宽

    def refresh(self):
        """

        :return:
        """
        recent = int(self.lineEdit_recent.text())
        self.dlt.get_history(terms=recent)
        self.frq_bars()
        self.hitory_table()



class DataFrameModel(QtCore.QAbstractTableModel):
    def __init__(self, df: pd.DataFrame, parent=None):
        super(DataFrameModel, self).__init__(parent)
        self.df = df

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return str(self.df.columns[section][1])
            else:
                return str(self.df.index[section])
        return QtCore.QVariant()

    def rowCount(self, parent=QtCore.QModelIndex()):
        return self.df.shape[0]

    def columnCount(self, parent=QtCore.QModelIndex()):
        return self.df.shape[1]

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return str(self.df.iloc[index.row(), index.column()])
            elif role == QtCore.Qt.BackgroundRole:
                if index.column() < 5:
                    return QtGui.QColor(255, 255, 0)
                else:
                    return QtGui.QColor(0, 255, 0)
        return None


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    my_win = UI()
    my_win.show()
    sys.exit(app.exec_())

