import nltk
import pprint
import argparse

import filestuff
import spimi
import compress
# import merge
# import query

###################################### NO COMPRESSION ##############################################
print("#### NO COMPRESSION #####")
# get all reuters docs and accumulate all term, docID pairs

doc_ctr = 1
tokens_list = []
doc_path = './docs'
docs = filestuff.get_reuters(doc_path)

index_file = './blocks/index.txt'

# do for each file in the collection
for title,doc in docs.iteritems():
    terms = nltk.word_tokenize (doc)                      # tokenize SGM doc to a list
    # COMPRESSION techniques
    terms = compress.remove_weird_things(terms)           #1 remove puntuations, escape characters, etc
    terms = compress.remove_numbers(terms)              #2 remove numbers
    # terms = compress.case_folding(terms)                #3 convert all to lowercase
    # terms = compress.remove_stop_words(terms, 30)       #4 remove 30 most common words
    # terms = compress.remove_stop_words(terms, 150)      #5 remove 150 most common words 

    # collect all term,docID pairs to a list
    for term in terms:
        token_obj = {"term":term,"docID":doc_ctr}
        tokens_list.append(token_obj)

    # print("finished doc" + str(doc_ctr))
    doc_ctr += 1    # next doc


pprint.pprint(tokens_list)


########## SPIMI ####################
spimi_files = spimi.SPIMI(tokens_list, 30000)
print(spimi_files)

########## MERGING ##################
index_file = spimi.block_merge(spimi_files, index_file)
#print(index_file)

index = filestuff.read_index_into_memory(index_file)
print("Term count: " + str(len(index)))