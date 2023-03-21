#!/usr/bin/env python3

import bz2
import collections
import csv
import sys
import time
import tracemalloc
import xml.etree.ElementTree as Et
import filter

tracemalloc.start()
idx_filename = sys.argv[1]
path_name = idx_filename.rsplit('/', 1)
dat_filename = path_name[0]+'/'+path_name[1].replace('-index', '',).replace('txt', 'xml')

start_timestamp = time.time()
offsets = set()
with bz2.open(idx_filename, mode='rt', encoding='UTF-8') as f:
    for line in f:
        offsets.add(int(line.split(':')[0]))

sorted_offsets = sorted(offsets)
total = len(sorted_offsets)
word_count = collections.defaultdict(int)
f = open(dat_filename, mode='rb')
sum_words = 0
limit = 1e6*float(sys.argv[2])
for n, (start, end) in enumerate(zip(sorted_offsets, sorted_offsets[1:])):
    if sum_words >= limit:
        break
    length = end - start
    start_block_timestamp = time.time()
    decompressor = bz2.BZ2Decompressor()
    f.seek(start)
    data = f.read(length)
    text = decompressor.decompress(data).decode('UTF-8')
    xml_obj = Et.fromstringlist(["<root>", text, "</root>"])
    for page_obj in xml_obj.findall('page'):
        article_body = page_obj.find('revision').find('text').text
        article_body = filter.strip_wiki(article_body)
        word = ''
        for ch in article_body:
            if ch.isalpha():
                word += ch
            else:
                if len(word) > 0:
                    word_count[word] += 1
                sum_words += 1
                word = ''
        if len(word) > 0:
            word_count[word] += 1
    end_block_timestamp = time.time()
    print('{}/{}. {}-{}={}. time={:.3}s({}s). words={}. sum words={:.2} mln. mem={}MiB'.format(
          n, total, end, start, length, end_block_timestamp-start_block_timestamp,
          int(end_block_timestamp-start_timestamp), len(word_count), sum_words/1e6,
          int(tracemalloc.get_traced_memory()[0] / 1024 ** 2)))

f.close()

f = open(idx_filename+'.csv', mode='wt', encoding='UTF-8')
word_count_l = sorted(word_count.items(), key=lambda item: item[1], reverse=True)
writer = csv.DictWriter(f, fieldnames=['count', 'word'])
writer.writeheader()
for w, c in word_count_l:
    writer.writerow({'word': w, 'count': c})
f.close()
tracemalloc.stop()