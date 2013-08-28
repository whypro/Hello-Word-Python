# -*- coding: utf-8 -*-
import re
in_file = open(u'./考研英语词库.txt', 'r')
# pattern = r'^([a-zA-z]+(( |-)?[a-zA-Z]+)*)$'
pattern = u'^([a-zA-Z \-]+)(\/([a-zA-z \-]+))*[\u4e00-\u9fa5]*$'
out_file = open(u'./考研英语词库_2.txt', 'w')
count = 0
for line in in_file.readlines():
    m = re.search(pattern, line.decode('utf-8'))
    if m:
        print m.groups()
        word = m.group(1)
        word = word.strip()
        if len(word) > 1:
            # 写入文件
            out_file.write(word.encode('utf-8'))
            out_file.write('\n')
            count += 1
        word = m.group(3)
        if word:
            word = word.strip()
            if len(word) > 1:
                # 写入文件
                out_file.write(word.encode('utf-8'))
                out_file.write('\n')
                count += 1



out_file.close()
in_file.close()

print count
