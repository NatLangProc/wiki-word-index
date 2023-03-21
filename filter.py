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
    output_text = re.sub('(<!--(.)*-->)|(\[\[.*:.*\]\])|(<.*>.*</.*>)', '', output_text)
    pattern = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    output_text = re.sub(pattern, '', output_text)
    return output_text
