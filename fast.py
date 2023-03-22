#!/usr/bin/env python3

import bz2
import collections
import csv
import sys
import time
import tracemalloc
import xml.etree.ElementTree as Et
import filter

def process_one_article(article_body, word_count,sum_words):
    if not article_body:
        return sum_words
    article_body = filter.strip_wiki(article_body)
    word = ''
    for ch in article_body:
        if ch.isalnum() or ch=="'":
            word += ch
        else:
            if len(word) > 0:
                word_count[word] += 1
            sum_words += 1
            word = ''
    if len(word) > 0:
        word_count[word] += 1
    return sum_words


def process_one_article_file(filename):
    word_count = collections.defaultdict(int)
    with open(filename, "r") as f:
        article_body = f.read()
    sum_words = process_one_article(article_body,word_count,0)

def process_one_block(text, word_count, sum_words, limit):
    xml_obj = Et.fromstringlist(["<root>", text, "</root>"])
    for page_obj in xml_obj.findall('page'):
        article_body = page_obj.find('revision').find('text').text
        sum_words = process_one_article(article_body, word_count, sum_words)
        if limit>0 and sum_words >= limit:
            break
    return sum_words
def read_index(idx_filename):
    offsets = set()
    with bz2.open(idx_filename, mode='rt', encoding='UTF-8') as f:
        for line in f:
            offsets.add(int(line.split(':')[0]))
    sorted_offsets = sorted(offsets)
    return sorted_offsets

def process_wiki(idx_filename,dat_filename):
    start_timestamp = time.time()
    sorted_offsets = read_index(idx_filename)
    total = len(sorted_offsets)
    end_timestamp = time.time()
    print('Index: total positions: {} time={:.3}s'.format(total, end_timestamp - start_timestamp))
    start_timestamp = time.time()
    word_count = collections.defaultdict(int)
    f = open(dat_filename, mode='rb')
    sum_words = 0
    limit = 1e6 * float(sys.argv[2])
    for n, (start, end) in enumerate(zip(sorted_offsets, sorted_offsets[1:])):
        length = end - start
        start_block_timestamp = time.time()
        decompressor = bz2.BZ2Decompressor()
        f.seek(start)
        data = f.read(length)
        text = decompressor.decompress(data).decode('UTF-8')
        sum_words = process_one_block(text, word_count, sum_words, limit)
        end_block_timestamp = time.time()
        print('{}/{}. {}-{}={}. time={:.3}s({}s). words={}. sum words={:.3} mln. mem={}MiB'.format(
            n, total, end, start, length, end_block_timestamp - start_block_timestamp,
            int(end_block_timestamp - start_timestamp), len(word_count), sum_words / 1e6,
            int(tracemalloc.get_traced_memory()[0] / 1024 ** 2)))
        if limit>0 and sum_words >= limit:
            break
    f.close()
    f = open(idx_filename + '.csv', mode='wt', encoding='UTF-8')
    word_count_l = sorted(word_count.items(), key=lambda item: item[1], reverse=True)
    writer = csv.DictWriter(f, fieldnames=['count', 'word'])
    writer.writeheader()
    for w, c in word_count_l:
        writer.writerow({'word': w, 'count': c})
    f.close()

if __name__ == '__main__':
    tracemalloc.start()
    idx_filename = sys.argv[1]
    path_name = idx_filename.rsplit('/', 1)
    dat_filename = path_name[0] + '/' + path_name[1].replace('-index', '', ).replace('txt', 'xml')
    process_wiki(idx_filename,dat_filename)
    tracemalloc.stop()


