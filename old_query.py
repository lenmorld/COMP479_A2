"""
query

parameters:
[-k k]      [k value for BM25 algorithm]
[-b b]      [value for BM25 algorithm]
[-q query] 

if no k,b passed, defaults will be used

o   Allows user to run one query by passing a query as a parameter, 
or running the script without parameters which loops to accept and process queries

o   Involves creating a QueryObject that holds the index loaded from memory. 
This improves performance if program is ran interactively (loop), because the index is loaded once to memory, 
and can be used to process queries until user stops program

"""

import argparse
import cPickle as pickle
import pprint

import filestuff
import ranking


class QueryObject:

    def __init__(self, index_file):
        self.index, self.postings_count  = filestuff.read_index_into_memory(index_file)

    """
    query_list

    prccess OR, AND queries, handling OR in a special way
    """
    @staticmethod
    def query_list(index, term_list, op):
        if len(term_list) >1:
            # get postings of first term

            # [{'21004': 1}, {'21005': 1}]

            try:    
                temp_postings_LoD = index[term_list[0]]       # initialize with first term's docs
                # this simply discards v in each k:v  [{'21004': 1}, {'21005': 1}] -> ['21004','21005']
                temp_postings = list({k for d in temp_postings_LoD for k in d.keys()})
                # print(temp_postings)
            except KeyError:
                temp_postings = list()

            and_postings = temp_postings                 
            and_postings_multiple = [temp_postings, ]     # accumulate intersection of documents per level ,e.g 1 doc, 2 docs 'and-ed', 3 docs 'and-ed', ...
            or_postings = temp_postings                  
            or_postings_multiple = [temp_postings, ]      # accumulate union of documents per level ,e.g 1 doc, 2 docs 'and-ed', 3 docs 'and-ed', ...


            #### doing OR with priority on the Intersections ###
            # to process OR, we need to order documents by how many keywords they contain
            # e.g. for a 3 word query, the first in the list should be the ones that contain all 3 keywords (i.e. the intersection of all 3)
            #       then the intersection of just 2 docs, and lastly the other docs that has either of the 3 but no intersection
            # to do that, we have to know the intersection and union at each level, in which level means incresing number of documents we are intersecting

            print(term_list)

            for t in term_list:

                try:
                    temp_term_LoD = index[t]    # [{'21004': 1}, {'21005': 1}]
                    # this simply discards v in each k:v  [{'21004': 1}, {'21005': 1}] -> ['21004','21005']
                    temp_term = list({k for d in temp_term_LoD for k in d.keys()})

                except KeyError:
                    temp_term = list()

                # before: print list(set(and_postings) & set(temp_term))

                and_postings = list(set(and_postings) & set(temp_term))
                and_postings_multiple.insert(0, and_postings)           # add the intersection of this much documents to the head of the list
                                                                        # at the end of the loop, we will have the intersection of all (or most) docs at the start of the list
                or_postings = list(set(or_postings) | set(temp_term))
                or_postings_multiple.insert(0, or_postings)

            

            if op == 'AND':
                return and_postings
            elif op == 'OR':
                # we want to put first the ones that have their intersection
                list_collector = []
                for and_postings_m in and_postings_multiple:        # go through all intersections, starting with the most 'encompassing' one
                    for item in and_postings_m:                     # for each intersection, get the list items
                        if item not in list_collector:              # instead of simply appending which will cause duplicates (and forced ordering for sets)
                            list_collector.append(item)             # we carefully append to the end of the final list, if item is not there yet

                for or_postings_m in or_postings_multiple:         # go through all unions, starting with the most 'encompassing' one
                    for item in or_postings_m:                     # for each union, get the list items
                        if item not in list_collector:              # instead of simply appending which will cause duplicates (and forced ordering for sets)
                            list_collector.append(item)             # we carefully append to the end of the final list, if item is not there yet
                return list_collector

        else:
            return index[term_list]


    """
    run_query

    process passed query, separate terms in the query and invokes query_list to query index
    """
    def run_query(self, query):
        index = self.index
        q_split = query.split()

        err = ''
        if len(q_split) == 1:   # single word query
            try:
                # query = query.lower()                  # enable this if index is case-folded
                print(query)
                result = index[query]
            except KeyError:
                result = list()
                err = "term not found"
        else:                   # multiple query, separated by AND | OR
            if 'OR' in query:
                # multiple words query - cat OR dog
                q_terms = query.split(' OR ')
                # q_terms = [q.lower() for q in q_terms]                    # enable this if index is case-folded
                result = QueryObject.query_list(index, q_terms, 'OR')
            # elif 'AND' in query:
            else:       # default to AND if seperated by spaces or explicit AND

                if 'AND' in query:
                    q_terms = query.split(' AND ')
                else:
                    q_terms = query.split()
                # q_terms = [q.lower() for q in q_terms]                     # enable this if index is case-folded
                try:
                    result = QueryObject.query_list(index, q_terms, 'AND')
                except KeyError:
                    result = list()
                    err = "one or all of the terms not found"
        return result, err



def get_query_results(q_string, q_object):
    # q1= QueryObject('./blocks/index.txt')
    result, err = q_object.run_query(q_string)
    # print(q + '->')
    if len(result):
        return result
    else:
        print(err)
        return err


# ############# MAIN ######################
# parser = argparse.ArgumentParser(description='query', add_help=False)
# parser.add_argument("-q","--query")
# args = parser.parse_args()

# # init index to use for querying
# q1= QueryObject('./blocks/index.txt')

# # if query passed as argument, run query
# # otherwise, loop to allow user to run queries
# if args.query:
#     query = args.query
#     prepare_query(query)

# else:
#     while True:
#         print("Enter query separated by AND(or spaces) | OR:")
#         query = raw_input(">")
#         try:
#             prepare_query(query)
#         except:
#             print("No input detected")


############# QUERY ######################
parser = argparse.ArgumentParser(description='query', add_help=False)
parser.add_argument("-q","--query")
parser.add_argument("-k", "--k")
parser.add_argument("-b", "--b")
args = parser.parse_args()

# init index to use for querying
# final_index = QueryObject('./blocks/index.txt')
# final_index, final_postings_count = filestuff.read_index_into_memory('./blocks/index.txt')

# load document lengths used for ranking
with open('doc_lengths.p','rb') as fp:
    doc_length_dict = pickle.load(fp)

N = len(doc_length_dict) 

# print("Doc length dict:=======================")
# pprint.pprint(doc_length_dict)
print "N: ", N

# get Lave (document length average)
temp_doc_len_sum = 0
for d in doc_length_dict:
    # print(d, ":", doc_length_dict[d])
    temp_doc_len_sum += doc_length_dict[d]

doc_len_ave = temp_doc_len_sum /  N



# print("INDEX")
# pprint.pprint(final_index)

# if query passed as argument, run query
# otherwise, loop to allow user to run queries

if args.k:
    k = float(args.k)
else:
    k = 0.5

if args.b:
    b = float(args.b)
else:
    b = 0.5

if args.query:
    q1= QueryObject('./blocks/index.txt')
    q_string = args.query
    doc_results = get_query_results(q_string, q1)

    print("results")
    print(doc_results)

    ################ RANKING ####################
    # k = 1
    # b = 0.5
    RSVd = ranking.get_rsvd(q_string, doc_results, N, doc_length_dict, doc_len_ave, k, b, q1.index)

    for d in RSVd:
        print d, "_", RSVd[d]

else:
    q1= QueryObject('./blocks/index.txt')
    while True:
        print("Enter query separated by AND(or spaces) | OR:")
        q_string = raw_input(">")
        try:
            # query.prepare_query(q)
            doc_results = get_query_results(q_string, q1)
            print(doc_results)
            print(str(len(doc_results)) + " found " )
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

        # k = 1
        # b = 0.5
        RSVd = ranking.get_rsvd(q_string, doc_results, N, doc_length_dict, doc_len_ave, k, b, q1.index)

        for d in RSVd:
            print d, "_", RSVd[d]