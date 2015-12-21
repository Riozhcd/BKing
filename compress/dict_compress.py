import pickle
class DictFileError(Exception):
	pass
class CompressFileError(Exception):
	pass

class SingleStringDict:
	_Str = ''
	_TID = 0
	_Dict = dict()

	def __init__(self, word, df, post_list_id):
		if not (word and df and post_list_id):
			self.df = ''
			self.post_id = ''
			self.tid = ''
			return

		self.df = df
		self.post_id = post_list_id
		self.tid = self.getTID(word)
		
	def getTID(self, word):
		current = SingleStringDict._TID
		SingleStringDict._TID  =  SingleStringDict._TID + len(word)
		return current
	def __str__(self):
		return str(self.df)+','+str(self.post_id)+','+str(self.tid)+'\n'

	@staticmethod
	def add_word(word, df, post_list_id):
		SingleStringDict._Str = SingleStringDict._Str + word
		ssd = SingleStringDict(word, df, post_list_id)
		SingleStringDict._Dict[word] = ssd

	@staticmethod
	def del_word(word):
		try:
			del SingleStrignDict._Dict[word]
		except KeyError, e:
			pass
		 
	@staticmethod
	def dump(filename):
		# read file
		with open(filename, 'wb') as f:
			f.write(str(len(SingleStringDict._Str)))
			f.write('\n')
			f.write(SingleStringDict._Str)
			f.write('\n')
			for key in SingleStringDict._Dict:
				f.write(str(SingleStringDict._Dict[key]))
	
	@staticmethod
	def readfile(filename):
		with open(filename, 'rb') as f:
			length = f.readline()
			s = f.read(length) 
			f.read(1)
			line = f.readline()
			word, df, pid = '', '', ''
			if line:
				lines = line.strip().split(',')
				if len(lines) != 3:
					raise CompressFileFormatError('There are format error in:' + line)
				word, df, pid = lines[2], lines[0], lines[1]
			line = f.readline()
			while line:
				lines = line.strip().split(',')
				if len(lines) != 3:
					raise CompressFileFormatError('There are format error in:' + line)
				word = s[word:lines[2] - word]
				SingleStringDict.add_word(word, df, pid)
				df, pid, word = lines[0], lines[1], lines[2]
				line = f.readline()
			word = s[word:]
			SingleStringDict.add_word(word, df, pid)

def dict_single_string_compress(dictfile, targetfile = None):
	if not targetfile:
		targetfile = dictfile+'.sscompress'
	# read file
	with open(dictfile, 'r') as source:
		# prase dictfile
		for line in source:
			word = map(lambda x: x.strip(), line.strip().split(','))
			if len(word) != 3:
				raise DictFileError('The Dict format is error in :' + line)
			SingleStringDict.add_word(word[0], word[1], word[2])
	SingleStringDict.dump(targetfile)
	return targetfile
	
def test_dict_compress():
	dictfile = 'shakespeare-merchant.trec.1.dict.txt'
	dict_single_string_compress(dictfile)
if __name__ == '__main__':
	test_dict_compress()