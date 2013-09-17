# -*- coding: utf-8 -*-
import time
from PyQt4 import QtGui, QtCore
import datetime


class ChartWidget(QtGui.QWidget):
    def __init__(self, parent=None, records=None):
        super(ChartWidget, self).__init__(parent)
        self.records = records
        self.statistics = [0] * 12
        self.countRecords()

        self.margin = 10

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        self.drawAxis(painter)
        self.drawLines(painter)
        painter.end()

    def drawAxis(self, painter):
        pen = QtGui.QPen()
        pen.setWidth(1)
        pen.setColor(QtGui.QColor('#000'))
        painter.setPen(pen)
        # 两条坐标轴
        painter.drawLine(self.margin, self.height()-self.margin, self.margin, self.margin)
        painter.drawLine(self.margin, self.height()-self.margin, self.width()-self.margin, self.height()-self.margin)
        # 箭头
        painter.drawLine(self.margin, self.margin, self.margin-3, self.margin+10)
        painter.drawLine(self.margin, self.margin, self.margin+3, self.margin+10)
        painter.drawLine(self.width()-self.margin, self.height()-self.margin,
                         self.width()-self.margin-10, self.height()-self.margin-3)
        painter.drawLine(self.width()-self.margin, self.height()-self.margin,
                         self.width()-self.margin-10, self.height()-self.margin+3)

    def countRecords(self):
        year = datetime.datetime.fromtimestamp(time.time()).year
        for record in self.records:
            for month in xrange(0, 12):
                if datetime.datetime(year, month+1, 1) <= datetime.datetime.fromtimestamp(record.startTime) < datetime.datetime(year, month+2, 1):
                    self.statistics[month] += 1

    def drawLines(self, painter):
        vInterval = (self.height() - self.margin*2) / max(self.statistics)
        hInterval = (self.width() - self.margin*2) / 13

        pen = QtGui.QPen()
        pen.setWidth(10)
        pen.setColor(QtGui.QColor('#f55'))
        painter.setPen(pen)

        # startPoint = QtCore.QPoint(self.margin, self.height()-self.margin)
        for month in xrange(12):
            endPoint = QtCore.QPoint(
                (month + 1) * hInterval + self.margin,
                self.height() - self.margin - self.statistics[month] * vInterval
            )
            painter.drawPoint(endPoint)
            #painter.drawLine(startPoint, endPoint)
            #startPoint = endPoint

class StatDialog(QtGui.QDialog):
    def __init__(self, parent=None, records=None):
        super(StatDialog, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle(u'词汇统计')

        tableWidget = QtGui.QTableWidget(len(records), 5, self)
        # 设置表头
        tableWidget.setHorizontalHeaderLabels(
            (u'单词', u'首次记忆时间', u'上次记忆时间', u'阶段', u'陌生度')
        )
        tableWidget.verticalHeader().setVisible(False)
        tableWidget.horizontalHeader().setHighlightSections(False)  # 禁止表头高亮

        for row in xrange(len(records)):
            tableItemData = [
                records[row].wordName,
                time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(records[row].startTime)),
                time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(records[row].lastTime)),
                str(records[row].stage),
                str(records[row].strange),
            ]

            for col in xrange(len(tableItemData)):
                tableItem = QtGui.QTableWidgetItem(tableItemData[col])
                tableItem.setTextAlignment(QtCore.Qt.AlignCenter)
                #tableItem.setFlags(QtCore.Qt.ItemIsEnabled)
                tableWidget.setItem(row, col, tableItem)

        tableWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)     # 禁止编辑
        tableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)    # 整行选中的方式
        tableWidget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)   # 设置为只能选中单个目标
        tableWidget.setSortingEnabled(True)
        # 重设列宽
        tableWidget.resizeColumnToContents(1)
        tableWidget.resizeColumnToContents(2)
        tableWidget.resizeRowsToContents()
        tableWidget.horizontalHeader().setStretchLastSection(True)
        # 取消表格边框
        # tableWidget.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        chartWidget = ChartWidget(self, records)

        tabWidget = QtGui.QTabWidget(self)
        tabWidget.addTab(tableWidget, u'背诵记录')
        tabWidget.addTab(chartWidget, u'记忆图线')

        buttonBox = QtGui.QDialogButtonBox(parent=self)
        #buttonBox.setOrientation(QtCore.Qt.Horizontal)      # 设置为水平方向
        #buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        okButton = QtGui.QPushButton(u'确定')
        okButton.clicked.connect(self.accept)
        buttonBox.addButton(okButton, QtGui.QDialogButtonBox.AcceptRole)
        #buttonBox.accepted.connect(self.accept)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(tabWidget)
        layout.addWidget(buttonBox)
        self.setLayout(layout)

        # 根据屏幕大小设置窗口大小，并居中
        screen = QtGui.QDesktopWidget().screenGeometry()
        height = screen.height() / 2
        self.setMinimumHeight(height)
        width = 600
        self.setMinimumWidth(width)
        self.move((screen.width()-width)/2, (screen.height()-height)/2)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)