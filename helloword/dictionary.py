# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
import os
import json

import requests

from .deps.pystardict import Dictionary as StarDict


class Word(object):
    
    def __init__(self):
        self.name = None
        self.pronunciation = None
        self.definition = None

    def __repr__(self):
        return '{0} {1}'.format(self.name, self.pronunciation)


class ShanbayAPI(object):

    search_url = 'https://api.shanbay.com/bdc/search/?word={0}'
    
    def get_audio(self, word_name):
        url = self.search_url.format(word_name)
        resp = requests.get(url)
        data = json.loads(resp.text)
        # print(data)
        return dict(uk=data['data']['uk_audio'], us=data['data']['us_audio'])

    def _save_audio(self):
        pass


class GoogleAPI(object):

    audio_url = 'http://www.gstatic.com/dictionary/static/sounds/de/0/{0}.mp3'

    def get_audio(self, word_name):
        url = self.audio_url.format(word_name)
        return url


class Dictionary(object):
    
    def __init__(self, dict_path, dict_prefix):
        self.stardict = StarDict(filename_prefix=os.path.join(dict_path, dict_prefix), in_memory=True)
        self.shanbay_api = ShanbayAPI()

    def lookup(self, word_name):
        if word_name not in self.stardict:
            # print u'未找到单词：%s' % "".join(e.message)
            return None
        else:
            data = self.stardict[word_name]

            if data[0] == '*':
                pronunciation, definition = data.split('\n', 1)
                pronunciation = pronunciation[1:]
            else:
                pronunciation = ""
                definition = data

            word = Word()
            word.name = word_name
            word.pronunciation = pronunciation
            word.definition = definition
            print(word)
            return word

    def get_audio(self, word):
        return self.shanbay_api.get_audio(word.name)

    def get_image(self, word):
        pass


if __name__ == '__main__':
    d = Dictionary('./resources/dicts/stardict-langdao-ec-gb-2.4.2', 'langdao-ec-gb')
    word = d.lookup('good')
    import sys 
    print(sys.version)
    print(d.get_audio(word))

