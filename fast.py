#!/usr/bin/env python3

import bz2
import collections
import csv
import json
import sys
import time
import xml.etree.ElementTree as et


POLISH_LETTERS = ['a', 'ą', 'b', 'c', 'ć', 'd', 'e', 'ę', 'f', 'g', 'h', 'i', 'j', 'k',
                  'l', 'ł', 'm', 'n', 'ń', 'o', 'ó', 'p', 'q', 'r', 's', 'ś', 't', 'u',
                  'v', 'w', 'x', 'y', 'z', 'ź', 'ż', 'A', 'Ą', 'B', 'C', 'Ć', 'D', 'E',
                  'Ę', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'Ł', 'M', 'N', 'Ń', 'O', 'Ó',
                  'P', 'Q', 'R', 'S', 'Ś', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'Ź', 'Ż']

idx_filename = sys.argv[1]
path_name = idx_filename.rsplit('/',1)
dat_filename = path_name[0]+'/'+path_name[1].replace('-index', '',).replace('txt', 'xml')

timestamp = time.time()
start_timestamp = timestamp
offsets = set()
with bz2.open(idx_filename, mode='rt', encoding='UTF-8') as f:
    for line in f:
        offsets.add(int(line.split(':')[0]))

sorted_offsets = sorted(offsets)
total = len(sorted_offsets)
word_count = collections.defaultdict(int)
f = open(dat_filename, mode='rb')
for n, (start, end) in enumerate(zip(sorted_offsets, sorted_offsets[1:])):
    length = end - start
    prev_timestamp = timestamp
    timestamp = time.time()
    print('{}/{}. {}-{}={}. time={:.3}s({}s). words={}. mem={}kB'.format(
          n, total, end, start, length, timestamp-prev_timestamp,
          int(timestamp-start_timestamp), len(word_count), int(sys.getsizeof(word_count)/1024)))
    decompressor = bz2.BZ2Decompressor()
    f.seek(start)
    data = f.read(length)
    text = decompressor.decompress(data).decode('UTF-8')
    xml_obj = et.fromstringlist(["<root>", text, "</root>"])
    for page_obj in xml_obj.findall('page'):
        article_body = page_obj.find('revision').find('text').text
        word = ''
        for ch in article_body:
            if ch in POLISH_LETTERS:
                word += ch
            else:
                word_count[word] += 1
                word = ''
f.close()

f = open(idx_filename+'.csv', mode='wt', encoding='UTF-8')
writer = csv.DictWriter(f, fieldnames=['count', 'word'])
writer.writeheader()
for w, c in word_count.items():
    writer.writerow({'word': w, 'count': c})
f.close()
