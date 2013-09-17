# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore


class SettingsDialog(QtGui.QDialog):
    def __init__(self, parent=None, settingsManager=None):
        super(SettingsDialog, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle(u'设置')

        self.settingsManager = settingsManager

        self.initVoiceGroup()

        self.reciteHintIntervalSpin = QtGui.QSpinBox(self)
        self.reciteHintIntervalSpin.setRange(1, 120)
        self.reciteHintIntervalSpin.setSingleStep(1)
        self.reciteHintIntervalSpin.setSuffix(u' 分钟')
        reciteHintIntervalLabel = QtGui.QLabel(u'托盘提醒间隔')
        #reciteHintIntervalUnitLabel = QtGui.QLabel(u'分钟')

        self.reciteHintIntervalLayout = QtGui.QHBoxLayout()
        self.reciteHintIntervalLayout.addWidget(reciteHintIntervalLabel)
        self.reciteHintIntervalLayout.addWidget(self.reciteHintIntervalSpin)
        #self.reciteHintIntervalLayout.addWidget(reciteHintIntervalUnitLabel)

        self.showGuideCheck = QtGui.QCheckBox(u'启动时显示向导')

        self.initButton()

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.voiceGroup)
        mainLayout.addLayout(self.reciteHintIntervalLayout)
        mainLayout.addWidget(self.showGuideCheck)
        mainLayout.addWidget(self.buttonBox)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)

        self.initConfig()

    def initVoiceGroup(self):
        self.voiceGroup = QtGui.QGroupBox(u'发音设置')

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

        self.voiceGroup.setLayout(voiceLayout)

    def initButton(self):

        self.buttonBox = QtGui.QDialogButtonBox(parent=self)
        okButton = QtGui.QPushButton(u'保存')
        okButton.clicked.connect(self.accept)
        cancelButton = QtGui.QPushButton(u'取消')
        cancelButton.clicked.connect(self.accept)
        resetButton = QtGui.QPushButton(u'重置')
        resetButton.clicked.connect(self.resetConfig)

        self.buttonBox.addButton(okButton, QtGui.QDialogButtonBox.AcceptRole)
        self.buttonBox.addButton(cancelButton, QtGui.QDialogButtonBox.RejectRole)
        self.buttonBox.addButton(resetButton, QtGui.QDialogButtonBox.ResetRole)

    def initConfig(self):
        self.autoPlayCheck.setChecked(self.settingsManager.settings['autoPlayVoice'])
        self.voiceGenderCombo.setCurrentIndex(self.settingsManager.settings['voiceGender'])
        self.reciteHintIntervalSpin.setValue(self.settingsManager.settings['reciteHintInterval'])
        self.showGuideCheck.setChecked(self.settingsManager.settings.get('showGuide', True))

    def accept(self):
        # 保存配置
        self.settingsManager.settings['autoPlayVoice'] = self.autoPlayCheck.isChecked()
        self.settingsManager.settings['voiceGender'] = self.voiceGenderCombo.currentIndex()
        self.settingsManager.settings['reciteHintInterval'] = self.reciteHintIntervalSpin.value()
        self.settingsManager.settings['showGuide'] = self.showGuideCheck.isChecked()
        self.settingsManager.saveSettings()
        super(SettingsDialog, self).accept()

    def resetConfig(self):
        self.settingsManager.initSettings()
        self.initConfig()
