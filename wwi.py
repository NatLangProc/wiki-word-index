import csv
import os
from mysql.connector import connect
from getpass import getpass
import configparser
import spacy as spacy

config = configparser.ConfigParser()
config.read('wwi.ini')
wikiLang = config['locale']['lang']
jobRenew = int(config['jobs']['renew'])

if wikiLang == "en":
    spacy_name = wikiLang + '_core_web_md'
else:
    spacy_name = wikiLang + 'en_core_news_md'


def spacy_load():
    nlp = spacy.load(spacy_name, disable='ner')


def safe_spacy_load():
    try:
        spacy_load()
    except IOError:
        spacy.cli.download(spacy_name)
        spacy_load()

# safe_spacy_load()


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


conn = connect_wiki()
if jobRenew:
    drop_and_create_tables(conn)
    init_tables(conn)
conn.close()
