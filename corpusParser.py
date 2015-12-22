# coding=utf-8
# author: wei zhang
# update: wenlong cao
# create: 2015-12-10
# description:
# Read corpus file and parser into a inverted index
# then compress the inverted index into a file
# Update point: Update the offset from the line id into a doc offset
import sys
import os.path
import time
import re
from optparse import OptionParser
from collections import OrderedDict
from stemming.pyporter2 import stem

from indexing.inverted_index import DocItem, PostingList, InvertedIndex
import compress.index_gamma as IndexCompress
def split_words(line):
	regex = ur"[\d*|<.*?>|,|.|:|?|!|\"|\(|\)|/|;|\-|\[|\]]"
	l = re.sub(regex, ' ', line).strip()

	regex = ur"\s+"
	line_words = re.split(regex, l)
	return line_words

class CorpusParserInitError(Exception):
	pass

class CorpusParser:

	def __init__(self, corpus_file, stopword_file,
	                   doc_id_file = 'doc_id.docID'):
		if os.path.isfile(corpus_file):
			self.corpus = corpus_file
		else:
			raise CorpusParserInitError("Please input a correct corpus file path")

		self.doc_id = 0
		self.doc_offset = 0
		self.word_map, self.stop_map, self.regex = {}, {} ,{}
		if os.path.isfile(stopword_file):
			with open (stopword_file,'r') as f:
				for line in f: self.stop_map[line.strip()] = 1
		
		self.regex['DOCNO'] = ur"<DOCNO>(.*?)</DOCNO>"
		self.doc_id_output = corpus_file + '.docID'

	def __match_docheader(self, line, regex):
		return re.search(regex, line)

	def handle_data(self):
		'''
		Note:
			The word item site from the line number to doc file offset
		'''
		with open(self.doc_id_output, 'w+') as doc_file, \
		     open(self.corpus, 'r') as corpus:
		    for line in corpus:
				offset_inline = 0
				match = self.__match_docheader(line, self.regex['DOCNO'])
				if match:
					self.doc_id = self.doc_id + 1
					self.doc_offset = 0
					doc_file.write(match.groups()[0]+' '+str(self.doc_id)+'\n')

				line_words = split_words(line)
				lastword = ''
				for word in line_words:
					offset_inline = line.find(word, offset_inline + len(lastword))
					lastword = word	
					# Stem reduction
					word = stem(word).lower()
					if self.stop_map.has_key(word) == False and len(word) != 0: 
						self.__add_word_index(word, self.doc_offset + offset_inline)
				self.doc_offset = self.doc_offset + len(line)

	def __add_word_index(self, word, offset):
		word_item_default = PostingList()
		doc_item_default = DocItem()
		if offset < 0:
			print word
			return
		self.word_map.setdefault(word, word_item_default)
		if self.word_map[word].df == 0:
			self.word_map[word].name = word

		self.word_map[word].docitemmap.setdefault(self.doc_id, doc_item_default)

		if self.word_map[word].docitemmap[self.doc_id].dtf == 0:
			self.word_map[word].docitemmap[self.doc_id].id = self.doc_id
			self.word_map[word].df += 1

		self.word_map[word].docitemmap[self.doc_id].dtf += 1
		self.word_map[word].docitemmap[self.doc_id].positions.append(offset)

	def dump_index_bracket(self, index_file):
		with open(index_file, 'w+') as index_out_file,\
				open(self.corpus+'.dict', 'w+') as dict_out_file:
			for k0, v0 in self.word_map.items():
				dict_out_file.write(k0 + ", " + str(index_out_file.tell()) + "\n")
				index_out_file.write(k0+','+str(v0.df)+':<')
				for k1,v1 in v0.docitemmap.items():
					tmp=str(v1.list).replace('[','<').replace(']','>')
					index_out_file.write(str(k1)+','+str(v1.dtf)+':'+tmp+';')
				index_out_file.write('>;\n')

	def dump_index(self, index_file):
		self.word_map = OrderedDict(sorted(self.word_map.items(), key=lambda t: t[0]))
		IndexCompress.compress_inverted_index(self.word_map, index_file)
		return 
		with open(index_file, 'w+') as index_out_file,\
				open(self.corpus+'.dict', 'w+') as dict_out_file:
			self.word_map = OrderedDict(sorted(self.word_map.items(), key=lambda t: t[0]))

			for k0, v0 in self.word_map.items():
				dict_out_file.write(k0 +',' +str(v0.df)+"," + str(index_out_file.tell()) + "\n")
				index_out_file.write(str(v0))
				index_out_file.write(';\n')

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
		index_file = corpus_file + '.index'
	else:
		index_file = opts.index

	doc_id_file = corpus_file + '.docID'

	try:
		parser = CorpusParser(corpus_file, stopword_file)
	except CorpusParserInitError, e:
		print "Please Input correct init parser data"

	starttime = time.time()

	print "Start......"

	parser.handle_data()
	parser.dump_index(index_file)

	print "dump index from memory to file " + index_file
	print "----------------------------------------------------------"
	print "finish"
	print "----------------------------------------------------------"
	print "Total time analysis:"
	print time.time() - starttime, "s"

if __name__ == '__main__':
	main()