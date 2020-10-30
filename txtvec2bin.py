#!/usr/bin/python3

import numpy as np
import sys


def txt2bin(txtfile, binfile, vocabfile):
    f = open(txtfile)
    dim = int(f.readline().split()[1])
    vec = np.loadtxt(f, usecols=range(1, dim +1))
    f = open(txtfile)
    f.readline()
    vocab = [line.split(None, 1)[0] for line in f]

    f = open(vocabfile, 'w')
    for w in vocab:
        f.write('%s 0\n' % w)
    f.close()

    vec.tofile(binfile, format='f8')


if __name__ == '__main__':
    if sys.argv[3:]:
        txt2bin(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print('usage: txtvec2bin.py WORD2VEC.txt VECTORS.bin VOCAB.txt')
        
