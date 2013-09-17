# -*- coding: utf-8 -*-
import os
import time
import random
from pystardict import Dictionary
from models import Word, ReciteRecord, Ebbinghaus
from threading import Thread
from PyQt4 import QtGui
try:
    import cPickle as pickle
except ImportError:
    import pickle


class DictManager:
    def __init__(self, dictPath, dictPrefix):
        self.dictionary = Dictionary(os.path.join(dictPath, dictPrefix))

    def getWordByName(self, wordName):
        try:
            data = self.dictionary[wordName].decode('utf-8', 'ignore')
        except KeyError, e:
            print u'未找到单词：%s' % "".join(e.message)
            return None
        else:
            if data[0] == '*':
                phonetic, interp = data.split('\n', 1)
                phonetic = phonetic[1:]
            else:
                phonetic = ""
                interp = data

            word = Word()
            word.name = wordName
            word.phonetic = phonetic
            word.interp = interp
            return word

    def getRandomWord(self):
        # 随机取词
        name = "".join(random.choice(self.dictionary.idx._idx.keys()))
        word = self.getWordByName(name)
        return word


class RecordManager:
    def __init__(self, recordPath, dictManager):
        self.recordPath = recordPath
        self.dictManager = dictManager
        self.records = []
        self.loadRecords()
        self.ebbinghaus = Ebbinghaus(self.records)

    def saveRecords(self):
        dirname = os.path.dirname(self.recordPath)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        f = open(self.recordPath, 'wb')
        pickle.dump(self.records, f)
        f.close()

    def loadRecords(self):
        if os.path.exists(self.recordPath):
            f = open(self.recordPath, 'rb')
            self.records = pickle.load(f)
            f.close()
            return True
        else:
            print u'记录文件不存在'
            return False

    def getRecords(self):
        return self.records

    def addRecord(self, record):
        for r in self.records:
            if r.wordName == record.wordName:
                self.records.remove(r)
                self.records.append(record)
                return
        self.records.append(record)

    def getRandomRecord(self):
        # 将需要背诵的单词加入 needReciteRecords 列表
        needReciteWords = self.ebbinghaus.getNeedReciteWords()

        # 从复习列表中随机取出单词
        if len(needReciteWords) > 0:
            wordName = random.choice(needReciteWords).wordName
            word = self.dictManager.getWordByName(wordName)
            return word
        else:
            # 当没有需要复习的单词时返回 None
            return None


class NewWordManager:
    def __init__(self, lexPath, dictManager):
        self.lexPath = lexPath
        self.dictManager = dictManager

    def getRandomWord(self):
        # try
        f = open(self.lexPath, 'r')
        lines = [line.strip() for line in f.readlines()]
        f.close()

        while True:
            name = random.choice(lines)
            word = self.dictManager.getWordByName(name)
            # 如果获取失败，则尝试再次获取
            if word:
                break
        return word


class ReciteManager:
    class Modes:
        New, Review = range(2)

    def __init__(self, lexPath, recordPath, dictPath, dictPrefix):
        self.reciteMode = self.Modes.New
        self.currentWord = None
        self.strange = 0

        self.dictManager = DictManager(dictPath, dictPrefix)
        self.newWordManager = None
        self.recordManager = RecordManager(recordPath, self.dictManager)

        self.setLexicon(lexPath)

    # 陌生度++
    def increaseStrange(self):
        self.strange += 1
        return self.strange

    # 陌生度清零
    def resetStrange(self):
        self.strange = 0

    # 返回词库名
    def getLexiconName(self):
        return self.lexiconName

    # 返回记忆模式
    def getReciteMode(self):
        return self.reciteMode

    # 设置记忆模式
    def setReciteMode(self, mode):
        self.reciteMode = mode

    # 设置词库
    def setLexicon(self, lexPath):
        self.newWordManager = NewWordManager(lexPath, self.dictManager)
        self.lexiconName = os.path.basename(lexPath).split('.')[0]

    def getWord(self):
        return self.currentWord

    def getVoiceUrl(self):
        googleTTS = 'http://translate.google.com/translate_tts?q=%s&tl=en' % self.currentWord.name
        voiceUrl = 'http://www.gstatic.com/dictionary/static/sounds/de/0/%s.mp3' % self.currentWord.name
        return voiceUrl, googleTTS

    def nextWord(self):
        if self.reciteMode == self.Modes.New:
            while True:
                currentWord = self.newWordManager.getRandomWord()
                if currentWord not in self.recordManager.getRecords():
                    break
        elif self.reciteMode == self.Modes.Review:
            while True:
                currentWord = self.recordManager.getRandomRecord()
                if currentWord not in self.recordManager.getRecords():
                    break

        self.strange = 0
        self.currentWord = currentWord
        return currentWord

    def saveRecord(self):
        if self.reciteMode == self.Modes.New:
            reciteRecord = ReciteRecord(
                self.currentWord.name,
                time.time(),            # 首次记忆时间
                time.time(),            # 上次记忆时间
                0,                      # 阶段
                self.strange,           # 陌生度
            )

            self.recordManager.addRecord(reciteRecord)
        elif self.reciteMode == self.Modes.Review:
            for record in self.recordManager.getRecords():
                if self.currentWord.name == record.wordName:
                    reciteRecord = ReciteRecord(
                        record.wordName,
                        record.startTime,
                        time.time(),
                        record.stage + 1,
                        record.strange + self.strange,
                    )
                    self.recordManager.addRecord(reciteRecord)
                    break
        self.recordManager.saveRecords()


class SettingsManager:
    class VoiceGender:
        (Male, Female) = range(2)

    def __init__(self, settingsPath):
        self.settingsPath = settingsPath
        self.settings = {}
        if not self.loadSettings():
            self.initSettings()

    def initSettings(self):
        self.settings.clear()
        self.settings['autoPlayVoice'] = True   # 自动发音
        self.settings['voiceGender'] = self.VoiceGender.Male
        self.settings['reciteHintInterval'] = 30   # 复习间隔，分钟
        self.settings['showGuide'] = True   # 显示向导

    def saveSettings(self):
        dirname = os.path.dirname(self.settingsPath)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        f = open(self.settingsPath, 'wb')
        pickle.dump(self.settings, f)
        f.close()

    def loadSettings(self):
        self.initSettings()
        if os.path.exists(self.settingsPath):
            f = open(self.settingsPath, 'rb')
            settings = pickle.load(f)
            f.close()
            self.settings.update(settings)
            return True
        else:
            print u'记录文件不存在'
            return False


# 复习提示，在系统托盘显示提示消息
class EbbinghausManager(Thread):
    def __init__(self, window):
        super(EbbinghausManager, self).__init__()
        self.window = window
        self.setDaemon(True)

    def run(self):
        time.sleep(60)
        while True:
            needReciteWords = self.window.reciteManager.recordManager.ebbinghaus.getNeedReciteWords()
            count = len(needReciteWords)
            if count:
                self.window.sysTrayIcon.showMessage(
                    u"复习提示",
                    u"您有%d个单词需要复习，点击我开始复习哦～" % count,
                    QtGui.QSystemTrayIcon.NoIcon
                )
            print self.window.settingsManager.settings['reciteHintInterval']
            time.sleep(self.window.settingsManager.settings['reciteHintInterval'] * 60)


if __name__ == '__main__':
    dictManager = DictManager('stardict-langdao-ec-gb-2.4.2', 'langdao-ec-gb')
    # for i in xrange(0, 10):
    #     word = wordManager.getRandomWord()
    #     print word.name
    #     print word.phonetic
    #     print word.interp

    recordManager = RecordManager('./record/recite.dat', dictManager)
    for record in recordManager.records:
        print record.wordName
    record = ReciteRecord('good', 0, 0, 0, 0)
    recordManager.records.append(record)
    recordManager.saveRecords()

    # reciteManager = ReciteManager(u'./考研英语.txt', 'recite.dat', 'stardict-langdao-ec-gb-2.4.2', 'langdao-ec-gb')
    # reciteManager.getLexiconName()
    # reciteManager.nextWord()
    # print reciteManager.getWord().name
    # reciteManager.setReciteMode(ReciteManager.Modes.Review)
    # reciteManager.nextWord()
    # if not reciteManager.getWord():
    #     print u'没有需要复习的单词'
