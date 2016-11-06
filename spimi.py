"""
SPIMI()

input: token_stream - list of tokens - (term, docID) pair
"""

from collections import OrderedDict
import sys
import linecache
# import pprint
import ast

import filestuff


def SPIMI(token_stream, block_size):
    print("block_size: " + str(block_size))
    spimi_files = []
    spimi_file_count = 0
    dictionary = {}
    # pprint.pprint(token_stream)
    token_count = len(token_stream)
    token_ctr = 0

    # print(token_stream)
    for token in token_stream:
        token_ctr += 1
        term = token["term"]
        docID = token["docID"]

        if term in dictionary:
            # if docID not in dictionary[term]:
            # e.g. 'apple'= [{200:1}, {202:3}]
            if any(docID in posting for posting in dictionary[term]):       # if docID is already in postings list
                # dictionary[term].append(docID)

                # dictionary[term][docID] += 1                # add 1 to tf

                for d in dictionary[term]:
                    d.update((doc, tf+1) for doc, tf in d.iteritems() if doc == docID )    # add 1 to tf for the matching docID
            else:
                dictionary[term].append({docID:1})              # else add docID to postings list
        else:
            dictionary[term] = [{docID:1}]      # initialize tf to 0

        # if it becomes too big for the block size, or it is the last document (indicated by the last token)
        if (sys.getsizeof(dictionary) > block_size) or (token_ctr >= token_count) :
            # print(str(sys.getsizeof(dictionary)))
            sorted_dictionary = sort_terms(dictionary)
            spimi_file_count += 1
            spimi_file = write_block_to_disk(sorted_dictionary, spimi_file_count)    # generate block file for tokens_list
            spimi_files.append(spimi_file.name)         # add filename to the file list,   append(spimi_file) would add file objects
            # print("------------ SPIMI-generated dictionary block ------------------")
            dictionary = {}        # clear dictionary and postings list
            # print("------------ wrote to block# " + str(spimi_file_count) + "------------------")

    return spimi_files



def sort_terms(dictionary):
    sorted_terms = sorted(dictionary)
    dictionary_sorted = OrderedDict()
    for item in sorted_terms:
    	dictionary_sorted[item] = dictionary[item]

    return dictionary_sorted

def write_block_to_disk(sorted_terms, file_count):
    out_file = './blocks/block' + str(file_count) + '.txt'
    with open(out_file, "w") as out_file:

        # 'apple'= [{200:1}, {202:3}]
        for item in sorted_terms:
            out_file.write(str(item) + "=" + str(sorted_terms[item]) + "\n")
    return out_file

def block_merge(block_filenames, index_file):

    block_count = len(block_filenames)
    # index_file = './blocks/index.txt'

    block_ctr = 1
    blocks = {}
    line_ctrs ={}

    for f in block_filenames:
        blocks[block_ctr] = f
        line_ctrs[block_ctr] = 1
        block_ctr += 1

    print("Blocks:")
    print(blocks)
    sorted_lines = []
    index = []
    finished_blocks = []

    filestuff.delete_content(index_file)  # clear contents of file before writing in a loop

    while len(finished_blocks) < block_count :
        with open(index_file, 'a+') as index_f:
            lines=[]
            for x in range(1,block_count+1):    # go through all blocks
                if x in finished_blocks:        # if block is finished, skip this
                    continue
                line = {}
                term = linecache.getline(blocks[x], line_ctrs[x])    # get line(posting) where the block pointer currently is
                # print 'term: ', term
                if term == '':                  # EOF, flag this block as finished
                    finished_blocks.append(x)
                else:                           # get line (posting) from this block, and collect them into a list
                    line['term'] = term
                    line['blockID'] = x
                    lines.append(line)
            # pprint.pprint(sorted_lines)
            if (len(lines) > 0):                                # if list of lines collected has at least one item
                min_line = min(lines, key=lambda t:t['term'])   # get minimum based on term
                min_block_id = min_line['blockID']                  # get blockID

                #disect entry into term and postings

                # workers:[{200:1}, {202:3}]
                t_split = min_line['term'].split('=')
                d_term = t_split[0]
                # print(min_line['term'])
                # print(t_split[1])
                
                postings = ast.literal_eval(t_split[1])     #  convert postings string to list e.g. '[{200:1}, {202:3}]\n' -> [{200:1}, {202:3}]   

                # BEFORE: convert postings string to list e.g. '[7,9]\n' -> [7,9]


                for l in lines:
                    if l['blockID'] != min_block_id:
                        other_block_id = l['blockID']
                        t_split_other = l['term'].split('=')
                        d_term_other = t_split_other[0]
                        postings_other = ast.literal_eval(t_split_other[1])         # convert postings string to list e.g. '[7,9]\n' -> [7,9]

                        if d_term == d_term_other:   # similar term: min term and one of the others
                            # postings = postings + postings_other    # merge them -> this would keep duplicates
                            postings = postings + list(set(postings_other) - set(postings))          # this would be an effective set union
                            line_ctrs[other_block_id] += 1          # make this other posting point to next line
                            min_line['term'] = str(d_term) + ":" + str(postings) + "\n"

                postings = sorted(postings)
                final_posting = str(d_term) + "=" + str(postings) + "\n"
                index.append(final_posting)                     # add to final_index
                index_f.write(final_posting)                    # write to file

                # sorted_lines.append(min_line)                   # TESTING - add to in-memory list
                line_ctrs[min_block_id] += 1                    # increment pointer to this block to next line (posting)

            # print 'min: ', min_line
    #pprint.pprint(sorted_lines)    #in-memory
    #pprint.pprint(index)           #FILE

    return index_file