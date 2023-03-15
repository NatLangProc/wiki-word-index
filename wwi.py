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


(user,password) = read_credentials()
print(user,password)