"""
SPIMI()

input: token_stream - list of tokens - (term, docID) pair

includes SPIMI and block_merging
"""

from collections import OrderedDict
import sys
import linecache
# import pprint
import ast
import json

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

        temp_doc_dict = {}

        if term in dictionary:
            # e.g. 'apple' = {'200': 1, '202': 3}
            try:
                dictionary[term][docID] += 1         # increment tftd, this would fail if docID is not in the postings list yet
                # print term, "incremented"
            except:                                  # adds docID to postings list, init tftd to 1
                # print("Key error")
                dictionary[term][docID] = 1
        else:                                       # if term not in dict yet, create postings list, add first docID, init tftd to 1
            dictionary[term] = {}
            dictionary[term][docID] = 1

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

"""
ListOfDictionaries to DictionaryOfDictionaries
"""
def LoD_to_DoD(LoD, term):  
    # do some string manipulation and duck-typing to convert list to dictionary

    temp_json = json.dumps(LoD) 
    temp_json = temp_json.replace("{","")
    temp_json = temp_json.replace("}","")
    temp_json = temp_json.replace("[","{")
    temp_json = temp_json.replace("]","}")
    temp_json = "{'" + term  + "':" + temp_json + '}'

    new_dict = ast.literal_eval(temp_json)

    return new_dict

"""
DictionaryOfDictionaries to ListOfDictionaries
"""
def DoD_to_LoD(DoD):
    # gather all k,v pairs from dictionary, put in a list
    LoD = []
    for k,v in DoD.iteritems():
        LoD.append({k:v})
    return LoD    


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

"""
block_merge


"""
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

                # disect entry into term and postings
                # e.g. moore={'17966': 1, '1854': 1, '18906': 2, '8080': 3}
                t_split = min_line['term'].split('=')
                d_term = t_split[0]
                # print(min_line['term'])
                # print(t_split[1])
                
                # make it a full dictionary
                dict1 = "{1:" + str(t_split[1]) + "}"
                dict1 = ast.literal_eval(dict1)
                # print(dict1[1])

                # collect k,v pairs, add to list
                postings = []
                for k,v in dict1[1].iteritems():
                    postings.append({k:v}) 

                for l in lines:
                    if l['blockID'] != min_block_id:
                        other_block_id = l['blockID']
                        t_split_other = l['term'].split('=')
                        d_term_other = t_split_other[0]

                        # if d_term == 'supercomputers' :
                        #     print l

                        # postings_other = ast.literal_eval(t_split_other[1])         # convert postings string to list e.g. '[7,9]\n' -> [7,9]
                        # {'21002': 3, '21004': 2, '21005': 2, '21006': 2}
                        dict1 = "{1:" +  str(t_split_other[1]) + "}"
                        dict1 = ast.literal_eval(dict1)
                        # postings_other = dict1[1]      #  convert postings string to list e.g. '[{200:1}, {202:3}]\n' -> [{200:1}, {202:3}]   
                        postings_other = []
                        for k,v in dict1[1].iteritems():
                            postings_other.append({k:v})


                        # if d_term == 'supercomputers' :
                        #     print postings_other


                        if d_term == d_term_other:   # similar term: min term and one of the others

                            # convert postings, postings_other to dict so easier to handle
                            postings_dict_d = LoD_to_DoD(postings, d_term)
                            postings_other_d = LoD_to_DoD(postings_other, d_term)

                            # if d_term == 'supercomputers' :
                            #     print "postings_d"
                            #     print postings_dict_d
                            #     print "postings_others_d"
                            #     print postings_other_d

                            union_d = {}

                            for k,v in postings_dict_d[d_term].iteritems():
                                if k in union_d:   # if already there, add
                                    union_d[k] += v
                                else:
                                    union_d[k] = v

                            for k,v in postings_other_d[d_term].iteritems():
                                if k in union_d:   # if already there, add
                                    union_d[k] += v
                                else:
                                    union_d[k] = v

                            union = DoD_to_LoD(union_d)


                            # if d_term == 'supercomputers' :
                            #     print "union"
                            #     print union
                            #     print "union_d"
                            #     print union_d
                                
                            # union = postings + list(set(postings_other) - set(postings))          # this would be an effective set union
                            line_ctrs[other_block_id] += 1          # make this other posting point to next line
                            min_line['term'] = str(d_term) + "=" + str(union) + "\n"

                            postings = union

                postings = sorted(postings)
                final_posting = str(d_term) + "=" + str(postings) + "\n"
                index.append(final_posting)                     # add to final_index
                index_f.write(final_posting)                    # write to file

                line_ctrs[min_block_id] += 1                    # increment pointer to this block to next line (posting)

    return index_file