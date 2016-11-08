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


    @staticmethod
    def query_rank(index, term_list):
        if len(term_list) >1:
            # get postings of first term
            try:    
                temp_postings_LoD = index[term_list[0]]       # initialize with first term's docs
                # this simply discards v in each k:v  [{'21004': 1}, {'21005': 1}] -> ['21004','21005']
                temp_postings = list({k for d in temp_postings_LoD for k in d.keys()})
                # print(temp_postings)
            except KeyError:
                temp_postings = list()

            or_postings = temp_postings  

            print(term_list)
            for t in term_list:
                try:
                    temp_term_LoD = index[t]    # [{'21004': 1}, {'21005': 1}]
                    # this simply discards v in each k:v  [{'21004': 1}, {'21005': 1}] -> ['21004','21005']
                    temp_term = list({k for d in temp_term_LoD for k in d.keys()})
                except KeyError:
                    temp_term = list()

                or_postings = list(set(or_postings) | set(temp_term))

            return or_postings

        else:
            return index[term_list[0]]

    def run_ranked_query(self, query):
        index = self.index
        q_terms = query.split() 
        err = ''
        try:
            result = QueryObject.query_rank(index, q_terms)       
        except KeyError:
            result = list()
            err = "no documents found"
        return result, err

def get_query_results(q_string, q_object):
    # q1= QueryObject('./blocks/index.txt')
    # result, err = q_object.run_query(q_string)

    result, err = q_object.run_ranked_query(q_string)

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

    # print("results")
    # print(doc_results)

    ################ RANKING ####################
    # k = 1
    # b = 0.5
    RSVd = ranking.get_rsvd(q_string, doc_results, N, doc_length_dict, doc_len_ave, k, b, q1.index, 10)

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
        RSVd = ranking.get_rsvd(q_string, doc_results, N, doc_length_dict, doc_len_ave, k, b, q1.index, 10)

        for d in RSVd:
            print d, "_", RSVd[d]