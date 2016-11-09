import cPickle as pickle

# doc_length_dict = {}

with open('doc_lengths.p','rb') as fp:
    doc_length_dict = pickle.load(fp)


with open('doc_lengths.txt', 'w') as fp:
	for d in doc_length_dict:
		fp.write(str(d) + '\n')