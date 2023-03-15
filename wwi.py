import csv
import os
from mysql.connector import connect
from getpass import getpass
import configparser
import spacy as spacy

config = configparser.ConfigParser()
config.read('wwi.ini')
wikiLang = config['locale']['lang']

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


def drop_and_create_tables(conn):
    directory = 'sql/tables'
    dirlist = os.listdir(directory)
    # Tables have constraints so drop and create must be in specified order
    dirlist.sort(reverse=True)
    for filename in dirlist:
        if not filename.endswith('.sql'):
            continue
        stmt = get_sql_from_file(directory + '/' + filename)[0]
        with conn.cursor() as cursor:
            cursor.execute(stmt)

    dirlist.sort()
    for filename in dirlist:
        if not filename.endswith('.sql'):
            continue
        stmt = get_sql_from_file(directory + '/' + filename)[1]
        with conn.cursor() as cursor:
            cursor.execute(stmt)


def init_pos_table(connection):
    rows = []
    with open("postable.csv", newline="") as f:
        reader = csv.reader(f, delimiter=";", quoting=csv.QUOTE_NONE)
        for row in reader:
            rows.append(row)

    with connection.cursor() as cursor:
        stmt = "insert into pos (id,spacy,description) VALUES (%s, %s, %s)"
        cursor.executemany(stmt, rows)
        connection.commit()

def init_tables(connection):
    init_pos_table(connection)

connection = connect_wiki()
drop_and_create_tables(connection)
init_tables(connection)
connection.close()
