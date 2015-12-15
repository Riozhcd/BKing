# coding=utf-8
import sys
import os.path
import time
import re
from optparse import OptionParser
from stemming.pyporter2 import stem

class doc_item:
	def __init__(self):
		self.id = 0
		self.size = 0
		self.list = []

class word_item:
	def __init__(self):
		self.name = ''    
		self.size = 0     
		self.map ={}

def split_words(line):
	regex = ur"[<.*?>|,|.|:|?|!|\"|\(|\)|/|;|\-|\[|\]]"
	line = re.sub(regex, ' ', line).strip()

	regex = ur"\s+"
	line_words = re.split(regex, line)
	return line_words

class CorpusParserInitError(Exception):
	pass

class CorpusParser:

	def __init__(self, corpus_file, stopword_file,
	                   doc_id_file = 'doc_id.txt'):
		if os.path.isfile(corpus_file):
			self.corpus = corpus_file
		else:
			raise CorpusParserInitError("Please input a correct corpus file path")

		self.doc_id, self.line_id = 0, 1
		self.word_map, self.stop_map, self.regex = {}, {} ,{}
		if os.path.isfile(stopword_file):
			with open (stopword_file,'r') as f:
				for line in f:
					self.stop_map[line.strip()] = 1

		
		self.regex['DOCNO'] = ur"<DOCNO>(.*?)</DOCNO>"
		self.doc_id_output = corpus_file + '.docID.txt'

	def __match_docheader(self, line, regex):
		return re.search(regex, line)

	def handle_data(self):
		with open(self.doc_id_output, 'w+') as doc_file, \
		     open(self.corpus, 'r') as corpus:

		    for line in corpus:
				match = self.__match_docheader(line, self.regex['DOCNO'])
				if match:
					self.line_id, self.doc_id = 1, self.doc_id + 1
					doc_file.write(match.groups()[0]+' '+str(self.doc_id)+'\n')
				self.line_id += 1
				line_words = split_words(line)
				for word in line_words:
					# Stem reduction
					word = stem(word).lower()

					if self.stop_map.has_key(word) == False and len(word) != 0:
						self.__add_word_index(word)

	def __add_word_index(self, word):
		word_item_default = word_item()
		doc_item_default = doc_item()

		self.word_map.setdefault(word, word_item_default)
		if self.word_map[word].size == 0:
			self.word_map[word].name = word

		self.word_map[word].map.setdefault(self.doc_id,doc_item_default)

		if self.word_map[word].map[self.doc_id].size == 0:
			self.word_map[word].map[self.doc_id].id = self.doc_id
			self.word_map[word].size += 1

		self.word_map[word].map[self.doc_id].size += 1
		self.word_map[word].map[self.doc_id].list.append(self.line_id)

	def dump_index(self, index_file):
		with open(index_file, 'w+') as index_out_file,\
				open(self.corpus+'.dict.txt', 'w+') as dict_out_file:
			for k0, v0 in self.word_map.items():
				dict_out_file.write(k0 + ", " + str(index_out_file.tell()) + "\n")
				index_out_file.write(k0+','+str(v0.size)+':<')
				for k1,v1 in v0.map.items():
					tmp=str(v1.list).replace('[','<').replace(']','>')
					index_out_file.write(str(k1)+','+str(v1.size)+':'+tmp+';')
				index_out_file.write('>;\n')


	def __del__(self):
		pass

def main():
	parser = OptionParser(usage="""\
	        Indexer for your input corpus.

	        Usage: %prog [options]

	        Create a index for user input document
	        """)
	parser.add_option('-f', '--corpus', metavar="FILE",
			help='Corpus data resolute path')
	parser.add_option('-s', '--stopword', metavar="FILE",
			help='A file including stopword')
	parser.add_option('-i', '--index', metavar="FILE",
			help='output result to the file')

	opts, args = parser.parse_args()
	if not opts.corpus:
		parser.print_help()
		sys.exit(1)

   	corpus_file = opts.corpus
	stopword_file = opts.stopword
	if corpus_file and not opts.index:
		index_file = corpus_file + '.index.txt'
	else:
		index_file = opts.index

	doc_id_file = corpus_file + '.docID.txt'

	try:
		parser = CorpusParser(corpus_file, stopword_file)
	except CorpusParserInitError, e:
		print "Please Input correct init parser data"

	starttime = time.time()

	print("Start......")

	parser.handle_data()
	parser.dump_index(index_file)

	print("dump index from memory to file " + index_file)
	print("----------------------------------------------------------")
	print("finish")
	print("----------------------------------------------------------")
	print("Total time analysis:")
	print(time.time() - starttime, "s")

if __name__ == '__main__':
	main()