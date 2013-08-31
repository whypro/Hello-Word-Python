# -*- coding: utf-8 -*-
import sys
import os
import time
from PyQt4 import QtGui, QtCore, QtNetwork
from PyQt4.phonon import Phonon
from managers import ReciteManager
from models import Settings
import string


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
        tabWidget = QtGui.QTabWidget()
        tabWidget.addTab(tableWidget, u'记忆中')

        buttonBox = QtGui.QDialogButtonBox(parent=self)
        buttonBox.setOrientation(QtCore.Qt.Horizontal)      # 设置为水平方向
        buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        buttonBox.accepted.connect(self.accept)

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


class SettingsDialog(QtGui.QDialog):
    def __init__(self, parent=None, settings=None):
        super(SettingsDialog, self).__init__(parent)

        self.settings = settings

        voiceGroup = QtGui.QGroupBox(u'发音设置')

        self.autoPlayCheck = QtGui.QCheckBox(u'自动朗读单词')
        voiceGenderLabel = QtGui.QLabel(u'朗读模式')
        self.voiceGenderCombo = QtGui.QComboBox()
        self.voiceGenderCombo.addItems([u'男声', u'女声'])

        voiceGenderLayout = QtGui.QHBoxLayout()
        voiceGenderLayout.addWidget(voiceGenderLabel)
        voiceGenderLayout.addWidget(self.voiceGenderCombo)

        voiceLayout = QtGui.QVBoxLayout()
        voiceLayout.addWidget(self.autoPlayCheck)
        voiceLayout.addLayout(voiceGenderLayout)
        voiceGroup.setLayout(voiceLayout)

        buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        self.initConfig()

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(voiceGroup)
        mainLayout.addWidget(buttonBox)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)

    def initConfig(self):
        self.autoPlayCheck.setChecked(self.settings.autoPlayVoice)
        self.voiceGenderCombo.setCurrentIndex(self.settings.voiceGender)

    def accept(self):
        # 保存配置
        self.settings.autoPlayVoice = self.autoPlayCheck.isChecked()
        self.settings.voiceGender = self.voiceGenderCombo.currentIndex()
        print self.settings.autoPlayVoice
        print self.settings.voiceGender
        super(SettingsDialog, self).accept()


class Window(QtGui.QMainWindow):
    # 标题
    windowTitle = 'Hello Word'

    # 版本
    version = '0.2.1'

    # 词库
    lexiconDir = 'res/lexicons/'
    lexiconName = 'CET6.lxc'

    # 图标
    iconDir = 'res/icons/'
    lexiconIconName = 'lexicon.png'
    statIconName = 'stat.png'
    newWordIconName = 'new.png'
    reviewIconName = 'review.png'
    exitIconName = 'exit.png'
    aboutIconName = 'about.png'
    mainIconName = 'main.png'
    sysTrayIconName = 'tray.png'
    settingsIconName = 'config.png'

    # 记录
    recordPath = 'record/recite.dat'

    # 字典
    dictDir = 'res/dicts/stardict-langdao-ec-gb-2.4.2/'
    dictPrefix = 'langdao-ec-gb'

    # 字体
    fontDir = 'res/fonts/'
    phoneticFontName = 'lingoes.ttf'

    acceptList = tuple(string.uppercase + string.lowercase + '-')

    # 显示状态
    class DisplayStatus:
        Display, Input, Correct, Wrong = range(4)

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

        self.settings = Settings()

        windowTitle = self.windowTitle + ' | ' + self.reciteManager.getLexiconName()
        self.setWindowTitle(windowTitle)
        self.setWindowIcon(
            QtGui.QIcon(
                os.path.join(self.iconDir, self.mainIconName)
            )
        )

        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint)
        self.setWindowFlags(
            QtCore.Qt.CustomizeWindowHint |
            QtCore.Qt.WindowMinimizeButtonHint |
            QtCore.Qt.WindowCloseButtonHint
        )

        self.initMainPanel()    # 初始化中央面板

        self.initVoice()

        self.nextWord()

        self.initSysTray()

        # 根据屏幕大小设置窗口大小，并居中
        screen = QtGui.QDesktopWidget().screenGeometry()
        width = height = screen.width() / 3
        self.setFixedSize(width, height)
        self.move((screen.width()-width)/2, (screen.height()-height)/2)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        # self.setWindowState(self.windowState() | QtCore.Qt.WindowFullScreen)  # 窗口全屏

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
        self.chooseLexAction.triggered.connect(self.chooseLexicon)
        self.fileMenu.addAction(self.chooseLexAction)

        self.statAction = QtGui.QAction(u'词汇统计 (&S)', self)
        self.statAction.setStatusTip(u'词汇统计')
        self.statAction.setIcon(
            QtGui.QIcon(
                os.path.join(self.iconDir, self.statIconName)
            )
        )
        self.statAction.triggered.connect(self.statRecite)
        self.fileMenu.addAction(self.statAction)

        self.changeModeAction = QtGui.QAction(u'复习 (&R)', self)
        self.changeModeAction.setStatusTip(u'复习')
        self.changeModeAction.setIcon(
            QtGui.QIcon(
                os.path.join(self.iconDir, self.reviewIconName)
            )
        )
        self.changeModeAction.triggered.connect(self.changeReciteMode)
        self.fileMenu.addAction(self.changeModeAction)

        self.settingsAction = QtGui.QAction(u'设置 (&O)', self)
        self.settingsAction.setStatusTip(u'设置')
        self.settingsAction.setIcon(
            QtGui.QIcon(
                os.path.join(self.iconDir, self.settingsIconName)
            )
        )
        self.settingsAction.triggered.connect(self.configureSettings)
        self.fileMenu.addAction(self.settingsAction)

        self.exitAction = QtGui.QAction(u'退出 (&X)', self)
        self.exitAction.setStatusTip(u'退出程序')
        self.exitAction.setIcon(
            QtGui.QIcon(
                os.path.join(self.iconDir, self.exitIconName)
            )
        )
        self.exitAction.triggered.connect(QtGui.qApp.quit)
        self.fileMenu.addAction(self.exitAction)

        self.helpMenu = self.menuBar.addMenu(u"帮助 (&H)")

        self.aboutAction = QtGui.QAction(u'关于 (&A)', self)
        self.aboutAction.setStatusTip(u'关于')
        self.aboutAction.setIcon(
            QtGui.QIcon(
                os.path.join(self.iconDir, self.aboutIconName)
            )
        )
        self.aboutAction.triggered.connect(self.about)
        self.helpMenu.addAction(self.aboutAction)

    def initToolbar(self):
        self.toolBar = self.addToolBar(u'快捷栏')
        self.toolBar.addAction(self.chooseLexAction)
        self.toolBar.addAction(self.statAction)
        self.toolBar.addAction(self.changeModeAction)
        self.toolBar.addAction(self.settingsAction)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.aboutAction)
        #self.toolBar.addSeparator()
        #self.toolBar.addAction(self.exitAction)
        self.toolBar.setFloatable(False)

    def initMainPanel(self):
        self.lblWordName = QtGui.QLabel()
        self.lblWordName.setFont(QtGui.QFont('Times New Roman', 48, QtGui.QFont.Bold))

        #self.nextButton = QtGui.QPushButton(u'下一个单词')
        # self.nextButton.setDisabled(True)
        #self.nextButton.setFocusPolicy(QtCore.Qt.NoFocus)
        #self.connect(self.nextButton, QtCore.SIGNAL('clicked()'), self.nextWord)
        #self.nextButton.setVisible(False)

        QtGui.QFontDatabase.addApplicationFont(os.path.join(self.fontDir, self.phoneticFontName))
        self.lblPhonetic = QtGui.QLabel()
        self.lblPhonetic.setFont(QtGui.QFont('Lingoes Unicode', 14))

        self.lblInterp = QtGui.QTextEdit()
        self.lblInterp.setFont(QtGui.QFont(u'楷体', 20))
        self.lblInterp.setReadOnly(True)
        self.lblInterp.setFocusPolicy(QtCore.Qt.NoFocus)

        self.mainPanel = QtGui.QWidget()    # parent = self
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.mainPanel.layout = QtGui.QGridLayout(self.mainPanel)

        #self.voiceButton = QtGui.QPushButton(u"发音")
        #self.voiceButton.setFocusPolicy(QtCore.Qt.NoFocus)
        #self.connect(self.voiceButton, QtCore.SIGNAL('clicked()'), self.nextWord)

        self.imageArea = QtGui.QPixmap()
        self.mainPanel.layout.addWidget(self.lblWordName, 0, 0)
        self.mainPanel.layout.addWidget(self.lblPhonetic, 1, 0)
        #self.mainPanel.layout.addWidget(self.voiceButton, 1, 1)
        self.mainPanel.layout.addWidget(self.lblInterp, 2, 0, 1, 1)
        #self.mainPanel.layout.addWidget(self.nextButton, 3, 0)

        self.mainPanel.setLayout(self.mainPanel.layout)
        self.setCentralWidget(self.mainPanel)

    def initVoice(self):
        self.mediaObject = Phonon.MediaObject()
        self.audioOutput = Phonon.AudioOutput(Phonon.MusicCategory)
        Phonon.createPath(self.mediaObject, self.audioOutput)

    def nextWord(self):
        self.reciteManager.nextWord()
        word = self.reciteManager.getWord()
        if self.reciteManager.reciteMode == ReciteManager.Modes.Review and not word:
            QtGui.QMessageBox.information(self, u'Hello Word', u'恭喜，没有需要复习的单词了~')
            self.changeModeAction.trigger()
            return

        # 设置颜色
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.black)
        self.lblWordName.setPalette(palette)
        self.lblWordName.setText(word.name)
        self.lblPhonetic.setText(word.phonetic)
        self.lblInterp.setText(word.interp)
        self.spelling = ''
        self.displayStatus = self.DisplayStatus.Display
        self.statusBar.showMessage(u'"."键跳过该单词，"/"键发音，空格键或回车键检查拼写，退格键修正拼写')

        # import urllib2
        # i = urllib2.urlopen('http://img1.51cto.com/attachment/200910/200910271256653086390.png').read()
        # image = QtGui.QPixmap()
        # image.convertFromImage(QtGui.QImage(i)
        # self.lblWordName.setPixmap(image)

        # 发音
        if self.settings.autoPlayVoice:
            self.playWord()

    def playWord(self):
        self.mediaObject.stop()
        # voiceUrl, googleTTS = self.reciteManager.getVoiceUrl()
        voiceGender = self.reciteManager.getVoiceUrl()
        mediaSource = Phonon.MediaSource(QtCore.QUrl(voiceGender[self.settings.voiceGender]))
        self.mediaObject.setCurrentSource(mediaSource)
        self.mediaObject.play()

    def configureSettings(self):
        settingsDialog = SettingsDialog(self, self.settings)
        settingsDialog.show()

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
        sender = self.sender()
        modeTo = unicode(sender.text().toUtf8(), 'utf-8')
        if modeTo == u'学习 (&N)':
            self.changeModeAction.setText(u'复习 (&R)')
            self.changeModeAction.setStatusTip(u'复习')
            self.changeModeAction.setIcon(
                QtGui.QIcon(
                    os.path.join(self.iconDir, self.reviewIconName)
                )
            )
            self.reciteManager.setReciteMode(ReciteManager.Modes.New)
            self.nextWord()
        elif modeTo == u'复习 (&R)':
            self.changeModeAction.setText(u'学习 (&N)')
            self.changeModeAction.setStatusTip(u'学习')
            self.changeModeAction.setIcon(
                QtGui.QIcon(
                    os.path.join(self.iconDir, self.newWordIconName)
                )
            )
            self.reciteManager.setReciteMode(ReciteManager.Modes.Review)
            self.nextWord()

    def about(self):
        aboutMessage = u'\
        <p><strong>Hello Word</strong>&nbsp;%s&nbsp;\
        <font color="red"><em>%s</em></font></p>\
        <p>版权所有&nbsp;&copy;&nbsp;2010-2013&nbsp;WHYPRO</p>\
        <p>献给：Q</p>' % (self.version, 'Alpha')

        QtGui.QMessageBox.about(self, u'关于', aboutMessage)

    def keyPressEvent(self, event):
        # print self.displayStatus

        # 当拼写正确时，忽略一次键盘事件，并产生新词
        if self.displayStatus == self.DisplayStatus.Correct:
            self.nextWord()
            return

        ch = event.text()
        key = event.key()
        # print ch, '=>', key

        # Key_Space and Key_Enter 判断拼写是否正确
        if key == QtCore.Qt.Key_Space or key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter:
            # 当拼写正确时，以蓝色字体显示，并设置 Correct 标志
            if self.spelling == self.reciteManager.getWord().name:
                self.displayStatus = self.DisplayStatus.Correct
                # 设置颜色
                palette = QtGui.QPalette()
                palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(0x33, 0x99, 0xee))
                self.lblWordName.setPalette(palette)
                # 生成该单词背诵数据，并写入文件
                self.reciteManager.saveRecord()
            # 当拼写错误时，以红色字体显示，并设置 Wrong 标志
            else:
                if self.displayStatus != self.DisplayStatus.Wrong:
                    # 防止陌生度连续增加
                    self.reciteManager.increaseStrange()
                    self.spelling = ""
                    # 设置颜色
                    palette = QtGui.QPalette()
                    palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(0xff, 0x66, 0x66))
                    self.lblWordName.setPalette(palette)
                    self.lblWordName.setText(self.reciteManager.getWord().name)
                    self.displayStatus = self.DisplayStatus.Wrong
            return
        # '.' 跳过该单词
        if ch == '.':
            self.nextWord()
            return
        # '/' 发音
        if ch == '/':
            self.playWord()
            return
        # 合法输入
        if ch in self.acceptList:
            # 保证拼写长度小于单词长度
            if len(self.spelling) < len(self.reciteManager.getWord().name):
                self.spelling += ch
                self.lblWordName.setText(self.spelling)
                # 设置颜色
                palette = QtGui.QPalette()
                palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.black)
                self.lblWordName.setPalette(palette)
            self.displayStatus = self.DisplayStatus.Input
            return
        # 退格键删除最后一个字符
        if key == QtCore.Qt.Key_Backspace:
            if self.spelling:
                self.spelling = self.spelling[0:-1]
                self.lblWordName.setText(self.spelling)
                self.displayStatus = self.DisplayStatus.Input
            return

    def initSysTray(self):
        self.sysTrayMenu = QtGui.QMenu(self)
        self.sysTrayMenu.addSeparator()
        self.sysTrayMenu.addAction(self.exitAction)

        self.sysTrayIcon = QtGui.QSystemTrayIcon(
            QtGui.QIcon(os.path.join(self.iconDir, self.sysTrayIconName)),
            self,
        )
        self.sysTrayIcon.activated.connect(self.iconActivated)
        # self.connect(self.sysTrayIcon, QtCore.SIGNAL('activated()'), self.iconActivated)
        self.sysTrayIcon.messageClicked.connect(self.messageClicked)
        self.sysTrayIcon.setContextMenu(self.sysTrayMenu)

    def iconActivated(self, reason):
        if reason == QtGui.QSystemTrayIcon.Trigger:
            self.show()
            self.sysTrayIcon.hide()
        elif reason == QtGui.QSystemTrayIcon.DoubleClick:
            pass
        elif reason == QtGui.QSystemTrayIcon.MiddleClick:
            pass

    # 点击系统托盘信息的响应处理
    def messageClicked(self):
        pass

    def closeEvent(self, event):
        if not QtGui.QSystemTrayIcon.isSystemTrayAvailable():
            event.accept()
        else:
            self.hide()
            self.sysTrayIcon.show()
            self.sysTrayIcon.showMessage(u"Hello Word", u"我在这里，点击我继续背单词哦～", QtGui.QSystemTrayIcon.NoIcon)
            event.ignore()


class SingleApplication(QtGui.QApplication):
    def __init__(self, argv):
        super(SingleApplication, self).__init__(argv)
        self.isSingle = True

        self.setApplicationName('HelloWord')
        serverName = self.applicationName()
        socket = QtNetwork.QLocalSocket()
        socket.connectToServer(serverName)
        if socket.waitForConnected(1000):
            # print u'已存在一个实例'
            self.isSingle = False
            return
        # print u'建立本地服务器'
        self.server = QtNetwork.QLocalServer(self)
        # self.server.listen(serverName)
        self.server.newConnection.connect(self.newLocalConnection)
        if not self.server.listen(serverName):
            #     print '听'
            # 防止程序崩溃时,残留进程服务,移除之
            # 确保监听成功
            if self.server.serverError() == QtNetwork.QAbstractSocket.AddressInUseError and \
                    QtCore.QFile.exists(self.server.serverName()):
                QtCore.QFile.remove(self.server.serverName())
        #       print u'什么情况？'
                self.server.listen(serverName)

    def newLocalConnection(self):
        #self.activeWindow().show()
        socket = self.server.nextPendingConnection()
        if not socket:
            return
        # 其他处理

    def isSingle(self):
        return self.isSingle

if __name__ == '__main__':
    iconDir = 'res/icons/'
    splashIconName = 'splash.png'
    mainIconName = 'main.png'

    app = SingleApplication(sys.argv)
    if not app.isSingle:
        QtGui.QMessageBox.information(
            None,
            "Hello Word",
            u"程序已经在运行了哦~",
        )
        app.quit()
    else:
        # 显示 splash
        splash = QtGui.QSplashScreen(QtGui.QPixmap(os.path.join(iconDir, splashIconName)))
        splash.show()
        splash.showMessage(u'孵化中...', QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter, QtCore.Qt.white)
        # 主窗体
        m = Window()
        splash.showMessage(u'孵化完成!', QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter, QtCore.Qt.white)
        m.show()
        # 主窗体加载完成后释放
        splash.finish(m)
        del splash
        app.exec_()


# DONE: 只运行一个实例
# TODO: 复习提示
# DONE: 单词发音
# TODO: 设置
# TODO: 词汇统计，确定按钮，曲线