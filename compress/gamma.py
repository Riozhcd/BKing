#!/usr/bin/python
# coding:utf-8
# author: jiaxing deng
# create: 2015-12-1
# update: wenlong cao
# description: 
# The element in gamma list should be the integer >= 1
class GammaError(Exception):
    pass
def to_bin(num):
    a = int(num)
    mid = []
    str = ''
    while True:
        if a == 0:
            break
        a, rem = divmod(a, 2)
        mid.append(rem)
    mid.reverse()
    for i in mid:
        str = str + '%d' % i
    return str


def gamma(num):
    if num < 1:
        raise GammaError('The gamma value should be >= 1, but %d found' % num)
    cur = ''  
    num_bin_coding = to_bin(num) 
    cod_length = len(num_bin_coding)  
    length = '1' * (cod_length - 1) + '0' 
    for i in range(1, cod_length):
        cur = cur + '%s' % num_bin_coding[i]
    return length + cur

def degamma(str):
    i = 0
    temp = 0
    num = 0
    b = []
    
    while(i < len(str)):
        if(str[i] != '1'):
            a = [1]
            j = 0
            for j in range(1, i - temp + 1):
                a.append(int(str[i + j]))
            a.reverse()
            for k in range(0, len(a)):
                num += a[k] * (2**k)
            b.append(num)
            i += j
            temp = i + 1
            num = 0
        i += 1
    return b

def gamma_list(l):
    gammastr = ''

    for i in l:
        gammastr += gamma(i)
    return gammastr
  
    

def testGamma():
    try:
        gamma(0)
    except GammaError:
         print 'gamma 0 raise exception'
    l = [1, 2 ,3, 4 ,1 ,1, 1, 3 ,4 ,5 ,6,1,1,1]
    g = gamma_list(l)

    if decompression(g) == l:
        print 'success'
    else:
        print 'gamma list error'
