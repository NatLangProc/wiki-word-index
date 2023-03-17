import re

OPENING_CHAR = '{'
CLOSING_CHAR = '}'

def strip_templates(input_text):
    output_text = ''
    level = 0
    for ch in input_text:
        if ch == OPENING_CHAR:
            level += 1

        if level == 0:
            output_text += ch

        if ch == CLOSING_CHAR:
            level -= 1

        if level < 0:
            level = 0

    return output_text

def strip_wiki(input_text):
    output_text = strip_templates(input_text)
    output_text = re.sub('(<!--(.)*-->)|(\[\[.*:.*\]\])|(<ref.*>.*</ref>)', '', output_text)
    pattern = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    output_text = re.sub(pattern, '', output_text)
    return output_text
