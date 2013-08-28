# -*- coding: utf-8 -*-
import re
in_file = open(u'./lexicons/TOFEL.txt', 'r')
# pattern = r'^([a-zA-z]+(( |-)?[a-zA-Z]+)*)$'
#pattern = u'^([a-zA-Z \-]+)(\/([a-zA-z \-]+))*[\u4e00-\u9fa5]*$'
pattern = u'^([a-zA-Z \-]+)$'
out_file = open(u'./lexicons/TOFEL_2.txt', 'w')
count = 0
for line in in_file.readlines():
    m = re.search(pattern, line.decode('utf-8'))
    if m:

        word = m.group(1)
        word = word.strip()
        print word
        if len(word) > 1:
            # 写入文件
            out_file.write(word.encode('utf-8'))
            out_file.write('\n')
            count += 1
        # word = m.group(3)
        # if word:
        #     word = word.strip()
        #     if len(word) > 1:
        #         # 写入文件
        #         out_file.write(word.encode('utf-8'))
        #         out_file.write('\n')
        #         count += 1



out_file.close()
in_file.close()

print count
