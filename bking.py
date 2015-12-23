__author__ = 'wenlong cao'

import sys
import os
import math

from stemming.pyporter2 import stem
from compress.index_gamma \
import decompress_inverted_index, seek_inverted_index_file, decompress_dict
from indexing.inverted_index import  PostingList, InvertedIndex
from utility.stringUtil import split_words

def getCorpusDoc(filename):
    docfile = filename +'.docID'
    docs_byID = dict()
    docs_byName = dict()
    try:
        with open(docfile) as f:
            for line in f.readlines():
                doc = line.split()
                docs_byID[doc[1]] = tuple(doc)
                docs_byName[doc[0]] = tuple(doc)
        return (len(docs_byName.keys()),docs_byID, docs_byName)
    except IOError , e:
        print docfile, ' Not found!'
    

def usage():
    print "Usage:"
    print "\tpython "+ sys.argv[0]+" [-r number] -w warc_file_name -q free_query_text"
    print "\tpython"+ sys.argv[0]+ "-h"
    print "\r\nParameter:"
    print "\t" + "-w\t", "corpus file, can auto detect index file is exist or not."
    print "\t"+ "-r\t", "control that how many document may display. default is 10"
    print "\t"+ "-q\t", "free text query term"
    print "\t"+ "-h\t", "show this helper"
    print "\r\nExample:"
    print "python "+ sys.argv[0]+" -w xxxx.trec.1"+ " -ql hong kong"
    exit(0)

def stem_query(query_string):
    return filter(lambda word: stem(word).lower(), query_string)

def query_weight(query_string, dicts, idx_file, N):
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
           
            if doc_len == 0:
                docs_score[doc] = 0
            else:
                docs_score[doc] = up_part / (math.sqrt(doc_len) * euclidean(query_table))
    return docs_score

def BKing(file_name, query_string, return_count = 10):

    # set idx file and dict file path
    idx_file = file_name + ".index"
    # error detection
    if not os.path.isfile(idx_file):
        print "Error: index dictionary file inverted index file (.index) not found. Please Run:\
        python corpusParser.py -f %s -s %s" % (file_name, 'stopword')
        exit(1)

    # read dict file to dict
    dicts = decompress_dict(idx_file)
    (N, docsyID, docsByName) = getCorpusDoc(file_name)

    # docs's parameter table
    docs_table = {}
  
    # docs score hash, use cosine similarity score with weight use tf-idf
    docs_score = {}
    # stem the query string
    query_string = stem_query(query_string)

    (query_table, docs_set, term_index) = query_weight(query_string, dicts, idx_file, N)
   
    docs_table = docs_weight(docs_set, term_index, query_string, query_table)

    

    docs_score = cos_vector_space_model(query_table, docs_table)

    print "Query terms:", query_string
    print "Top", return_count, "results:"
    print "doc#\tscore"
    count = return_count
    for i in sorted(docs_score, key=docs_score.get, reverse=True):
        count -= 1
        if count < 0:
            break
        print "%d\t%.6f" % (int(i), docs_score[i])

    if count >= 0:
        print "Only have found  %d relevant documents." % (return_count - count)

    print '\n*****************Some information about corpus*************************'
    print "The query string in corups information:"
    for i in term_index:
         if term_index[i].df > 0:
            term_index[i].output()

    print '\n*****************Some information about corpus*************************'
    for doc in docsByName.values():
        print doc[1], " docID:", doc[0], " docLength:", doc[2] 
def main():
    return_count = 10
    #parse parameters
    if len(sys.argv) >= 3:

        if "-w" in sys.argv:
           file_name = sys.argv[sys.argv.index("-w") + 1]
        else:
            usage()

        if "-r" in sys.argv:
            return_count = int(sys.argv[sys.argv.index("-r") + 1])

        if "-ql" in sys.argv and "-qs" not in sys.argv:
            query_strlist = stem_query(sys.argv[sys.argv.index("-ql") + 1:])
            
        elif "-qs" in sys.argv and "-ql" not in sys.argv:
            query_string = str(sys.argv[sys.argv.index("-qs") + 1:])
            query_strlist = stem_query(split_words(query_string))
        else:
            usage()
    else:
       usage()
  
    BKing(file_name, query_strlist, return_count)  

if __name__ == "__main__":
    main()

