"""
buildindex.py

o   Builds index using SPIMI and compression methods, and block size as a parameter
o   After getting documents from the collection, this module iterates through all documents and collects all (term, docID) pairs
o   Multiple indexes can be generated with different levels of compression
"""

import nltk
import pprint
import argparse
import cPickle as pickle

import filestuff
import spimi
import compress
# import merge
# import query
import ranking

####### Memory management ########
memory_size = 1000000000
default_block_size = 1315000    # whole corpus 26.3 MB/10 blocks = 2.63 MB

# good values 2630000-> ~ 5 blocks
#             1315000-> ~9 blocks
#              657500-> ~ 20 blocks
              
# parse arguments from command-line
parser = argparse.ArgumentParser(description='build index', add_help=False)
parser.add_argument("block_size")
args = parser.parse_args()

if args.block_size:
    block_size = int(args.block_size)
else:
    block_size = default_block_size

print ("Using block size " + str(block_size))


# get all reuters docs and accumulate all term, docID pairs

tokens_list = []
doc_path = './docs'
docs, sgm_docID_map = filestuff.get_reuters(doc_path)
index_file = './blocks/index.txt'

doc_ctr = 0
doc_len_ave = 0
doc_length_dict = {}

# pprint.pprint(sgm_docID_map)

# do for each file in the collection
for docID,doc in docs.iteritems():

    try:    
        int(docID)
        doc_ctr += 1
        # print("NewId: " + docID)
        # print("Doc: " + doc)
        # print("next doc===============================")
    except:
        # print("no body")
        continue

    terms = nltk.word_tokenize (doc)                      # tokenize SGM doc to a list
    # print(terms)
    # print("Length")
    # print(len(terms))
    # raw_input()

    # COMPRESSION techniques
    terms = compress.remove_weird_things(terms)           #1 remove puntuations, escape characters, etc
    terms = compress.remove_numbers(terms)              #2 remove numbers
    terms = compress.case_folding(terms)                #3 convert all to lowercase

    doc_length = len(terms)
    doc_length_dict[docID] =  doc_length                # save doc length in a dict

    # print(terms)
    # print("Length")
    # print(len(terms))
    # raw_input()

    # collect all term,docID pairs to a list
    for term in terms:
        token_obj = {"term":term,"docID":docID}
        tokens_list.append(token_obj)


print("N: " + str(doc_ctr))

temp_doc_len_sum = 0
for d in doc_length_dict:
    # print(d, ":", doc_length_dict[d])
    temp_doc_len_sum += doc_length_dict[d]

doc_len_ave = temp_doc_len_sum /  doc_ctr


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


# save some necessary info for querying
# to save space and computing, only write doc_length_dict to a file
# from which we can derive N and doc_len_ave
# use Pickle for speed

with open('doc_lengths.p','wb') as fp:
    pickle.dump(doc_length_dict, fp)
