#! /usr/bin/env python
#-*-coding:utf-8-*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from bs4 import BeautifulSoup
import os

count = 1
packageInfo = []
htmls = os.listdir('htmls/')
for html in htmls:
    if count % 100 == 0:
        print str(count) + " Done"
    count += 1
    down_num, like_num, comment_num, size_num = 0, 0, 0, 0
    html_file = open('htmls/' + html)
    bs = BeautifulSoup(html_file.read(), 'lxml')
    div = bs.find('div', attrs = {'class': 'num-list'})

    if div == None:
        continue

    down_text = div.find('i', attrs = {'itemprop': 'interactionCount'})
    if down_text == None:
        down_num = 0
    else:
        down_text = down_text.text.strip()
        if down_text.find('万') != -1:
            down_num = float(down_text[:-2]) * 10000
        elif down_text.find('亿') != -1:
            down_num = float(down_text[:-2]) * 100000000
        else:
            down_num = float(down_text)
        down_num = int(down_num)

    like_text = div.find('span', attrs = {'class': 'item love'}).find('i')
    if like_text == None:
        like_num = 0
    else:
        like_text = like_text.text.replace(',', '').strip()
        like_num = int(like_text)

    comment_text = div.find('a', attrs = {'class': 'item last comment-open'}).find('i')
    if comment_text == None:
        comment_num = 0
    else:
        comment_text = comment_text.text.replace(',', '').strip()
        comment_num = int(comment_text)

    size_text = bs.find('dl', attrs = {'class': 'infos-list'}).find_all('dd')[0].text.replace(',', '').strip()
    if size_text[-1] == 'K':
        size_num = float(size_text[:-1]) * 1024
    elif size_text[-1] == 'M':
        size_num = float(size_text[:-1]) * 1024 * 1024
    else:
        size_num = float(size_text[:-1]) * 1024 * 1024 * 1024
    packageInfo.append([html[:-5], down_num, like_num, comment_num, size_num])

info = sorted(packageInfo, key = lambda pi : pi[1], reverse = True)
top_file = open('top_info.txt', 'w+')
for item in info:
    top_file.write(' '.join(map(str, item)) + '\n')
top_file.close()
