# -*- coding: utf-8 -*-
import os
from PyQt4 import QtGui, QtCore
from PyQt4.phonon import Phonon
from managers import ReciteManager, SettingsManager
import string

from wizard import Wizard
from settingsdialog import SettingsDialog
from statdialog import StatDialog

class Window(QtGui.QMainWindow):
    # 标题
    windowTitle = 'Hello Word'

    # 版本
    version = '0.2.3'

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
    helpIconName = 'help.png'

    # 记录
    recordPath = 'dat/recite.dat'

    # 设置
    settingsPath = 'dat/config.dat'

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

        self.initAction()
        self.initMenu()
        self.initToolbar()

        self.reciteManager = ReciteManager(
            os.path.join(self.lexiconDir, self.lexiconName),
            self.recordPath,
            self.dictDir,
            self.dictPrefix
        )
        self.settingsManager = SettingsManager(self.settingsPath)

        self.initMainPanel()    # 初始化中央面板

        if self.settingsManager.settings.get('showGuide'):
            self.initWizard()

        self.initVoice()
        self.nextWord()
        self.initSysTray()
        self.initWindow()

        from managers import EbbinghausManager
        self.ebbinghausManager = EbbinghausManager(self)
        self.ebbinghausManager.start()

    def initWizard(self):
        # 显示向导，模态对话框
        wizard = Wizard(self)
        wizard.exec_()

    def initWindow(self):
        windowTitle = self.windowTitle + ' | ' + self.reciteManager.getLexiconName()
        self.setWindowTitle(windowTitle)
        self.setWindowIcon(
            QtGui.QIcon(
                os.path.join(self.iconDir, self.mainIconName)
            )
        )

        # self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint)
        self.setWindowFlags(
            QtCore.Qt.CustomizeWindowHint |
            QtCore.Qt.WindowMinimizeButtonHint |
            QtCore.Qt.WindowCloseButtonHint
        )

        # 根据屏幕大小设置窗口大小，并居中
        screen = QtGui.QDesktopWidget().screenGeometry()
        width = height = screen.width() / 3
        self.setFixedSize(width, height)
        self.move((screen.width()-width)/2, (screen.height()-height)/2)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        #self.setWindowState(self.windowState() | QtCore.Qt.WindowFullScreen)  # 窗口全屏

    def initAction(self):
        self.chooseLexAction = QtGui.QAction(u'选择词库 (&C)', self)
        self.chooseLexAction.setStatusTip(u'选择词库')
        self.chooseLexAction.setIcon(
            QtGui.QIcon(
                os.path.join(self.iconDir, self.lexiconIconName)
            )
        )
        self.chooseLexAction.triggered.connect(self.chooseLexicon)

        self.statAction = QtGui.QAction(u'词汇统计 (&S)', self)
        self.statAction.setStatusTip(u'词汇统计')
        self.statAction.setIcon(
            QtGui.QIcon(
                os.path.join(self.iconDir, self.statIconName)
            )
        )
        self.statAction.triggered.connect(self.statRecite)

        self.changeModeAction = QtGui.QAction(u'复习 (&R)', self)
        self.changeModeAction.setStatusTip(u'复习')
        self.changeModeAction.setIcon(
            QtGui.QIcon(
                os.path.join(self.iconDir, self.reviewIconName)
            )
        )
        self.changeModeAction.triggered.connect(self.changeReciteMode)

        self.settingsAction = QtGui.QAction(u'设置 (&O)', self)
        self.settingsAction.setStatusTip(u'设置')
        self.settingsAction.setIcon(
            QtGui.QIcon(
                os.path.join(self.iconDir, self.settingsIconName)
            )
        )
        self.settingsAction.triggered.connect(self.configureSettings)

        self.exitAction = QtGui.QAction(u'退出 (&X)', self)
        self.exitAction.setStatusTip(u'退出程序')
        self.exitAction.setIcon(
            QtGui.QIcon(
                os.path.join(self.iconDir, self.exitIconName)
            )
        )
        self.exitAction.triggered.connect(QtGui.qApp.quit)

        self.helpAction = QtGui.QAction(u'按键说明 (&B)', self)
        self.helpAction.setStatusTip(u'按键说明')
        self.helpAction.setIcon(
            QtGui.QIcon(
                os.path.join(self.iconDir, self.helpIconName)
            )
        )
        self.helpAction.triggered.connect(self.help)

        self.aboutAction = QtGui.QAction(u'关于 (&A)', self)
        self.aboutAction.setStatusTip(u'关于')
        self.aboutAction.setIcon(
            QtGui.QIcon(
                os.path.join(self.iconDir, self.aboutIconName)
            )
        )
        self.aboutAction.triggered.connect(self.about)

    def initMenu(self):
        # 初始化菜单栏
        self.menuBar = self.menuBar()
        self.fileMenu = self.menuBar.addMenu(u"文件 (&F)")
        self.fileMenu.addAction(self.chooseLexAction)
        self.fileMenu.addAction(self.statAction)
        self.fileMenu.addAction(self.changeModeAction)
        self.fileMenu.addAction(self.settingsAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAction)

        self.helpMenu = self.menuBar.addMenu(u"帮助 (&H)")
        self.helpMenu.addAction(self.helpAction)
        self.helpMenu.addAction(self.aboutAction)

    def initToolbar(self):
        self.toolBar = self.addToolBar(u'快捷栏')
        self.toolBar.addAction(self.chooseLexAction)
        self.toolBar.addAction(self.statAction)
        self.toolBar.addAction(self.changeModeAction)
        self.toolBar.addAction(self.settingsAction)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.helpAction)
        self.toolBar.addAction(self.aboutAction)
        #self.toolBar.addSeparator()
        #self.toolBar.addAction(self.exitAction)
        self.toolBar.setFloatable(False)

    def initMainPanel(self):
        self.lblWordName = QtGui.QLabel()
        self.lblWordName.setFont(QtGui.QFont('Times New Roman', 48, QtGui.QFont.Bold))
        # self.lblWordName.setAlignment(QtCore.Qt.AlignHCenter)

        QtGui.QFontDatabase.addApplicationFont(os.path.join(self.fontDir, self.phoneticFontName))
        self.lblPhonetic = QtGui.QLabel()
        self.lblPhonetic.setFont(QtGui.QFont('Lingoes Unicode', 14))
        # self.lblPhonetic.setAlignment(QtCore.Qt.AlignHCenter)

        self.lblInterp = QtGui.QTextEdit()
        self.lblInterp.setFont(QtGui.QFont(u'华文中宋', 20))
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
        #self.statusBar.showMessage(u'"."键跳过该单词，"/"键发音，空格键或回车键检查拼写，退格键修正拼写')

        # import urllib2
        # i = urllib2.urlopen('http://img1.51cto.com/attachment/200910/200910271256653086390.png').read()
        # image = QtGui.QPixmap()
        # image.convertFromImage(QtGui.QImage(i)
        # self.lblWordName.setPixmap(image)

        # 发音
        if self.settingsManager.settings.get('autoPlayVoice') is True:
            self.playWord()

    def playWord(self):
        voiceGender = self.settingsManager.settings.get('voiceGender')
        if voiceGender not in (SettingsManager.VoiceGender.Male, SettingsManager.VoiceGender.Female):
            return
        self.mediaObject.stop()
        # voiceUrl, googleTTS = self.reciteManager.getVoiceUrl()
        voiceUrlTuple = self.reciteManager.getVoiceUrl()
        mediaSource = Phonon.MediaSource(QtCore.QUrl(voiceUrlTuple[voiceGender]))
        self.mediaObject.setCurrentSource(mediaSource)
        self.mediaObject.play()

    def configureSettings(self):
        settingsDialog = SettingsDialog(self, self.settingsManager)
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

    def changeModeToNew(self):
        self.changeModeAction.setText(u'复习 (&R)')
        self.changeModeAction.setStatusTip(u'复习')
        self.changeModeAction.setIcon(
            QtGui.QIcon(
                os.path.join(self.iconDir, self.reviewIconName)
            )
        )
        self.reciteManager.setReciteMode(ReciteManager.Modes.New)
        self.nextWord()

    def changeModeToReview(self):
        self.changeModeAction.setText(u'学习 (&N)')
        self.changeModeAction.setStatusTip(u'学习')
        self.changeModeAction.setIcon(
            QtGui.QIcon(
                os.path.join(self.iconDir, self.newWordIconName)
            )
        )
        self.reciteManager.setReciteMode(ReciteManager.Modes.Review)
        self.nextWord()

    def changeReciteMode(self):
        # sender = self.sender()
        modeTo = unicode(self.changeModeAction.text().toUtf8(), 'utf-8')

        if modeTo == u'学习 (&N)':
            self.changeModeToNew()
        elif modeTo == u'复习 (&R)':
            self.changeModeToReview()

    def help(self):
        helpMessage = u"""
        <p>【控制】<br />
        "<b>.</b>" 键跳过当前单词，"<b>/</b>" 键发音；"<b>Esc</b>" 键将程序最小化到托盘。</p>
        <p>【拼写】<br />
        <b>字母</b>键开始拼写；<b>空格</b>键或<b>回车</b>键检查拼写；<b>退格</b>键修正拼写。</p>
        """
        QtGui.QMessageBox.information(self, u'按键说明', helpMessage)

    def about(self):
        aboutMessage = u'\
        <p><strong>Hello Word</strong>&nbsp;%s&nbsp;\
        <font color="red"><em>%s</em></font></p>\
        <p>版权所有&nbsp;&copy;&nbsp;2010-2013&nbsp;WHYPRO</p>\
        <p>献给：Qi~</p>' % (self.version, 'Alpha')

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

        # Key_Escape 最小化到托盘
        if key == QtCore.Qt.Key_Escape:
            self.close()

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
        #self.sysTrayMenu.addSeparator()
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
        self.iconActivated(QtGui.QSystemTrayIcon.Trigger)
        self.changeModeToReview()

    def closeEvent(self, event):
        if not QtGui.QSystemTrayIcon.isSystemTrayAvailable():
            event.accept()
        else:
            self.hide()
            self.sysTrayIcon.show()
            self.sysTrayIcon.showMessage(u"Hello Word", u"我在这里，点击我继续背单词哦～", QtGui.QSystemTrayIcon.NoIcon, 1000)
            event.ignore()