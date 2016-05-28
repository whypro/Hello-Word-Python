# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import os
import random

from .dictionary import Dictionary


class Lexicon(object):
    
    def __init__(self, lexicon_path):
        self.path = lexicon_path
        self.name = os.path.splitext(os.path.basename(lexicon_path))[0]
        self.words = []
        with open(lexicon_path, 'r') as f:
            for line in f:
                self.words.append(line.strip())
        self.count = len(self.words)

    def __repr__(self):
        return '{0} {1}'.format(self.name, self.count)

    def get_random_word(self):
        return random.choice(self.words)


class ReciteManager(object):

    class ReciteMode:
        NEW, REVIEW = range(2)

    def __init__(self, dict_path, dict_prefix, lexicon_path):
        self.lexicon = None
        self.recite_mode = self.ReciteMode.NEW
        self.set_lexicon(lexicon_path)
        self.dictionary = Dictionary(dict_path=dict_path, dict_prefix=dict_prefix)
        self.current_word = None

    def set_lexicon(self, lexicon_path):
        self.lexicon = Lexicon(lexicon_path)

    def next_word(self):
        if self.recite_mode == self.ReciteMode.NEW:
            while True:
                word_name = self.lexicon.get_random_word()
                word = self.dictionary.lookup(word_name)
                if word:
                    self.current_word = word
                    break
        else:
            return self.dictionary.lookup('good')

    def get_audio(self, pron_type):
        return self.dictionary.get_audio(self.current_word)[pron_type]


if __name__ == '__main__':
    lexicon = Lexicon('./resources/lexicons/研究生入学考试词汇.lxc')
    print(lexicon)