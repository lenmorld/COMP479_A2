import math

def get_rsvd(q, docs, N, doc_length_dict, Lave, k, b, index):
	RSVd = {}

	# RSVd['10001'] = 0.9
	# RSVd['10002'] = 0.8 

	

	terms = q.split()

	# this simply discards v in each k:v  [{'21004': 1}, {'21005': 1}] -> ['21004','21005']
	docs_list = list({key for d in docs for key in d.keys()})

	for d in docs_list:

		Ld = doc_length_dict[d]

		# RSVd[d] = 0			
		
		# calculate RSV for this document

		tf_idf_sum = 0			# init. tf_idf sum to 0
		for t in terms:
			print(t)
			postings = index[t]
			dft = len(postings)

			tftd = 0
			for posting in postings:
				for k1,v in posting.iteritems():
					# print "postings:"
					# print k, ':', v
					# print "docID", d

					if k1 == d:
						tftd = v

			print d, ':' , t			
			print "DFT: " + str(dft)
			print "TFTD: " + str(tftd)

			# dft = int(dft)
			# tftd = int(tftd)


			print type(k), type(b), type(Ld), type(Lave), type(tftd), type(dft), type(N)


			idf = ( math.log10 ( N/dft ) )
			tftd_norm = ((k+1) + tftd ) / ( (k * ((1-b) + (b * (Ld/Lave)))  ) + tftd)

			tf_idf =  idf / tftd_norm

			tf_idf_sum += tf_idf

		RSVd[d] = tf_idf_sum


	for d in RSVd:
		print d, "_", RSVd[d]