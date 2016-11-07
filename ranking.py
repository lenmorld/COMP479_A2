"""
ranking
"""



import math


"""
calculates RSV for each document, aggregate in a RSV dictionary

inputs:
q - query string
docs - docs which are the result of the query
N - number of docs in the colletion
doc_length_dict - doc. lengths in a dictionary data structure
Lave - average length of all documents
k - positive tuning parameter that calibrates tftd scaling
b - tuning parameter for document length

"""

def get_rsvd(q, docs, N, doc_length_dict, Lave, k, b, index):
	RSVd = {}

	print(q)
	print(docs)
	terms = q.split()
	print(terms)
	raw_input()

	# this simply discards v in each k:v  [{'21004': 1}, {'21005': 1}] -> ['21004','21005']
	try:
		docs_list = list({key for d in docs for key in d.keys()})
	except:
		docs_list = docs

	for d in docs_list:

		Ld = doc_length_dict[d]
		
		# calculate RSV for this document

		tf_idf_sum = 0			# init. tf_idf sum to 0
		for t in terms:
			postings = index[t]
			dft = len(postings)

			tftd = 0

			# get tftd 
			for posting in postings:
				for k1,v in posting.iteritems():
					# print "postings:"
					# print k, ':', v
					# print "docID", d
					if k1 == d:
						tftd = v
			print d, ':' , t, " DFT: " + str(dft), " TFTD: " + str(tftd)

			idf = ( math.log10 ( N/dft ) )
			tftd_norm = ((k+1) + tftd ) / ( (k * ((1-b) + (b * (Ld/Lave)))  ) + tftd)
			tf_idf =  idf / tftd_norm
			tf_idf_sum += tf_idf

		RSVd[d] = tf_idf_sum

	# for d in RSVd:
	# 	print d, "_", RSVd[d]

	return RSVd