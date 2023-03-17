#!/usr/bin/env python3

import xml.etree.ElementTree as Et
import csv
import os
from bz2 import BZ2Decompressor
import time
from mysql.connector import connect
from getpass import getpass
import configparser
import spacy as spacy
import filter

config = configparser.ConfigParser()
config.read('wwi.ini')
wikiLang = config['locale']['lang']
jobRenewStruct = int(config['jobs']['renew_struct'])
jobRenewData = int(config['jobs']['renew_data'])
data_from = int(config['data']['from'])
data_to = int(config['data']['to'])

# Two dictionaries between one byte id of PoS (part of speech)
# and abbreviate name of PoS
# in table pos
dict_id2pos = dict()
dict_pos2id = dict()


if wikiLang == "en":
    spacy_name = wikiLang + '_core_web_md'
else:
    spacy_name = wikiLang + '_core_news_md'


def spacy_load():
    nlp_ = spacy.load(spacy_name, disable='ner')
    return nlp_


def safe_spacy_load():
    try:
        nlp_ = spacy_load()
    except IOError:
        spacy.cli.download(spacy_name)
        nlp_ = spacy_load()
    return nlp_


nlp = safe_spacy_load()


def read_credentials():
    if 'user' in config['credentials']:
        user = config['credentials']['user']
    else:
        user = None
    if 'password' in config['credentials']:
        password = config['credentials']['password']
    else:
        password = None
    if not user:
        user = input("Enter username (or put it to wwi.ini): "),
    if not password:
        password = getpass("Enter password (or put it in plain text to wwi.ini): "),
    return user, password


def connect_wiki():
    credentials = read_credentials()
    return connect(
        host="localhost",
        user=credentials[0],
        password=credentials[1],
        database="wiki_" + wikiLang,
    )


def get_sql_from_file(path):
    file = open(path, 'r')
    lines = file.readlines()
    file.close()
    for i in range(0, len(lines)):
        lines[i] = lines[i].strip()
    sql_list = list()
    sql = ""
    for i in range(0, len(lines)):
        sql += " " + lines[i]
        if lines[i].endswith(';'):
            sql_list.append(sql)
            sql = ""
    if len(sql) > 0:
        sql_list.append(sql)
    return sql_list


def drop_and_create_tables(connection):
    directory = 'sql/tables'
    dirlist = os.listdir(directory)
    # Tables have constraints so drop and create must be in specified order
    dirlist.sort(reverse=True)
    for filename in dirlist:
        if not filename.endswith('.sql'):
            continue
        stmt = get_sql_from_file(directory + '/' + filename)[0]
        with connection.cursor() as cursor:
            cursor.execute(stmt)

    dirlist.sort()
    for filename in dirlist:
        if not filename.endswith('.sql'):
            continue
        stmt = get_sql_from_file(directory + '/' + filename)[1]
        with connection.cursor() as cursor:
            cursor.execute(stmt)


def init_pos_table(connection):
    rows = []
    with open("pos_table.csv", newline="") as f:
        reader = csv.reader(f, delimiter=";", quoting=csv.QUOTE_NONE)
        for row in reader:
            rows.append(row)

    with connection.cursor() as cursor:
        stmt = "insert into pos (id,spacy,description) VALUES (%s, %s, %s)"
        cursor.executemany(stmt, rows)
        connection.commit()


def read_index(wiki_filename, index_filename):
    index = []
    file = open(index_filename, 'r')
    line = file.readline().rstrip()
    start = int(line.split(':')[0])
    end = start
    counter = 0
    while True:
        line = file.readline().rstrip()
        if not line:
            break
        offset = int(line.split(':')[0])
        if offset > end:
            start = end
            end = offset
            index.append((counter, start, end))
            if counter % 2000 == 0:
                print('.', end="")
            counter += 1
            # if counter > limit:
            #      break
    file.close()
    start = end
    end = os.stat(wiki_filename).st_size
    index.append((counter, start, end))
    return index


def init_blocks_table(connection):
    with connection.cursor() as cursor:
        cursor.execute("truncate table blocks")
        wiki_filename = 'wikidumps/' + wikiLang + 'wiki-latest-pages-articles-multistream.xml.bz2'
        index_filename = 'wikidumps/' + wikiLang + 'wiki-latest-pages-articles-multistream-index.txt'
        data = read_index(wiki_filename, index_filename)
        stmt = "INSERT INTO blocks (number,start,end) VALUES (%s, %s, %s)"
        cursor.executemany(stmt, data)
        connection.commit()


def init_tables(connection):
    init_pos_table(connection)
    init_blocks_table(connection)

def reset(connection):
    with connection.cursor() as cursor:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("truncate table pages")
        cursor.execute("truncate table words")
        cursor.execute("truncate table bwords")
        cursor.execute("truncate table words_pages")
        cursor.execute("truncate table bwords_pages")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        cursor.execute("update blocks set processed=0,proctime=NULL,sqltime=0,words=NULL"+
                       ",sum=NULL,newwords=NULL,maxlen=NULL")
        connection.commit()

def fill_pos_dictionaries(connection):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id,spacy FROM pos")
        rows = cursor.fetchall()
        for row in rows:
            dict_id2pos[row[0]] = row[1]
            dict_pos2id[row[1]] = row[0]


def fetch_block_info(connection, number):
    cursor = connection.cursor()
    cursor.execute("SELECT start,end,processed FROM blocks where number=" + str(number))
    return cursor.fetchone()


def process(text):
    page_freq = dict()
    doc = nlp(filter.strip_wiki(text))
    for token in doc:
        if token.pos_ in 'SPACE':
            continue
        if len(token.lemma_) > 100:
            lemma = 'Long'+str(len(token.lemma_))+' '+token.lemma_[:20]
            pos = 'LONG'
        else:
            lemma = token.lemma_
            pos = token.pos_
        idpos = dict_pos2id[pos]
        if (token.lemma, idpos) in page_freq:
            page_freq[(token.lemma, idpos)][1] += 1
        else:
            page_freq[(token.lemma, idpos)] = [lemma, 1]
    return page_freq


def add_to_block(block_freq, page_freq):
    for el in page_freq:
        if el in block_freq:
            block_freq[el][1] += page_freq[el][1]
        else:
            block_freq[el] = page_freq[el]


def read_block(file, start, end):
    decompressor = BZ2Decompressor()
    file.seek(start)
    data = file.read(end - start)
    data1 = decompressor.decompress(data)
    xml_object = Et.fromstringlist(["<root>", data1, "</root>"])
    pages = xml_object.findall('page')
    block_freq = dict()
    for k in pages:
        if k.find('title').text.find(':') >= 0:
            continue
        # print("====",l[k].find('title').text)
        page = k.find('revision').find('text').text
        print('.', end="")
        page_freq = process(page)
        add_to_block(block_freq, page_freq)
    print("words in block", len(block_freq))
    return block_freq


def update_main_with_block(connection):
    with connection.cursor() as cursor:
        stmt = """UPDATE words
            INNER JOIN bwords
            ON words.hword = bwords.hword and
            words.idpos = bwords.idpos
            SET words.count = words.count+bwords.count"""
        cursor.execute(stmt)
        stmt = """INSERT INTO words ( hword, idpos, word, count, len)
                SELECT hword, idpos, word, count, len
                FROM bwords b
                WHERE
                NOT EXISTS (SELECT * FROM words w
                WHERE b.hword = w.hword and b.idpos = w.idpos)"""
        cursor.execute(stmt)


def getlen(el, val):
    if dict_id2pos[el[1]] == 'LONG':
        return int(val[0][4:val[0].find(' ')])
    else:
        return len(val[0])


def freq_to_array(freq):
    result = []
    for el in freq:
        result.append((el[0], el[1], freq[el][0], freq[el][1], getlen(el, freq[el])))
    return result


def freq_to_db(connection, freq, number, spacy_time):
    with connection.cursor() as cursor:
        st = time.time()
        cursor.execute("SELECT count(*) from words")
        words_before = int(cursor.fetchone()[0])
        arr = freq_to_array(freq)
        maxl = 0
        for el in arr:
            word_len = el[4]
            if word_len > maxl:
                maxl = word_len
                slowo = el[2]
        print("longest word has", maxl, slowo)
        stmt = "INSERT INTO bwords (hword,idpos,word,count,len) VALUES (%s, %s, %s, %s, %s)"
        cursor.executemany(stmt, arr)
        update_main_with_block(connection)
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("truncate table bwords_pages")
        cursor.execute("truncate table bwords")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        cursor.execute("update blocks set processed=1,proctime="+str(spacy_time)
                       + ",words="+str(len(arr))+",maxlen="+str(maxl)
                       + " where number="+str(number))
        connection.commit()
        et = time.time()
        sql_time = et - st
        cursor.execute("SELECT count(*) from words")
        words_after = int(cursor.fetchone()[0])
        cursor.execute("update blocks set sqltime="+str(sql_time)
                       + ",sum="+str(words_after)
                       + ",newwords=" + str(words_after-words_before)
                       + " where number="+str(number))
        print('sql time:', sql_time, 'seconds')
        connection.commit()


def process_wiki(connection):
    fill_pos_dictionaries(connection)
    wiki_filename = 'wikidumps/' + wikiLang + 'wiki-latest-pages-articles-multistream.xml.bz2'
    binfile = open(wiki_filename, 'rb')
    for number in range(data_from, data_to):
        print("===", number)
        row = fetch_block_info(connection, number)
        if row[2] == 0:
            st = time.time()
            freq = read_block(binfile, row[0], row[1])
            et = time.time()
            elapsed_time = et - st
            print('spacy time:', elapsed_time, 'seconds')
            freq_to_db(connection, freq, number, elapsed_time)

conn = connect_wiki()
if jobRenewStruct:
    drop_and_create_tables(conn)
    init_tables(conn)
elif jobRenewData:
    reset(conn)
process_wiki(conn)
conn.close()
