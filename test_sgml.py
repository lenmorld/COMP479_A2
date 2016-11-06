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

import query
import ranking

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

# doc length dictionary
doc_length_dict = {}


# # pprint.pprint(docs)
# print(type(docs))

# for d in docs:
# 	print(d)
# 	print("--------")
doc_ctr = 0
doc_len_ave = 0


# do for each file in the collection
for docID, doc in docs.iteritems():
	# print (doc)

	try:	
		int(docID)
		doc_ctr += 1
		print("NewId: " + docID)
		print("Doc: " + doc)
		print("next doc===============================")
	except:
		print("no body")
		continue

	terms = nltk.word_tokenize (doc)                      # tokenize SGM doc to a list
	# print(terms)
	# print("Length")
	# print(len(terms))
	# raw_input()

	# # COMPRESSION techniques
	terms = compress.remove_weird_things(terms)           #1 remove puntuations, escape characters, etc
	terms = compress.remove_numbers(terms)              #2 remove numbers
	terms = compress.case_folding(terms)                #3 convert all to lowercase

	doc_length = len(terms)
	doc_length_dict[docID] =  doc_length 				# save doc length in a dict

	# print(terms)
	# print("Length")
	# print(len(terms))

	# raw_input()

	# collect all term,docID pairs to a list
	for term in terms:
	    token_obj = {"term":term,"docID": docID}
	    tokens_list.append(token_obj)


print("N: " + str(doc_ctr))

temp_doc_len_sum = 0
for d in doc_length_dict:
	print(d, ":", doc_length_dict[d])
	temp_doc_len_sum += doc_length_dict[d]

doc_len_ave = temp_doc_len_sum /  doc_ctr


# Ld -> doc_length_dict
# Lave -> doc_len_ave


# at this point, we have the token stream #

######### TODO: Eliminate stop words from Doc before and after indexing #################
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

for k,v in index.iteritems():
	print(k, len(v))				# term with its doc. frequency

######## testing ##############


# after collecting all terms, now we can get the 30 & 150 most frequent words (stop words)


############# QUERY ######################
# parser = argparse.ArgumentParser(description='query', add_help=False)
# parser.add_argument("-q","--query")
# args = parser.parse_args()

# init index to use for querying
# final_index = query.QueryObject('./blocks/index.txt')

final_index, final_postings_count = filestuff.read_index_into_memory('./blocks/index.txt')

print("INDEX")
pprint.pprint(final_index)

# if query passed as argument, run query
# otherwise, loop to allow user to run queries

# if args.query:
#     query = args.query
#     prepare_query()

# else:

# while True:

print("Enter query separated by AND(or spaces) | OR:")
q_string = raw_input(">")
try:
    # query.prepare_query(q)
    doc_results = query.get_query_results(q_string)
    print(doc_results)
    print(type(doc_results))
except:
    print("No input detected")


################ RANKING ####################

# Ld -> doc_length_dict {'10001':2,'10002':3}
# Lave -> doc_len_ave

"""
k: positive tuning parameter that calibrates tftd (document term frequency)
	k = 0 ;binary model- no term frequency
	large k value corresponds to using raw term frequency

b: scaling by document length
	0 <= b <= 1
	b= 1 ; fully scaling the term weight by doc length
	b = 0; no length normalization
"""

k = 1
b = 0.5

ranking.get_rsvd(q_string, doc_results, doc_ctr, doc_length_dict, doc_len_ave, k, b, final_index)
