# -*- coding: utf-8 -*-
import sys
import os

from PyQt5 import QtWidgets, QtCore, QtGui

from .ui_main_window import Ui_MainWindow
from ..config import Config


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    # 显示状态
    class DisplayStatus:
        Display, Input, Correct, Wrong = range(4)

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.menu_sys_tray = QtWidgets.QMenu(self)
        self.sys_tray_icon = QtWidgets.QSystemTrayIcon(self)

        # self.lexicon_dir = Config.lexicon_dir
        self.config = Config()

        self.init_window()
        self.init_menu()
        self.init_slot()
        self.init_sys_tray()

        self.set_new_mode()

    def init_window(self):
        # windowTitle = self.windowTitle + ' | ' + self.reciteManager.getLexiconName()
        # self.setWindowTitle(windowTitle)

        # self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint)
        self.setWindowFlags(
            QtCore.Qt.CustomizeWindowHint |
            QtCore.Qt.WindowMinimizeButtonHint |
            QtCore.Qt.WindowCloseButtonHint
        )

        # 根据屏幕大小设置窗口大小，并居中
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        width = height = screen.width() / 3
        self.setFixedSize(width, height)
        self.move((screen.width()-width)/2, (screen.height()-height)/2)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        # self.setWindowState(self.windowState() | QtCore.Qt.WindowFullScreen)  # 窗口全屏

    def init_menu(self):
        pass

    def init_slot(self):
        self.action_choose_lexicon.triggered.connect(self.choose_lexicon)
        self.action_new_mode.triggered.connect(self.set_new_mode)
        self.action_review_mode.triggered.connect(self.set_review_mode)

        self.action_help.triggered.connect(self.show_help)
        self.action_about.triggered.connect(self.show_about)
        self.action_exit.triggered.connect(QtWidgets.qApp.quit)

    def choose_lexicon(self):
        file_path = QtWidgets.QFileDialog().getOpenFileName(
            parent=self,
            caption='选择词库',
            directory=self.config.lexicon_dir,
            filter='词库文件 (*.lxc);;所有文件 (*.*)',
        )[0]
        # print(file_path)
        if file_path:
            self.statusbar.showMessage(file_path)
            # self.reciteManager.setLexicon(filePath)
            # windowTitle = self.windowTitle + ' | ' + self.reciteManager.getLexiconName()
            # self.setWindowTitle(windowTitle)
            # self.nextWord()

    def set_new_mode(self):
        self.menu_file.removeAction(self.action_new_mode)
        # insert action_review_mode before action_settings
        self.menu_file.insertAction(self.action_settings, self.action_review_mode)
        self.toolbar.removeAction(self.action_new_mode)
        self.toolbar.insertAction(self.action_settings, self.action_review_mode)

        # self.reciteManager.setReciteMode(ReciteManager.Modes.New)
        # self.nextWord()

    def set_review_mode(self):
        self.menu_file.removeAction(self.action_review_mode)
        self.menu_file.insertAction(self.action_settings, self.action_new_mode)
        self.toolbar.removeAction(self.action_review_mode)
        self.toolbar.insertAction(self.action_settings, self.action_new_mode)

    def show_help(self):
        help_message = """
            <p>【控制】<br />
            "<b>.</b>" 键跳过当前单词，"<b>/</b>" 键发音；"<b>Esc</b>" 键将程序最小化到托盘。</p>
            <p>【拼写】<br />
            <b>字母</b>键开始拼写；<b>空格</b>键或<b>回车</b>键检查拼写；<b>退格</b>键修正拼写。</p>
        """
        QtWidgets.QMessageBox().information(self, '按键说明', help_message, QtWidgets.QMessageBox.Ok)

    def show_about(self):
        about_message = (
            '<p><strong>Hello Word</strong>&nbsp;{version}&nbsp;'
            '<font color="red"><em>{version_type}</em></font></p>'
            '<p>版权所有&nbsp;&copy;&nbsp;2010-2013&nbsp;WHYPRO</p>'
            '<p>献给：Qi~</p>'
        ).format(version=self.config.version, version_type='Alpha')

        QtWidgets.QMessageBox().about(self, '关于', about_message)

        # sender = self.sender()

        # modeTo = unicode(self.changeModeAction.text().toUtf8(), 'utf-8')
        #
        # if modeTo == u'学习 (&N)':
        #     self.changeModeToNew()
        # elif modeTo == u'复习 (&R)':
        #     self.changeModeToReview()

    def init_sys_tray(self):
        self.menu_sys_tray.addAction(self.action_exit)
        self.sys_tray_icon.setIcon(QtGui.QIcon(os.path.join(self.config.icon_dir, self.config.sys_tray_icon_name)))
        self.sys_tray_icon.setContextMenu(self.menu_sys_tray)
        self.sys_tray_icon.activated.connect(self.sys_tray_icon_activated)
        self.sys_tray_icon.messageClicked.connect(self.sys_tray_message_clicked)

    def sys_tray_icon_activated(self, reason):
        if reason == QtWidgets.QSystemTrayIcon.Trigger:
            self.show()
            self.sys_tray_icon.hide()
        elif reason == QtWidgets.QSystemTrayIcon.DoubleClick:
            pass
        elif reason == QtWidgets.QSystemTrayIcon.MiddleClick:
            pass

    # 点击系统托盘信息的响应处理
    def sys_tray_message_clicked(self):
        self.sys_tray_icon_activated(QtWidgets.QSystemTrayIcon.Trigger)
        # self.changeModeToReview()

    def closeEvent(self, event):
        if not self.sys_tray_icon.isSystemTrayAvailable():
            event.accept()
        else:
            self.hide()
            self.sys_tray_icon.show()
            # self.sys_tray_icon.showMessage('Hello Word', '我在这里，点击我继续背单词哦～', QtWidgets.QSystemTrayIcon.NoIcon, 5000)
            event.ignore()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())

