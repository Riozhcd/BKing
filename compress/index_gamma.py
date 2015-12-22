# -*- encoding=utf8 -*-
# inverted index gamma code, including postinglist handle and 
# inverted_index gamma compressing into a file.
__author__= 'wenlong cao'
import pickle
import struct
from gamma import gamma_list, degamma, gamma
from dict_singlestring import SingleStringDict
from indexing.inverted_index \
import PostingList, PostingListInitError, DocItem, InvertedIndex
'''
:param inverted_index: the InvertedIndex._index
:param filename : the dump file
:return 
'''
def compress_inverted_index(inverted_index, filename):
	def write_posting_gamma(postinglist):
		'''
		Writing the postinglist into f.
		:param postinglist A value type is indexing.PostingList
		:param f  A opened file
		'''
		resultpl = pregamma_handle_didlist(postinglist)
		gammadata = gamma_list(resultpl)
		length = len(gammadata)
		f.write(struct.pack('I', length))
		for i in range(0, len(gammadata), 8):
			if i + 8 < len(gammadata):
				f.write(struct.pack('B', int(gammadata[i:i + 8], 2)))
			else:
	            # padding
				f.write(struct.pack('B', int(gammadata[i:], 2)))
	# TODO: write inverted index into file

	with open(filename, 'wb') as f:
		for key, postlist in inverted_index.items():
			offset = f.tell()
			SingleStringDict.add_word(word = key, df = postlist.df, post_list_id = offset)
			try:
				write_posting_gamma(postlist)
			except Exception, e:
				print inverted_index[key]
	SingleStringDict.compress(filename)

def pregamma_handle_didlist(postlinglist):
	def prehandle_dtlist(plist):
		pl = sorted(plist)[::-1]
		for i in range(len(plist) - 1):
			pl[i] = pl[i] - pl[i + 1]
		pl = pl[::-1]
		# Note: If the first element is 0, the Gamma cannot represent, so +1
		pl[0] = pl[0] + 1
		return pl

	resultpl = []
	pl = sorted(postlinglist.docitemmap.values(), key= lambda x: x.id)
	did = pl[0].id

	# NOTE: the first docID should +1, because gamma code cannot represent 0
	resultpl.extend([pl[0].id + 1, pl[0].dtf])
	resultpl.extend(prehandle_dtlist(pl[0].positions))
	for v in pl[1:]:
		resultpl.extend([v.id - did, v.dtf])
		resultpl.extend(prehandle_dtlist(v.positions))
		did = v.id
	return resultpl

# degamma the didlist from a int list
def degamma_didlist(l, name = ''):

	def succ_handle_dtlist(plist):
		pl = plist[:]
		pl[0] = pl[0] - 1
		for j in range(1,len(plist)):
			pl[j] = pl[j] + pl[j - 1]
		# Note: If the first element is 0, the Gamma cannot represent, so +1
		return pl
	result = dict()
	i = 0
	if len(l) >= 2:
		predocid, tf,  i = l[0] - 1, l[1], 2
		if i + tf > len(l): raise PostingListInitError('The init postlist data is error: %s\n' % (str(l)))
		dtl = succ_handle_dtlist(l[i:i + tf])
		result[predocid] = DocItem(predocid, tf, dtl)
		i = i + tf
	else:
		raise PostingListInitError('The init postlist data is error: %s\n' % (str(l)))
	
	while i < len(l):
		docid = predocid + l[i]
		tf = l[i + 1]
		i  = i + 2
		if i + tf > len(l):
			raise PostingListInitError('The init postlist data is error: %s\n' % (str(l)))
		dtl = succ_handle_dtlist(l[i:i + tf])
		i = i + tf
		result[docid] = DocItem(docid, tf, dtl)

	return PostingList(_name = name, _df = len(result.keys()), _docmap = result)

def write_postlist_gamma(f, offset, code_data):
	f.seek(offset)
	length = (len(code_data)-1) / 8 + 1
	# using 4 Bytes
	f.write(struct.pack('I', length))
	# using length Bytes
	for i in range(0, len(code_data), 8):
		if i + 8 < len(code_data):
			f.write(struct.pack('B', int(code_data[i:i + 8], 2)))
		else:
			# padding
			f.write(struct.pack('B', int(code_data[i:], 2)))
	nextoffset = offset + length + 4
	return nextoffset

def decompress_dict(filename):
	return SingleStringDict.decompress(filename)

def decompress_inverted_index(filename):
	invertedindex = {}
	pldict = SingleStringDict.decompress(filename)
	with open(filename, 'rb') as plf:
		for word, offset in pldict.items():
			# TODO :there are something cause the 
			invertedindex[word] = seek_inverted_index_file(filename, offset)
			
			
	return (pldict, invertedindex)

def seek_inverted_index_file(indexfile, offset, word = ''):

	encode_data = ''
	with open(indexfile, 'rb') as f:
		f.seek(offset)
		length = struct.unpack('I', f.read(4))[0]
		datalist = []
		for i in range(0, length, 8):
			bdata = bin(struct.unpack('B', f.read(1))[0])[2:]
			datalist.append(bdata)

		for i in range(len(datalist) - 1):
			datalist[i] = '%s%s' % ('0' * (8 - len(datalist[i])), datalist[i])
		left = ((((length - 1) >> 3) + 1) << 3) - length
		datalist[-1] = '%s%s' % ('0' * (8 - left - len(datalist[-1])), datalist[-1])
		encode_data = ''.join(datalist)
		print degamma(encode_data)
	return degamma_didlist(degamma(encode_data), word)
 