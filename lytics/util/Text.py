# Text.py
# author = Jonathan Huang
from nltk.tokenize import word_tokenize, wordpunct_tokenize

class Text (object):    

    text = ''

    def __init__(self, string):
        self.text = string

    def __str__(self):
        return self.text

    def __repr__(self):
        return self.text

    def __len__(self):
        return len(text)
    
    def tokenize(self):
        self.tokens = [t.lower().encode('ascii', 'ignore') \
                        for t in wordpunct_tokenize(self.text) if t.isalpha()]

    def getTokens(self):
        try:
            self.tokens
        except AttributeError:
            self.tokenize()
        return self.tokens

    def getNumTokens(self):
        try:
            self.tokens
        except AttributeError:
            self.tokenize()
        return len(self.tokens)


