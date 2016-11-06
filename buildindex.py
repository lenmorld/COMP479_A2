import nltk
# import pprint
import argparse

import filestuff
import spimi
import compress
# import merge
# import query

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
    # terms = compress.remove_numbers(terms)              #2 remove numbers
    # terms = compress.case_folding(terms)                #3 convert all to lowercase

    # collect all term,docID pairs to a list
    for term in terms:
        token_obj = {"term":term,"docID":doc_ctr}
        tokens_list.append(token_obj)

    doc_ctr += 1    # next doc

# tokens_list = compress.remove_stop_words(tokens_list, 30)       # 4 remove 30 most common words
# tokens_list = compress.remove_stop_words(tokens_list, 150)      # 5 remove 30 most common words

########## SPIMI ####################
spimi_files = spimi.SPIMI(tokens_list, block_size)
print(spimi_files)

########## MERGING ##################
index_file = spimi.block_merge(spimi_files, index_file)
#print(index_file)

index, postings_count = filestuff.read_index_into_memory(index_file)
print("Term count: " + str(len(index)))



######## testing ##############


