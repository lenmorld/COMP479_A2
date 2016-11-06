import argparse
import filestuff
import pprint

class QueryObject:

    def __init__(self, index_file):
        self.index, self.postings_count  = filestuff.read_index_into_memory(index_file)

    @staticmethod
    def query_list(index, term_list, op):
        if len(term_list) >1:
            # get postings of first term

            # [{'21004': 1}, {'21005': 1}]

            try:    
                temp_postings_LoD = index[term_list[0]]       # initialize with first term's docs

                # because of changes in data structure
                # before ['21005','21004']
                # now
                # cat and dog
                # cat=[{'21004': 1}, {'21005': 1}]
                # dog=[{'21005': 1}, {'21006': 1}]

                # this simply discards v in each k:v  [{'21004': 1}, {'21005': 1}] -> ['21004','21005']
                temp_postings = list({k for d in temp_postings_LoD for k in d.keys()})

            except KeyError:
                temp_postings = list()

            print("FUCK")
            print(temp_postings)

            and_postings = temp_postings                 
            and_postings_multiple = [temp_postings, ]     # accumulate intersection of documents per level ,e.g 1 doc, 2 docs 'and-ed', 3 docs 'and-ed', ...
            or_postings = temp_postings                  
            or_postings_multiple = [temp_postings, ]      # accumulate union of documents per level ,e.g 1 doc, 2 docs 'and-ed', 3 docs 'and-ed', ...

            #### doing OR with priority on the Intersections ###
            # to process OR, we need to order documents by how many keywords they contain
            # e.g. for a 3 word query, the first in the list should be the ones that contain all 3 keywords (i.e. the intersection of all 3)
            #       then the intersection of just 2 docs, and lastly the other docs that has either of the 3 but no intersection
            # to do that, we have to know the intersection and union at each level, in which level means incresing number of documents we are intersecting

            for t in term_list:

                try:
                    temp_term_LoD = index[t]    # [{'21004': 1}, {'21005': 1}]
                    # this simply discards v in each k:v  [{'21004': 1}, {'21005': 1}] -> ['21004','21005']
                    temp_term = list({k for d in temp_term_LoD for k in d.keys()})

                except KeyError:
                    temp_term = list()

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


def prepare_query(q):
    result, err = q1.run_query(q)
    print(q + '->')
    if len(result):
        print(result)
        print(str(len(result)) + " found " )
    else:
        print(err)


def get_query_results(q):
    print(q)
    q1= QueryObject('./blocks/index.txt')
    result, err = q1.run_query(q)
    # print(q + '->')
    if len(result):
        # print(result)
        # print(str(len(result)) + " found " )
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