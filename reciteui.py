# -*- coding: utf-8 -*-
import sys
import os
import time
from PyQt4 import QtGui, QtCore
from managers import ReciteManager


class StatDialog(QtGui.QDialog):
    def __init__(self, parent=None, records=None):
        super(StatDialog, self).__init__(parent)

        tableWidget = QtGui.QTableWidget(len(records), 5, self)

        # 设置表头
        tableWidget.setHorizontalHeaderItem(0, QtGui.QTableWidgetItem(u'单词'))
        tableWidget.setHorizontalHeaderItem(1, QtGui.QTableWidgetItem(u'首次记忆时间'))
        tableWidget.setHorizontalHeaderItem(2, QtGui.QTableWidgetItem(u'上次记忆时间'))
        tableWidget.setHorizontalHeaderItem(3, QtGui.QTableWidgetItem(u'阶段'))
        tableWidget.setHorizontalHeaderItem(4, QtGui.QTableWidgetItem(u'陌生度'))

        for row in xrange(len(records)):
            tableItems = []
            tableItems.append(QtGui.QTableWidgetItem(records[row].wordName))
            tableItems.append(QtGui.QTableWidgetItem(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(records[row].startTime))))
            tableItems.append(QtGui.QTableWidgetItem(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(records[row].lastTime))))
            tableItems.append(QtGui.QTableWidgetItem(str(records[row].stage)))
            tableItems.append(QtGui.QTableWidgetItem(str(records[row].strange)))

            for col in xrange(len(tableItems)):
                tableItems[col].setFlags(QtCore.Qt.ItemIsEnabled)
                tableWidget.setItem(row, col, tableItems[col])

        layout = QtGui.QGridLayout()
        layout.addWidget(tableWidget)
        self.setLayout(layout)
        self.resize(600, 400)

class Window(QtGui.QMainWindow):
    windowTitle = 'Hello Word'

    # 词库
    lexiconDir = 'lexicons/'
    lexiconName = 'GRE.lxc'

    # 图标
    iconDir = 'res/icons/'
    lexiconIconName = 'lexicon.png'
    statIconName = 'stat.png'
    reviewIconName = 'review.png'
    exitIconName = 'exit.png'
    aboutIconName = 'about.png'
    mainIconName = 'main.png'

    # 记录
    recordPath = 'records/recite.dat'

    # 字典
    dictDir = 'dicts/stardict-langdao-ec-gb-2.4.2/'
    dictPrefix = 'langdao-ec-gb'

    # 字体
    fontDir = 'fonts/'
    phoneticFontName = 'lingoes.ttf'

    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        self.statusBar = self.statusBar()

        self.initMenu()
        self.initToolbar()

        self.reciteManager = ReciteManager(
            os.path.join(self.lexiconDir, self.lexiconName),
            self.recordPath,
            self.dictDir,
            self.dictPrefix
        )

        windowTitle = self.windowTitle + ' | ' + self.reciteManager.getLexiconName()
        self.setWindowTitle(windowTitle)
        self.setWindowIcon(
            QtGui.QIcon(
                os.path.join(self.iconDir, self.mainIconName)
            )
        )

        self.initMainPanel()    # 初始化中央面板

        self.nextWord()

         # 根据屏幕大小设置窗口大小，并居中
        screen = QtGui.QDesktopWidget().screenGeometry()
        width = height = screen.width() / 3
        self.resize(width, height)
        self.move((screen.width()-width)/2, (screen.height()-height)/2)

    def initMenu(self):
        # 初始化菜单栏
        self.menuBar = self.menuBar()
        self.fileMenu = self.menuBar.addMenu(u"文件 (&F)")

        self.chooseLexAction = QtGui.QAction(u'选择词库 (&C)', self)
        self.chooseLexAction.setStatusTip(u'选择词库')
        self.chooseLexAction.setIcon(
            QtGui.QIcon(
                os.path.join(self.iconDir, self.lexiconIconName)
            )
        )
        self.connect(self.chooseLexAction, QtCore.SIGNAL('triggered()'), self.chooseLexicon)
        self.fileMenu.addAction(self.chooseLexAction)

        self.statAction = QtGui.QAction(u'词汇统计 (&S)', self)
        self.statAction.setStatusTip(u'词汇统计')
        self.statAction.setIcon(
            QtGui.QIcon(
                os.path.join(self.iconDir, self.statIconName)
            )
        )
        self.connect(self.statAction, QtCore.SIGNAL('triggered()'), self.statRecite)
        self.fileMenu.addAction(self.statAction)

        self.modeAction = QtGui.QAction(u'复习 (&R)', self)
        self.modeAction.setStatusTip(u'复习')
        self.modeAction.setIcon(
            QtGui.QIcon(
                os.path.join(self.iconDir, self.reviewIconName)
            )
        )
        self.connect(self.modeAction, QtCore.SIGNAL('triggered()'), self.changeReciteMode)
        self.fileMenu.addAction(self.modeAction)

        self.exitAction = QtGui.QAction(u'退出 (&X)', self)
        self.exitAction.setStatusTip(u'退出程序')
        self.exitAction.setIcon(
            QtGui.QIcon(
                os.path.join(self.iconDir, self.exitIconName)
            )
        )
        self.connect(self.exitAction, QtCore.SIGNAL('triggered()'), self.close)
        self.fileMenu.addAction(self.exitAction)

        self.helpMenu = self.menuBar.addMenu(u"帮助 (&H)")

        self.aboutAction = QtGui.QAction(u'关于 (&A)', self)
        self.aboutAction.setStatusTip(u'关于')
        self.aboutAction.setIcon(
            QtGui.QIcon(
                os.path.join(self.iconDir, self.aboutIconName)
            )
        )
        self.connect(self.aboutAction, QtCore.SIGNAL('triggered()'), self.about)
        self.helpMenu.addAction(self.aboutAction)

    def initToolbar(self):
        self.toolBar = self.addToolBar(u'快捷栏')
        self.toolBar.addAction(self.chooseLexAction)
        self.toolBar.addAction(self.statAction)
        self.toolBar.addAction(self.modeAction)
        self.toolBar.addAction(self.aboutAction)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.exitAction)
        self.toolBar.setFloatable(False)

    def initMainPanel(self):
        self.lblWordName = QtGui.QLabel()
        self.lblWordName.setFont(QtGui.QFont('Times New Roman', 48, QtGui.QFont.Bold))

        self.nextButton = QtGui.QPushButton(u"下一个单词")
        self.connect(self.nextButton, QtCore.SIGNAL('clicked()'), self.nextWord)

        QtGui.QFontDatabase.addApplicationFont(os.path.join(self.fontDir, self.phoneticFontName))
        self.lblPhonetic = QtGui.QLabel()
        self.lblPhonetic.setFont(QtGui.QFont('Lingoes Unicode', 14))

        self.lblInterp = QtGui.QTextEdit()
        self.lblInterp.setFont(QtGui.QFont(u'楷体', 20))
        self.lblInterp.setReadOnly(True)

        self.mainPanel = QtGui.QWidget(self)
        self.mainPanel.layout = QtGui.QGridLayout(self.mainPanel)

        self.mainPanel.layout.addWidget(self.lblWordName, 0, 0)
        self.mainPanel.layout.addWidget(self.lblPhonetic, 1, 0)
        self.mainPanel.layout.addWidget(self.lblInterp, 2, 0)
        self.mainPanel.layout.addWidget(self.nextButton, 3, 0)

        self.mainPanel.setLayout(self.mainPanel.layout)
        self.setCentralWidget(self.mainPanel)

    def nextWord(self):
        # self.sender()
        self.reciteManager.nextWord()
        word = self.reciteManager.getWord()
        self.lblWordName.setText(word.name)
        self.lblPhonetic.setText(word.phonetic)
        self.lblInterp.setText(word.interp)


    def chooseLexicon(self):
        filePath = QtGui.QFileDialog.getOpenFileName(self, u'选择词库', self.lexiconDir).toUtf8()
        if filePath:
            filePath = unicode(filePath, 'utf-8')
            self.statusBar.showMessage(filePath)
            self.reciteManager.setLexicon(filePath)
            windowTitle = self.windowTitle + ' | ' + self.reciteManager.getLexiconName()
            self.setWindowTitle(windowTitle)
            self.nextWord()


    def statRecite(self):
        records = self.reciteManager.recordManager.getRecords()
        self.statDialog = StatDialog(self, records)
        self.statDialog.show()

    def changeReciteMode(self):
        pass

    def about(self):
        aboutMessage = u"""
        <p>版权所有&nbsp;&copy;&nbsp;2010-2013&nbsp;WHYPRO</p>
        """
        QtGui.QMessageBox.about(self, u'关于', aboutMessage)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    m = Window()
    m.show()
    app.exec_()

