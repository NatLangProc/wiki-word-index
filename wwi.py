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


safe_spacy_load()