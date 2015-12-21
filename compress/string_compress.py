# -*- encode:utf-8 -*-
# filename: huffman code 
# author: cwlseu@qq.com
# Date: 2015-11-11

import struct
import pickle
from collections import Counter

class Node:
    def __init__(self):
        self.value = ''
        self.left = None
        self.right = None
        self.frequency = 0
        self.code = ''

# let the unique value be the key in the map
def change_value_to_key(huffmap):
    result_map = {}
    for (key, value) in huffmap.items():
        result_map[value] = key
    return result_map

def code_with_huffname_tree(root):
    if root.left:
        root.left.code = '%s%s' % (root.code, '0')
        code_with_huffname_tree(root.left)
    if root.right:
        root.right.code = '%s%s' % (root.code, '1')
        code_with_huffname_tree(root.right)

def construct_huffman_tree(lettermap):
    # prepare all the leap node for construct huffman tree
    nodelist = []
    for (key, value) in lettermap.items():
        node = Node()
        node.value = key
        node.frequency = value
        nodelist.append(node)
    nodelist.sort(cmp=lambda n1, n2: cmp(n1.frequency, n2.frequency))

    # construct huffnam tree
    for i in range(len(nodelist) - 1):
        # get the first and second frequence smallest node to link together 
        # which means the larger frequence code length will be smaller
        node1 = nodelist[0]
        node2 = nodelist[1]
        node = Node()
        node.left = node1
        node.right = node2
        node.frequency = node1.frequency + node2.frequency
        nodelist[0] = node
        nodelist.pop(1)
        nodelist.sort(cmp=lambda n1, n2: cmp(n1.frequency, n2.frequency))

    return nodelist[0]
    
def print_code(root):
    if not root.left and not root.right:
        print "%s %s" % (root.value, root.code)
    if root.left:
        print_code(root.left)
    if root.right:
        print_code(root.right)


def save_code(huffman_map, node):
    if not node.left and not node.right:
        huffman_map[node.value] = node.code
    if node.left:
        save_code(huffman_map, node.left)
    if node.right:
        save_code(huffman_map, node.right)

def compress(origindata, ssdfile = 'compress.ssd'):
    # count the frequency of each letter
    lettermap = Counter(origindata)
    
    root = construct_huffman_tree(lettermap)
    code_with_huffname_tree(root)

    # save the node code to a map
    huffman_map = {}
    save_code(huffman_map, root)

    code_data = ''
    for letter in origindata:
        code_data += huffman_map[letter]
    # print_code(root)

    with open(ssdfile, 'wb') as f:
        huffman_map_bytes = pickle.dumps(huffman_map)
        f.write(struct.pack('I', len(huffman_map_bytes)))
        f.write(struct.pack('%ds' % len(huffman_map_bytes), huffman_map_bytes))
        f.write(struct.pack('B', len(code_data) % 8))
        for i in range(0, len(code_data), 8):
            if i + 8 < len(code_data):
                f.write(struct.pack('B', int(code_data[i:i + 8], 2)))
            else:
                # padding
                f.write(struct.pack('B', int(code_data[i:], 2)))
    return ssdfile

def decompress(filename):
    with open(filename, 'rb') as f:
        size = struct.unpack('I', f.read(4))[0]
        huffman_map = pickle.loads(f.read(size))
        
        left = struct.unpack('B', f.read(1))[0]

        data = f.read(1)
        datalist = []

        while not data == '':
            bdata = bin(struct.unpack('B', data)[0])[2:]
            datalist.append(bdata)
            data = f.read(1)
    
    for i in range(len(datalist) - 1):
        datalist[i] = '%s%s' % ('0' * (8 - len(datalist[i])), datalist[i])
    datalist[-1] = '%s%s' % ('0' * (left - len(datalist[-1])), datalist[-1])
    encode_data = ''.join(datalist)
    current_code = ''
    huffman_map = change_value_to_key(huffman_map)
    result = ''
    for letter in encode_data:
        current_code += letter
        if huffman_map.get(current_code):
            result = result + huffman_map[current_code]
            current_code = ''
    return result

def test_huffman_compress():
    str1 = 'aaaaabbbbb'
    f = compress(str1)
    print decompress(f)
if __name__ == '__main__':
    test_huffman_compress()