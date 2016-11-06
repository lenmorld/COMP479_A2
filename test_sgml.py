from os import listdir
from os.path import isfile, join
import sgml_parser
from collections import OrderedDict
import ast

import nltk
# import pprint
import argparse

import filestuff
import spimi
import compress
import pprint

block_size = 1315000 

def get_files(doc_path, file_ext):

    only_files = [f for f in listdir(doc_path) if isfile(join(doc_path, f))]
    file_types = [(doc_path + '/' +  f) for f in only_files if f.endswith(file_ext)]

    # print(reuter_files)
    return file_types

def get_reuters(doc_path):
    reuter_files = get_files(doc_path, '.sgm')
    docs = {}
    for reuter_file in reuter_files:
        new_docs = sgml_parser.extract(open(reuter_file))
        docs = dict(docs.items() + new_docs.items())
    return docs

# get all reuters docs and accumulate all term, docID pairs

doc_ctr = 1
tokens_list = []
doc_path = './docs'
docs = get_reuters(doc_path)
index_file = './blocks/index.txt'


# # pprint.pprint(docs)
# print(type(docs))

# for d in docs:
# 	print(d)
# 	print("--------")
docctr = 0
# do for each file in the collection
for docID, doc in docs.iteritems():
	# print (doc)

	try:	
		int(docID)
		docctr += 1
		print("NewId: " + docID)
		print("Doc: " + doc)
		print("next doc===============================")
	except:
		print("no body")


	#### now we have docID for eahc doc

	terms = nltk.word_tokenize (doc)                      # tokenize SGM doc to a list
	# print(terms)
	# print("Length")
	# print(len(terms))
	# raw_input()

	# # COMPRESSION techniques
	terms = compress.remove_weird_things(terms)           #1 remove puntuations, escape characters, etc
	terms = compress.remove_numbers(terms)              #2 remove numbers
	terms = compress.case_folding(terms)                #3 convert all to lowercase

	# print(terms)
	# print("Length")
	# print(len(terms))

	# raw_input()

	# collect all term,docID pairs to a list
	for term in terms:
	    token_obj = {"term":term,"docID": docID}
	    tokens_list.append(token_obj)


print("N: " + str(docctr))


# pprint.pprint("Length with stop words: ")
# pprint.pprint(tokens_list)
# print(len(tokens_list))
# # # tokens_list = compress.remove_stop_words(tokens_list, 30)       # 4 remove 30 most common words
# # tokens_list = compress.remove_stop_words(tokens_list, 150)      # 5 remove 30 most common words

# pprint.pprint("Length without stop words: ")
# pprint.pprint(tokens_list)
# print(len(tokens_list))


########## SPIMI ####################
spimi_files = spimi.SPIMI(tokens_list, block_size)
print(spimi_files)

########## MERGING ##################
index_file = spimi.block_merge(spimi_files, index_file)
#print(index_file)

index, postings_count = filestuff.read_index_into_memory(index_file)
print("Term count: " + str(len(index)))



######## testing ##############


# after collecting all terms, now we can get the 30 & 150 most frequent words (stop words)
