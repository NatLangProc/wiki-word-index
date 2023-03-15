import os

from mysql.connector import connect, Error
from getpass import getpass
import configparser
import spacy as spacy

wikilang = "en"
if wikilang == "en":
    spacy_name = wikilang + '_core_web_md'
else:
    spacy_name = wikilang + 'en_core_news_md'


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
    config = configparser.ConfigParser()
    config.read('wwi.ini')
    if 'user' in config['credentials']:
        user=config['credentials']['user']
    else:
        user=None
    if 'password' in config['credentials']:
        password=config['credentials']['password']
    else:
        password=None
    if not user:
        user=input("Enter username (or put it to wwi.ini): "),
    if not password:
        password=getpass("Enter password (or put it in plain text to wwi.ini): "),
    return(user,password)


def connectWiki():
    credentials = read_credentials()
    return connect(
        host="localhost",
        user=credentials[0],
        password=credentials[1],
        database="wiki_"+wikilang,
    )

def getSqlFromFile(path):
    file = open(path, 'r')
    lines = file.readlines()
    file.close()
    for i in range(0,len(lines)):
         lines[i]=lines[i].strip()
    sql_list=list()
    sql = ""
    for i in range(0,len(lines)):
        sql += " " + lines[i]
        if lines[i].endswith(';'):
            sql_list.append(sql)
            sql = ""
    if len(sql)>0:
        sql_list.append(sql)
    return sql_list

def create_tables(connection):
    dir = 'sql/tables'
    dirlist = os.listdir(dir)
    # Tables have constraints so drop and create must be in specified order
    dirlist.sort(reverse=True)
    for fname in dirlist:
        if not fname.endswith('.sql'):
            continue
        stmtDrop = getSqlFromFile(dir+'/'+fname)[0]
        with connection.cursor() as cursor:
            cursor.execute(stmtDrop)

    dirlist.sort()
    for fname in dirlist:
        if not fname.endswith('.sql'):
            continue
        stmtCreate = getSqlFromFile(dir + '/' + fname)[1]
        with connection.cursor() as cursor:
            cursor.execute(stmtCreate)


connection = connectWiki()
create_tables(connection)
connection.close()