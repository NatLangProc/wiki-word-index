import re

class SimpleLexer:
    def __init__(self, text):
        self.text = text
        self.position = 0
    def get_sym(self):
        if self.position>=len(self.text):
            return -1,None
        c = self.text[self.position]
        self.position += 1
        match c:
            case '{':
                if self.position < len(self.text) and self.text[self.position] == '{':
                    self.position += 1
                    return 2, '{'
                else:
                    return 1, '{'
            case '[':
                if self.position < len(self.text) and self.text[self.position] == '[':
                    self.position += 1
                    return 4, '['
                else:
                    return 3, '['
            case '<':
                return 5, '<'
            case '}':
                if self.position < len(self.text) and self.text[self.position] == '}':
                    self.position += 1
                    return 7, '}'
                else:
                    return 6, '}'
            case ']':
                if self.position < len(self.text) and self.text[self.position] == ']':
                    self.position += 1
                    return 9, ']'
                else:
                    return 8, ']'
            case '>':
                return 10, '>'
            case '|':
                return 11, '|'
            case "'":
                if self.position < len(self.text) and self.text[self.position] == "'":
                    self.position += 1
                    if self.position < len(self.text) and self.text[self.position] == "'":
                        self.position += 1
                        return 13, "'"
                    else:
                        return 12, "'"
                else:
                    return 0, "'"
            case':':
                return 14, ':'
            case _:
                return 0,c

def strip_brackets(input_text):
    lexer = SimpleLexer(input_text)
    stack = list()
    output_text = ''
    square_text = ""
    while(True):
        sym,ch = lexer.get_sym()
        if sym==-1:
            break
        if sym>0 and sym<6:
            stack.append(sym + 5)
        if sym == 4:
            clear_to_end = False
        if sym == 3:
            dont_clear_to_end = False

        if len(stack)==0:
            if sym == 0:
                output_text += ch
        elif stack[-1] == 9:
            if sym==0:
                if not clear_to_end:
                    square_text += ch
            elif sym == 11:
                square_text = ''
            elif sym == 14:
                square_text = ''
                clear_to_end = True

        elif stack[-1] == 8:
            if sym==0:
                square_text += ch
                if ch == ' ':
                    if not dont_clear_to_end:
                        square_text = ''
                        dont_clear_to_end = True

        if sym>=6 and len(stack) > 0 and sym == stack[-1]:
            stack.pop()
            if len(stack) == 0:
                output_text += square_text
            square_text = ''
    return output_text

def remove_lines(input_text):
    lines = input_text.split('\n')
    new_lines = list()
    counter = 0
    for line in lines:
        counter+=1
        line = line.strip()
        if len(line)==0:
            pass
        elif line.startswith("=="):
            pass
        elif line.startswith("*"):
            if line.startswith("***"):
                nl = line[3:].strip()
            elif line.startswith("**"):
                nl = line[2:].strip()
            else:
                nl = line[1:].strip()
            if len(nl) > 0:
                new_lines.append(nl)
        else:
            new_lines.append(line)
    return '\n'.join(new_lines)

def strip_wiki(input_text):
    output_text = strip_brackets(input_text)
    output_text = remove_lines(output_text)
    return output_text
