# -*- coding: utf-8 -*-
import os
from PyQt4 import QtGui


class WizardPage(QtGui.QWizardPage):
    def __init__(self, parent, title, text):
        super(WizardPage, self).__init__(parent)
        self.setTitle(title)
        label = QtGui.QLabel(text)
        label.setWordWrap(True)
        label.setFont(QtGui.QFont(u'微软雅黑', 10))
        layout = QtGui.QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)


class WizardPageThree(QtGui.QWizardPage):
    def __init__(self, parent):
        super(WizardPageThree, self).__init__(parent)
        #self.setTitle(u'向导')
        #label = QtGui.QLabel(text)
        #label.setWordWrap(True)
        neverCheck = QtGui.QCheckBox(u'不再显示')
        neverCheck.setChecked(True)
        neverCheck.setFont(QtGui.QFont(u'微软雅黑', 10))

        layout = QtGui.QVBoxLayout()
        layout.addWidget(neverCheck)
        self.setLayout(layout)


class Wizard(QtGui.QWizard):
    iconDir = 'res/icons/'
    mainIconName = 'hint.png'

    def __init__(self, parent=None):
        super(Wizard, self).__init__(parent)
        self.pageOne = WizardPage(
            self,
            u'控制',
            u'<p>"<b>.</b>"键跳过当前单词</p>'
            u'<p>"<b>/</b>"键发音</p>'
            u'<p>"<b>Esc</b>"键将程序最小化到托盘</p>')

        self.pageTwo = WizardPage(
            self,
            u'拼写',
            u'<p>"<b>字母</b>"键开始拼写</p>'
            u'<p>"<b>空格</b>"键或"<b>回车</b>"键查看答案</p>'
            u'<p>"<b>退格</b>"键更正拼写</p>')

        self.pageThree = WizardPageThree(self)

        self.addPage(self.pageOne)
        self.addPage(self.pageTwo)
        self.addPage(self.pageThree)

        self.setWindowTitle(u'使用说明')
        self.setButtonText(QtGui.QWizard.BackButton, u'上一页')
        self.setButtonText(QtGui.QWizard.NextButton, u'下一页')
        self.setButtonText(QtGui.QWizard.FinishButton, u'开始使用')

        buttonLayout = [
            QtGui.QWizard.Stretch,
            QtGui.QWizard.BackButton,
            QtGui.QWizard.NextButton,
            QtGui.QWizard.FinishButton,
        ]
        self.setButtonLayout(buttonLayout)

        self.setWindowIcon(
            QtGui.QIcon(
                os.path.join(self.iconDir, self.mainIconName)
            )
        )

        # 根据屏幕大小设置窗口大小，并居中
        #screen = QtGui.QApplication.desktop()
        #screen = QtGui.QDesktopWidget().screenGeometry()
        #width = 500
        #height = 390
        #self.setFixedSize(width, height)
        #self.move((screen.width()-width)/2, (screen.height()-height)/2)
        #self.setFocusPolicy(QtCore.Qt.StrongFocus)