__author__ = 'wenlong cao'

import sys
import os
import math

from stemming.pyporter2 import stem
from compress.index_gamma \
import decompress_inverted_index, seek_inverted_index_file, decompress_dict
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
            term_index[term] = seek_inverted_index_file(idx_file, dicts[term], term)
            print term_index[term]

            # add doc# to set
            for doc in term_index[term].docitemmap:
                docs_set.add(int(doc))
            query_table[term] = {}
            query_table[term]["tf"] = 1
            query_table[term]["df"] = term_index[term].df
            
            query_table[term]["idf"] = math.log(N / query_table[term]["df"], 10)
            query_table[term]["w"] = (1 + math.log(query_table[term]["tf"])) * query_table[term]["idf"]
        else:
            term_index[term] = {}
            query_table[term] = {}
            query_table[term]["tf"] = 1
            query_table[term]["df"] = 0
            query_table[term]["idf"] = 0
            query_table[term]["w"] = 0
    return (query_table, docs_set, term_index)

def docs_weight(docs_set, term_index, query_string, query_table):

    docs_table = {}
    # Calculate query's weight
    while True:
        try:
            element = str(docs_set.pop())
        except KeyError:
            break
        docs_table[element] = {}
        for term in query_string:
            docs_table[element][term] = {}
            docs_table[element][term]["tf"] = 0

            if element in term_index:

                docs_table[element][term]["tf"] = term_index[term][element].dtf
            
    for doc in docs_table:
        for term in query_string:
            if docs_table[doc][term]["tf"] > 0:
                docs_table[doc][term]["w"] = (1 + math.log(docs_table[doc][term]["tf"], 10)) * math.log(
                    query_table[term]["df"], 10)
            else:
                docs_table[doc][term]["w"] = 0
    return docs_table

def cos_vector_space_model(query_table, docs_table):
    query_len = 0
    docs_score = {}
    for term in query_table:
        query_len += query_table[term]["w"] * query_table[term]["w"]
    query_len = math.sqrt(query_len)

    for doc in docs_table:
        up_part = 0
        doc_len = 0
        for terms in docs_table[doc]:
            up_part += docs_table[doc][terms]["w"] * query_table[terms]["w"]
            doc_len += docs_table[doc][terms]["w"] * docs_table[doc][terms]["w"]

        docs_score[doc] = up_part / (math.sqrt(doc_len) * query_len)
    return docs_score

def query(file_name, query_string, return_count = 10):

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
    query(file_name, query_string, return_count)  

if __name__ == "__main__":
    main()

