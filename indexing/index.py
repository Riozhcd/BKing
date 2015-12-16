__author___ = 'wenlong cao'

from docindex import DocIndex 
import numbers
class Index:
    index = {}

    def read_partial_index(self, doc_id, docindex):
        for i in docindex.index:
            if i not in self.index:
                self.index[i] = {}
            self.index[i][doc_id] = docindex.index[i]

    def dump(self, filename):
        with open(filename + ".idx", "w+") as f, \
            open(filename + ".dict", "w+") as fdic:
            for k, v in ((k, self.index[k]) for k in sorted(self.index)):
                fdic.write(k + ", " + str(f.tell()) + "\n")
                f.write(k + ", " + str(len(v)) + ":<")
                for doc in v:
                    f.write(str(doc) + ", " + str(len(v[doc])) + ":<")
                    fr = True
                    for pos in v[doc]:
                        if fr:
                            f.write(str(pos))
                            fr = False
                        else:
                            f.write(", " + str(pos))
                    f.write(">;")
                f.write(">;\n")

    @staticmethod
    def read(filename):
        """
        read plain text index file to partial index
        :param filename:
        :return:
        """
        f = open(filename, "r")
        lines = f.readlines()
        index = Index()
        for line in lines:
            (key, posting_list) = line.split(",", maxsplit=1)
            docs = posting_list[posting_list.find(":") + 2:-4].split(";")
            for doc in docs:
                docindex = PartialIndex()
                (docId, position) = doc.split(",", maxsplit=1)
                positions = position[position.find(":") + 2:-1].split(",")
                for pos in positions:
                    docindex.push(key, int(pos))
                index.read_partial_index(docId, docindex)
        return index

    @staticmethod
    def parse_posting_entry(entry):
        '''
        e.g:
        worth,3:9,1:63;2,5:45, 46, 82, 157, 212;10,1:57;;
        '''
        index = Index()

        # The parameters of str.split are called sep and maxsplit:
        # str.split(sep="&", maxsplit=8)
        # But you can only use the parameter names like this in Python 3.x. In Python 2.x, you need to do:
        # str.split("&", 8)
        (key, posting_list) = entry.split(",", 1)
    
        '''
        posting_list = 3:9,1:63;2,5:45, 46, 82, 157, 212;10,1:57;;
        '''
        docs = posting_list[posting_list.find(":") + 1:-3].split(";")
        '''
        9,1:63
        2,5:45, 46, 82, 157, 212
        10,1:57
        '''
        for doc in docs:
            docindex = DocIndex()
            (docId, position) = doc.split(",", 1)
            position = position[position.find(":") + 1:-1]
            if ',' in position:
                positions = position.split(", ")
            else:
                positions = [position]
            for pos in positions:
                if '' != pos: # fix a bug: position have ''
                    docindex.push(key, int(pos))
            index.read_partial_index(docId, docindex)
        return index

    @staticmethod
    def read_index_by_offset(filename, offset):
        f = open(filename, "r")
        f.seek(offset)
        line = f.readline()
        return Index.parse_posting_entry(line)

def test():
    idx_file = 'shakespeare-merchant.trec.1.index.txt'
    dict_file ='shakespeare-merchant.trec.1.dict.txt'
    dict_file = open(dict_file, 'r')
    dicts = {}
    for d in dict_file:
        (key, offset) = d.split(', ')
        dicts[key] = int(offset)
    for term in dicts:
        try:
            Index.read_index_by_offset(idx_file, dicts[term]).index
        except ValueError, e:
            print term
            #print e
        