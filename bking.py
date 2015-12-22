__author__ = 'wenlong cao'

import sys
import os
import math

from stemming.pyporter2 import stem
from compress.index_gamma \
import decompress_inverted_index, seek_inverted_index_file, decompress_dict
from indexing.inverted_index import  PostingList, InvertedIndex
N = 15

class Weight:
    tf = 0
    df = 0
    def __init__(tf, df, N):
        if tf > 0 and df > 0 and N > 0:
            self.tf = tf
            self.df = df
            self.N = N
        else:
            raise ValueError("Please input right initilize data")

    @property
    def idf():
        return math.log(self.N / self.df, 10)
    @property
    def w():
        return (1 + math.log(self.tf, 10) * self.idf)
    def __del__():
        pass

def usage():
    print "Usage:"
    print "\tpython "+ sys.argv[0]+" [-r number] -w warc_file_name -q free_query_text"
    print "\tpython"+ sys.argv[0]+ "-h"
    print "\r\nParameter:"
    print "\t" + "-r\t", "WARC file, can auto detect index file is exist or not."
    print "\t"+ "-r\t", "control that how many document may display. default is 10"
    print "\t"+ "-q\t", "free text query term"
    print "\t"+ "-h\t", "show this helper"
    print "\r\nExample:"
    print "python "+ sys.argv[0]+" -w xxxx.trec.1"+ " -q hong kong"
    exit(0)

def stem_query(query_string):
    return filter(lambda word: stem(word).lower(), query_string)

# TODO:
# Update the query weight calculate
def query_weight(query_string, dicts, idx_file):
    ''' Calculate query's weight
    '''
    # term's index
    term_index = {}
    # query's parameter table
    query_table = {} 
    # docs set for merge document
    docs_set = set()

    for term in query_string:
        if term in dicts:
            InvertedIndex.add_word_postlist(term, seek_inverted_index_file(idx_file, dicts[term], term))
            # term_index[term] = seek_inverted_index_file(idx_file, dicts[term], term)
            # add doc# to set
            for doc in InvertedIndex.get_posting_list(term).docitemmap:
                docs_set.add(int(doc))

            query_table[term] = {}
            query_table[term]["tf"] = 1
            query_table[term]["df"] = InvertedIndex.get_posting_list(term).df  
            query_table[term]["idf"] = math.log(N / query_table[term]["df"], 10)
            query_table[term]["w"] = (1 + math.log(query_table[term]["tf"])) * query_table[term]["idf"]
        else:
            InvertedIndex.add_word_postlist(term, PostingList())
            query_table[term] = {}
            query_table[term]["tf"] = 1
            query_table[term]["df"] = 0
            query_table[term]["idf"] = 0
            query_table[term]["w"] = 0
   
    return (query_table, docs_set, InvertedIndex.InvertedIndex())

def docs_weight(docs_set, term_index, query_string, query_table):
   
    docs_table = {}
    # Calculate query's weight
    while True:
        try:
            docid = str(docs_set.pop())
        except KeyError:
            break
        docs_table[docid] = {}
        for word in query_string:
            docs_table[docid][word] = {}
            docs_table[docid][word]["tf"] = 0
            for i in term_index[word].docitemmap:
                if int(docid) == int(i):
                    docs_table[docid][word]["tf"] = term_index[word].docitemmap[int(docid)].dtf
            
    for doc in docs_table.values():
        for word in query_string:
            if doc[word]["tf"] > 0:
                doc[word]['w'] = \
                (1 + math.log(doc[word]["tf"], 10)) * math.log(query_table[word]["df"], 10)
            else:
                doc[word]['w'] = 0
   
    return docs_table

def cos_vector_space_model(query_table, docs_table):

    def euclidean(query_table):
        return math.sqrt(sum(map(lambda x: x['w']**2, query_table.values())))

    docs_score = {}

    for doc in docs_table:
        up_part = 0
        doc_len = 0
        for terms in docs_table[doc]:
            up_part += docs_table[doc][terms]['w'] * query_table[terms]['w']
            doc_len += docs_table[doc][terms]['w'] **2
            try:
                docs_score[doc] = up_part / (math.sqrt(doc_len) * euclidean(query_table))
            except ZeroDivisionError, e:
                pass#print  up_part , math.sqrt(doc_len), euclidean(query_table)
            
        
    return docs_score

def BKing(file_name, query_string, return_count = 10):

    # set idx file and dict file path
    idx_file = file_name + ".index"
    # error detection
    if not os.path.isfile(idx_file):
        print "Error: index dictionary file(.index.dict or inverted index file (.index.idx) not found."
        exit(1)

    # read dict file to dict
    dicts = decompress_dict(idx_file)
    

    # docs's parameter table
    docs_table = {}
  
    # docs score hash, use cosine similarity score with weight use tf-idf
    docs_score = {}
    # stem the query string
    query_string = stem_query(query_string)

    (query_table, docs_set, term_index) = query_weight(query_string, dicts, idx_file)
   
    docs_table = docs_weight(docs_set, term_index, query_string, query_table)

    

    docs_score = cos_vector_space_model(query_table, docs_table)

    print "Query terms:", query_string
    print "Top", return_count, "results:"
    print "doc#\tscore"

    for i in sorted(docs_score, key=docs_score.get, reverse=True):
        return_count -= 1
        if return_count < 0:
            break
        print "%d\t%.3f" % (int(i), docs_score[i])


def main():
    return_count = 10
    #parse parameters
    #if len(sys.argv) >= 3:
    #    if "-w" in sys.argv:
    #       file_name = sys.argv[sys.argv.index("-w") + 1]
    #    else:
    #        usage()
    #   if "-r" in sys.argv:
    #        return_count = int(sys.argv[sys.argv.index("-r") + 1])

    #    if "-q" in sys.argv:
    #        query_string = sys.argv[sys.argv.index("-q") + 1:]
    #    else:
    #        usage()
    #else:
    #   usage()
    file_name = 'shakespeare-merchant.trec.1'

    query_string = 'hello, my name is caowenlong, my favoriate dog is doges, shakespeare merchant'.replace(',','').split()
    BKing(file_name, query_string, return_count)  

if __name__ == "__main__":
    main()

