# -*- coding: utf-8 -*-
import os
import time
import random
from pystardict import Dictionary
from models import Word, ReciteRecord, Ebbinghaus
import pickle


class RecordManager:
    def __init__(self, recordPath):
        self.recordPath = recordPath
        self.records = []
        self.loadRecords()

    def saveRecords(self):
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
            return False

    def getRecords(self):
        return self.records

    def addRecord(self, record):
        for r in self.records:
            if r.wordName == record.wordName:
                self.records.remove(r)
                self.records.append(record)
                break
        self.records.append(record)

    def getRandomRecord(self):
        # 将需要背诵的单词加入 needReciteRecords 列表
        ebbinghaus = Ebbinghaus()
        needReciteRecords = []
        for record in self.records:
            if ebbinghaus.needRecite(record):
                needReciteRecords.add(record)

        # 从复习列表中随机取出单词
        if len(needReciteRecords) > 0:
            wordName = random.choice(needReciteRecords).word
            word = self.wordManager.getWordByName(wordName)
            return word
        else:
            # 当没有需要复习的单词时返回 None
            return None


class NewWordManager:
    def __init__(self, lexPath, dictPath, dictPrefix):
        self.lexPath = lexPath
        self.dictionary = Dictionary(os.path.join(dictPath, dictPrefix))

    def getRandomWord(self):
        # try
        f = open(self.lexPath, 'r')
        lines = [line.strip() for line in f.readlines()]
        f.close()

        while True:
            name = random.choice(lines)
            word = self.getWordByName(name)
            # 如果获取失败，则尝试再次获取
            if word:
                break
        return word

    def getRandomWordFromDict(self):
        # 随机取词
        name = "".join(random.choice(self.dictionary.idx._idx.keys()))
        data = self.dictionary[name].decode('utf-8', 'ignore')
        if data[0] == '*':
            phonetic, interp = data.split('\n', 1)
            phonetic = phonetic[1:]
        else:
            phonetic = ""
            interp = data

        word = Word()
        word.name = name
        word.phonetic = phonetic
        word.interp = interp
        return word

    def getWordByName(self, wordName):
        try:
            data = self.dictionary[wordName].decode('utf-8', 'ignore')
        except KeyError, e:
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


class ReciteManager:
    class Modes:
        New, Review = range(0, 2)

    def __init__(self, recordPath):
        self.reciteMode = self.Modes.New
        self.currentWord = None
        self.strange = 0
        self.wordManager = None
        self.recordManager = RecordManager(recordPath)

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
    def setLexicon(self, lexPath, dictPath, dictPrefix):
        self.wordManager = WordManager(lexPath, dictPath, dictPrefix)
        self.lexiconName = ''

    def getWord(self):
        return self.currentWord

    def nextWord(self):
        if self.reciteMode == self.Modes.New:
            while True:
                currentWord = self.wordManager.getRandomWord()
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

if __name__ == '__main__':
    # wordManager = WordManager(u'./考研英语.txt', 'stardict-langdao-ec-gb-2.4.2', 'langdao-ec-gb')
    # for i in xrange(0, 10):
    #     word = wordManager.getRandomWord()
    #     print word.name
    #     print word.phonetic
    #     print word.interp

    # recordManager = RecordManager('./recite.dat')
    # print recordManager.records[0].wordName
    # record = ReciteRecord('good')
    # recordManager.records.append(record)
    # recordManager.saveAllRecords()

    reciteManager = ReciteManager('recite.dat')
    reciteManager.setLexicon(u'./考研英语.txt', 'stardict-langdao-ec-gb-2.4.2', 'langdao-ec-gb')
    reciteManager.getLexiconName()
    reciteManager.nextWord()
    print reciteManager.getWord().name
    reciteManager.setReciteMode(ReciteManager.Modes.Review)
    reciteManager.nextWord()
    if not reciteManager.getWord():
        print u'没有需要复习的单词'
