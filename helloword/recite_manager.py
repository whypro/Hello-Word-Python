# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import os

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
    pass


if __name__ == '__main__':
    lexicon = Lexicon('./resources/lexicons/研究生入学考试词汇.lxc')
    print(lexicon)