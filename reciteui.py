# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtGui, QtCore
from managers import WordManager


class MainPanel(QtGui.QWidget):
    def __init__(self, parent=None):
        super(MainPanel, self).__init__(parent)

        self.layout = QtGui.QGridLayout()

        self.wordManager = WordManager(u'考研英语.txt', 'stardict-langdao-ec-gb-2.4.2', 'langdao-ec-gb')

        self.lblWordName = QtGui.QLabel()
        self.lblWordName.setFont(QtGui.QFont('Arial', 42, QtGui.QFont.Bold))

        self.btn = QtGui.QPushButton()
        self.connect(self.btn, QtCore.SIGNAL('clicked()'), self.nextWord)

        self.lblPhonetic = QtGui.QLabel()
        self.lblPhonetic.setFont(QtGui.QFont('Courier New', 12))

        self.lblInterp = QtGui.QTextEdit()
        self.lblInterp.setFont(QtGui.QFont('楷体', 20))
        self.lblInterp.setReadOnly(True)

        self.nextWord()

        self.layout.addWidget(self.lblWordName, 0, 0)
        self.layout.addWidget(self.lblPhonetic, 1, 0)
        self.layout.addWidget(self.lblInterp, 2, 0)
        self.layout.addWidget(self.btn, 3, 0)

        self.setLayout(self.layout)

    def nextWord(self):
        word = self.wordManager.getRandomWord()
        self.lblWordName.setText(word.name)
        self.lblPhonetic.setText(word.phonetic)
        self.lblInterp.setText(word.interp)


class StatDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(StatDialog, self).__init__(parent)

        QtGui.QTableView()

class Window(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        self.setWindowTitle('Hello Word')
        self.statusBar = self.statusBar()
        self.setWindowIcon(QtGui.QIcon('res/icons/icon.png'))


        self.initMenu()

        self.toolBar = self.addToolBar(u'工具栏')
        self.toolBar.addAction(self.exitAction)
        self.toolBar.addAction(self.statAction)
        self.toolBar.addAction(self.modeAction)

        self.mainPanel = MainPanel(self)
        self.setCentralWidget(self.mainPanel)

         # 根据屏幕大小设置窗口大小，并居中
        screen = QtGui.QDesktopWidget().screenGeometry()
        width = height = screen.width() / 3
        self.resize(width, height)
        self.move((screen.width()-width)/2, (screen.height()-height)/2)

    def initMenu(self):
        # 初始化菜单栏
        self.menuBar = self.menuBar()
        self.fileMenu = self.menuBar.addMenu(u"文件 (&F)")

        self.chooseThAction = QtGui.QAction(u'选择词库 (&C)', self)
        self.chooseThAction.setStatusTip(u'选择词库')
        self.connect(self.chooseThAction, QtCore.SIGNAL('triggered()'), self.chooseLexicon)
        self.fileMenu.addAction(self.chooseThAction)

        self.statAction = QtGui.QAction(u'词汇统计 (&S)', self)
        self.statAction.setStatusTip(u'词汇统计')
        self.connect(self.statAction, QtCore.SIGNAL('triggered()'), self.statRecite)
        self.fileMenu.addAction(self.statAction)

        self.modeAction = QtGui.QAction(u'复习 (&R)', self)
        self.modeAction.setStatusTip(u'复习')
        self.connect(self.modeAction, QtCore.SIGNAL('triggered()'), self.changeReciteMode)
        self.fileMenu.addAction(self.modeAction)

        self.exitAction = QtGui.QAction(u'退出 (&X)', self)
        self.exitAction.setStatusTip(u'退出程序')
        self.connect(self.exitAction, QtCore.SIGNAL('triggered()'), self.close)
        self.fileMenu.addAction(self.exitAction)

        self.helpMenu = self.menuBar.addMenu(u"帮助 (&H)")

        self.aboutAction = QtGui.QAction(u'关于 (&A)', self)
        self.aboutAction.setStatusTip(u'关于')
        self.connect(self.aboutAction, QtCore.SIGNAL('triggered()'), self.about)
        self.helpMenu.addAction(self.aboutAction)

    def chooseLexicon(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, u'选择词库').toUtf8()
        filename = unicode(filename, 'utf-8')
        self.statusBar.showMessage(filename)

    def statRecite(self):
        self.statDialog = StatDialog(self)
        self.statDialog.show()

    def changeReciteMode(self):
        pass

    def about(self):
        QtGui.QMessageBox.about(self, u'关于', u'<p>版权所有 2010-2013 WHYPRO</p>')

app = QtGui.QApplication(sys.argv)
m = Window()
m.show()
app.exec_()
app.closeAllWindows()

