import filestuff


######## testing ##############

index, postings = filestuff.read_index_into_memory("index_no_compression_1.txt")
print("Term count: " + str(len(index)))
print("Postings: ") + str(postings)

index, postings = filestuff.read_index_into_memory("index_no_numbers_2.txt")
print("Term count: " + str(len(index)))
print("Postings: ") + str(postings)

index, postings = filestuff.read_index_into_memory("index_case_fold_3.txt")
print("Term count: " + str(len(index)))
print("Postings: ") + str(postings)

index, postings = filestuff.read_index_into_memory("index_remove_30_stop_4.txt")
print("Term count: " + str(len(index)))
print("Postings: ") + str(postings)

index, postings = filestuff.read_index_into_memory("index_remove_150_stop_5.txt")
print("Term count: " + str(len(index)))
print("Postings: ") + str(postings)