# -*- coding: utf-8 -*-
class Word:
    def __init__(self, name='', phonetic='', interp=''):
        self.name = name
        self.phonetic = phonetic
        self.interp = interp


class ReciteRecord:
    def __init__(self, wordName='', startTime=0, lastTime=0, stage=0, strange=0):
        self.wordName = wordName
        self.startTime = startTime
        self.lastTime = lastTime
        self.stage = stage
        self.strange = strange


import time


class Ebbinghaus:

    forgettingCurve = (
        5,			# 5分钟
        30,         # 30分钟
        12*60,      # 12小时
        1*24*60,    # 1天
        2*24*60,    # 2天
        4*24*60,    # 4天
        7*24*60,    # 7天
        15*24*60,    # 15天
    )

    def __init__(self):
        pass

    # 根据记忆曲线，判断单词是否需要复习
    def needRecite(self, record):
        self.isExpire(record)

    def isExpire(self, record):
        # 记忆曲线完成
        # record.stage == 8
        # len(forgettingCurve) == 8
        if record.stage >= len(self.forgettingCurve):
            return False

        currentTime = time.time()
        timeDiff = (currentTime - record.lastTime) / (1000 * 60)
        if timeDiff > self.forgettingCurve[record.stage]:
            return True
        else:
            return False
