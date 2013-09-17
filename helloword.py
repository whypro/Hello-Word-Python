# /usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
from PyQt4 import QtGui, QtCore, QtNetwork

from ui.window import Window


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

        
        # 窗体加载完成后释放
        splash.finish(m)
        del splash

        m.show()

        app.exec_()


# DONE: 只运行一个实例
# TODO: 复习提示
# DONE: 单词发音
# TODO: 设置
# TODO: 词汇统计，确定按钮，绘制曲线
# TODO: 多字典选择
# TODO: 多语种记忆