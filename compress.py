from normalize import *
import collections
# import nltk
# from nltk.corpus import stopwords
# import re
import pprint
# import string

def remove_weird_things(words):         # remove punctuations, line breaks, whitespace, etc
    punctuations = '!"#$%&\'()*+,./:;<=>?@[\\]^_`{|}~'

    processed_words = [ t.translate(None, punctuations) for t in words ]  # remove punctuations
    garbage_words = ['','s','-','--']
    processed_words = [ t for t in processed_words if t not in garbage_words ]
    return processed_words

def remove_numbers(words):
    processed_words = []
    for w in words:
        if not w.isdigit():
            processed_words.append(w)
    return processed_words

def case_folding(words):
    processed_words = []
    for w in words:
        processed_words.append(w.lower())
    return processed_words
    # processed_words = [w.lower() for w in words ]
    # return processed_words

def remove_stop_words(token_list, num):
    # stops = set(stopwords.words("english"))
    words = []
    for t in token_list:
        words.append(t['term'])

    counter = collections.Counter(words)
    most_common_words_tuple = counter.most_common(num)                      # get the num most common words, which also includes count
    stop_words = [word for word, count in most_common_words_tuple]              # we only need the word, not the count
    # print("stop words")
    # raw_input()
    # pprint.pprint(stop_words)
    # raw_input()
    processed_words = []

    for t in token_list:
        w = t['term']
        d = t['docID']
        if w not in stop_words:
            token_obj = {"term":w,"docID":d}
            processed_words.append(token_obj)
    return processed_words

    # processed_words = [w for w in words if w not in stop_words]
    # return processed_words

def p_stemmer(terms):
    stemmer = PorterStemmer()
    stemmed_terms = [stemmer.stem(term) for term in terms]

    return stemmed_terms