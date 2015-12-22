#-*- encoding = utf-8 -*-
# \introduce:
# 	The script is the compress and decompress of single string dict
# 	We add some tip for the single string compress
# 	Using the huffman code to save the long single string which will
# 	save a lot of memory
# \author: wenlong cao
# \create : 2015-11-13

import pickle
import struct
from singleStringHuffman import huffman_decompress, huffman_compress

class DictFileError(Exception):
	pass
class CompressFileError(Exception):
	pass

def byte_to_int(b1, b2, b3):
	return (b1 << 16)|(b2<< 8)|(b3&0xFF)

def int_to_3b(i):
	try:
		i = int(i)
		b1, b2 , b3 = (i&0xFF0000) >> 16, (i&0x00FF00) >> 8, i&0xFF
		return (b1, b2, b3)
	except ValueError, e:
		return None
	
class SingleStringDict:
	'''
	A Singleton class to save the dict
	Each item in dict should including the following:
		df
		post_list_id
		tid
	'''
	_Str = ''
	_TID = 0
	_Dict = dict()

	def __init__(self, word = None, df  = None, post_list_id = None, tid = None):
		self.df 		= df if df else 0
		self.post_id 	= post_list_id if post_list_id else 0
		self.tid = 0
		if word and not tid:
			self.tid 		= self.getTID(word)
		elif tid:
			self.tid = tid

	def getTID(self, word):
		current = SingleStringDict._TID
		SingleStringDict._TID  =  SingleStringDict._TID + len(word)
		return current

	def __repr__(self):
		return str((self.df, self.post_id, self.tid))

	@staticmethod
	def add_word(word, df, post_list_id):
		SingleStringDict._Str += word
		ssd = SingleStringDict(word = word, df  = df, post_list_id = post_list_id)
		SingleStringDict._Dict[word] = ssd

	@staticmethod
	def del_word(word):
		try:
			del SingleStrignDict._Dict[word]
		except KeyError, e:
			pass

	@staticmethod
	def __dict_compress(ssdfile = 'compress.ssd'):
		length = len(SingleStringDict._Dict.keys())
		with open(ssdfile, 'wb') as f:
			f.write(struct.pack('Q', length))
			for v in SingleStringDict._Dict.values():
				f.write(struct.pack('I', int(v.df,)))
				f.write(struct.pack('I', int(v.post_id)))
				(b1, b2, b3) = int_to_3b(v.tid)
				f.write(struct.pack('B', b1))
				f.write(struct.pack('B', b2))
				f.write(struct.pack('B', b3))	
	@staticmethod
	def __dict_decompress(filename):
		with open(filename, 'rb') as f:
			idx_dict = []
			size = struct.unpack('Q', f.read(8))[0]
			for i in range(size):
				df = struct.unpack('I', f.read(4))[0]
				postid = struct.unpack('I', f.read(4))[0]
				b1 = struct.unpack('B', f.read(1))[0]
				b2 = struct.unpack('B', f.read(1))[0]
				b3 = struct.unpack('B', f.read(1))[0]
				tid = byte_to_int(b1, b2, b3)
				idx_dict.append(SingleStringDict(None, df, postid, tid))
		return idx_dict

	@staticmethod
	def compress(filename):
		hfmfile = filename + '.dicthfm'
		ssdfile = filename + '.dictssd'
		huffman_compress(SingleStringDict._Str, hfmfile)
		SingleStringDict.__dict_compress(ssdfile)

	@staticmethod
	def decompress(filename):
		hfmfile = filename + '.dicthfm'
		ssdfile = filename + '.dictssd'
		singlestring = huffman_decompress(hfmfile)
	 	dicts = SingleStringDict.__dict_decompress(ssdfile)
	 	post_list = dict()
	 	# get word from single string, and construct the SingleStringDict 
	 	dicts = sorted(dicts, key=lambda x: x.tid)
	 	tid = dicts[0].tid
	 	lastitem = dicts[0]

	 	for item in dicts[1:]:
	 		word = singlestring[tid : item.tid]
	 		SingleStringDict._Dict[word] = lastitem
	 		post_list[word] = lastitem.post_id
	 		tid = item.tid
	 		lastitem = item
	 	word = singlestring[lastitem.tid:].strip()
	 	SingleStringDict._Dict[word] = lastitem
	 	post_list[word] = lastitem.post_id

	 	SingleStringDict._Str = singlestring
	 	SingleStringDict._TID = len(singlestring)
		return post_list	



def test_dict_compress():
	dictfile = 'shakespeare-merchant.trec.1.dict.txt'
	SingleStringDict.compress(dictfile)

def test_dict_decompress():
	dictfile = 'shakespeare-merchant.trec.1.dict.txt'
	postlist = SingleStringDict.decompress(dictfile)

	

if __name__ == '__main__':
	test_dict_compress()
	test_dict_decompress()
