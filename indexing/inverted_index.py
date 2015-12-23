from collections import OrderedDict
class DocItem:
	def __init__(self, _id = None, _dtf = None, _positions = None):
		self.id = _id if _id else 0
		self.dtf = _dtf if _dtf else 0
		self.positions = _positions if _positions else [] 
	def __str__(self):
		result = str(self.dtf)+':'+str(self.positions).replace('[','').replace(']','')
		return result

class PostingListInitError(Exception):
	pass

class PostingList:
	def __init__(self, _name = None, _df = 0, _docmap = None):
		self.name = _name if _name else ''
		self.df = _df if _df else 0   
		self.docitemmap = _docmap if _docmap else OrderedDict()

	def add_docitem(self, docid, docItem):
		self.docitemmap[docid] = docItem

	def __str__(self):
		resultstr = self.name+','+str(self.df)+':'
		for k1, v1 in self.docitemmap.items():
			resultstr =resultstr+str(k1)+','+str(v1)+';'
		return resultstr 

	def output(self):
		resultstr = self.name+'>> df:'+str(self.df)
		for k1, v1 in self.docitemmap.items():
			resultstr += "\n\tdocid:"+ str(k1)+'\t dtf:'+str(v1.dtf) + ' offset:'+ (str(v1.positions))
		print resultstr
	@staticmethod
	def merge(p1, p2):
		docitemmap = dict(p1.docitemmap, **p1.docitemmap)
		df = len(docitemmap.keys())
		return PostingList(p1.name, df, docitemmap)

class InvertedIndex:
	_index = {}
	def __init__(self):
		pass
	@staticmethod
	def get_posting_list(word):
		return InvertedIndex._index[word]

	@staticmethod
	def add_word_postlist(word, postlist):
		if word in InvertedIndex._index:
			# merge
			InvertedIndex._index[word] = \
			PostingList.merge(InvertedIndex._index[word], postlist)
		else:
			InvertedIndex._index[word] = postlist
	

	@staticmethod
	def InvertedIndex():
		return InvertedIndex._index