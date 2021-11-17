#!/usr/bin/python3

from __future__ import print_function

import numpy as np
import os
import argparse


verbose = 3


def read_embeddings(filename, vocab_file='vocab.txt'):
    if filename.endswith('.bvec') or filename.endswith('.bvec32'):
        # bvec: format at embeddings.sketchengine.co.uk
        f = open(filename + '.dic', encoding='utf-8')
        f.readline() # skip dictionary size
        dim = int(f.readline())
        id2str = [w.strip() for w in f]
        dtype = np.float32 if filename.endswith('32') else np.float16
        vec = np.memmap(filename, dtype=dtype, mode='r')
        vec.resize(len(id2str), dim)
    elif filename.endswith('.bin'):
        # bin file  --> words from vocab_file
        id2str = [line.split(None, 1)[0] for line in open(vocab_file, encoding='utf-8')]
        vec = np.memmap(filename, dtype=np.float64, mode='r')
        dim = vec.shape[0] // len(id2str)
        vec.resize(len(id2str), dim)
    else:
        firstline = open(filename).readline().split()
        skipfirst = False
        if len(firstline) == 2:
            dim = int(firstline[1])
            skipfirst = True
        else:
            dim = len(firstline) -1
        f = open(filename, encoding='utf-8')
        if skipfirst:
            f.readline()
        vec = np.loadtxt(f, usecols=range(1, dim +1))
        id2str = [line.split(None, 1)[0] for line in open(filename, encoding='utf-8')]
        if skipfirst:
            id2str = id2str[1:]
        
    str2id = {w: idx for idx, w in enumerate(id2str)}

    if verbose > 2:
        print('read_embeddings: dim=%d shape=%s' % (dim, vec.shape))

    return vec, id2str, str2id


        
        
class Embeddings:
    def __init__(self, filename, vocab_file='vocab.txt'):
        self.vec, self.id2str, self.str2id = read_embeddings(filename, vocab_file)

    def outlier_position(self, iwords, iout):
        clv = [self.compose_vectors(mw) for mw in [iout] + iwords]
        cluster = np.vstack(clv)
        d = np.linalg.norm(cluster, axis=1)
        cluster /= np.expand_dims(d, 1)
        sim = np.sum(np.matmul(cluster, cluster.T), axis=0)
        sim -= 1   # similarity to self
        sim /= len(iwords)    # normalize to the size of cluster
        return sum(sim >= sim[0]), sim

    def compose_vectors(self, multiword_ids):
        v = np.copy(self.vec[multiword_ids[0]])
        for i in multiword_ids[1:]:
            v += self.vec[i]
        v /= len(multiword_ids)
        return v



class SkE_Thesaurus:
    def __init__(self, corpname, minsim=0.05, minfreq=100):
        import manatee
        corp = manatee.Corpus(corpname)
        self.corp = corp
        #self.lempos = corp.get_attr(corp.get_conf('WSATTR'))
        self.word2lem = corp.get_attr('word@' + corp.get_conf('WSATTR'))
        wa = corp.get_attr('word')
        #print('SkE init')
        self.str2id = {wa.id2str(i):wa.id2str(i) for i in range(wa.id_range())
                       if wa.freq(i) >= minfreq}
        #print('SkE str2id')

    def outlier_position(self, iwords, iout):
        alIds, asims = self.find_alternatives([iout] + iwords)
        clsim = [sum([asims.get((a,i),0) for i in alIds]) for a in alIds]
        return sum(s >= clsim[0] for s in clsim), clsim
       
    
    def find_alternatives(self, words):
        import wmap
        # find all lempos aternatives for given words
        alts = []
        candidates = set()
        #print('SkE find_alternatives', words)
        for w in words:
            #print('SkE dynid2srcids str2id:', w)
            r = self.word2lem.dynid2srcids(self.word2lem.str2id(w[0]))
            #print('SkE dynid2srcids next:', w)
            alternatives = [r.next() for _ in range(5) if not r.end()]
            alts.append((w, alternatives))
            candidates.update(alternatives)
        #print('SkE dynid2srcids')

        # simlilarity between all candidates
        thes = wmap.Thesaurus_f(self.corp.get_conf('WSTHES'), 0)
        asims = {}
        for id1 in sorted(candidates):
            thes.find(id1)
            while not thes.eos():
                id2 = thes.getid()
                if id2 in candidates:
                    asims[id1,id2] = thes.getscore()
                thes.next()
        #print('SkE thes')
              
        # find the best of alternatives
        alIds = []
        for w, alternatives in alts:
            if len(alternatives) == 1:
                alIds.append(alternatives[0])
                continue
            asum = [sum([asims.get((a,i),0) for i in candidates
                         if i not in alternatives]) for a in alternatives]
            abest = max(range(len(asum)), key=asum.__getitem__)   # argmax(asum)
            alIds.append(alternatives[abest])
        return alIds, asims

    
def split_multiword(model, multiword):
    if multiword in model.str2id:
        return [model.str2id[multiword]]
    mw = []
    for w in multiword.split('_'):
        if w in model.str2id:
            mw.append(model.str2id[w])
    return mw


    
        
def eval_topic(model, words, outliers, ignore_unknown=False):
    hits = 0
    opp = 0
    if verbose > 1:
        print('Cluster:', ', '.join(words))
    clsize = len(words) +1
    cnt = len(outliers)
    iwords, skipped = [], []
    for w in words:
        ids = split_multiword(model, w)
        if len(ids) == 0:
            skipped.append(w)
        else:
            iwords.append(ids)
    if skipped:
        if verbose > 1:
            print('\tSkipping missing:', ', '.join(skipped))
        if ignore_unknown:
            clsize = len(iwords) + 1
    if len(iwords) < 2:
        return (0 if ignore_unknown else cnt), 0, 0
    for out in outliers:
        iout = split_multiword(model, out)
        if len(iout) == 0:
            if verbose > 1:
                print('\tOutlier:', out, 'not found, skipping')
            if ignore_unknown:
                cnt -= 1
            continue
        pos, sim = model.outlier_position(iwords, iout)
        if pos == clsize:
            hits += 1
        opp += pos/clsize
        if verbose > 1:
            print('\tOutlier:', out, '\tPosition:', pos)
        if verbose > 2 and pos <= len(iwords):
            print('\t   outlier score: %.3f' % sim[0])
            scored = sorted(zip(sim[1:], [w for w in words if w not in skipped]))
            print('\t   more out:', ', '.join(
                ['%s/%.3f' % (w,s) for s,w in scored if s <= sim[0]]))
    if verbose > 1:
        if cnt > 0:
            print('   Accuracy %.3f   OPP %.3f' % (hits/cnt, opp/cnt))
    return cnt, hits, opp


    

def walk_dataset(dirpath, prefix):
    for root, _dirs, files in os.walk(dirpath):
        for fname in files:
            if fname.startswith(prefix):
                text = open(os.path.join(root, fname)).read().strip()
                clt, outt = text.split('\n\n')
                yield fname, clt.split('\n'), outt.split('\n')



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-vectors', type=str, help='evaluate word2vec vectors')
    parser.add_argument('-vocab', default='vocab.txt', type=str,
                        help='vocabulary file for binary vectors')
    parser.add_argument('-corpus', type=str, help='evaluate SkE thesaurus on CORPUS')
    parser.add_argument('-data', default='data', type=str,
                        help='data directory with cluster files')
    parser.add_argument('-prefix', default='', type=str,
                        help='process only files starting with this prefix')
    parser.add_argument('-ignore', default=False, type=bool,
                        help='ignore unknown words')
    parser.add_argument('-v', default=1, type=int,
                        help='verbosity level')
    args = parser.parse_args()

    if not args.corpus and not args.vectors:
        parser.print_help()
        parser.exit(1)

    verbose = args.v
    if args.corpus:
        model = SkE_Thesaurus(args.corpus)
    else:
        model = Embeddings(args.vectors, args.vocab)
    quest, clust, hits, opp = 0,0,0, 0
    for name, words, outs in walk_dataset(args.data, args.prefix):
        if verbose > 1:
            print(name)
            print('-' * len(name))
        c, h, o = eval_topic(model, words, outs, args.ignore)
        quest += c
        hits += h
        opp += o
        clust += 1
        if verbose == 1 and c > 0:
            print('%.3f\t%.3f\t%s' % (h/c, o/c, name))
        if verbose > 1:
            print()
    if quest > 0:
        print('Totals: Clusters %d   Questions %d   Accuracy %.3f   OPP %.3f'
              % (clust, quest, hits/quest, opp/quest))
    else:
        print('Nothing to evaluate!')
