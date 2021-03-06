# -*- coding: utf-8 -*-

import os
import itertools
import gzip
import sys

PY3 = sys.version_info[0] == 3
if PY3:
    import pickle
else:
    import cPickle as pickle

from . import pywrapfst as fst

class PenaltyTable:
    def __init__(self, fname=None):
        if fname is None:
            vowels = set(["a", "i", "u", "e", "o"])
            semi_vowels = set(["a", "i", "u", "e", "o", "y", "N"])
            symbols = dict((x, i) for i, x in enumerate([
                'a', 'i', 'u', 'e', 'o', 'k', 'ky', 's', 'sh', 't', 'ts', 'ch',
                'n', 'ny', 'h', 'hy', 'f', 'm', 'my', 'y', 'r', 'ry', 'w', 'g',
                'gy', 'z', 'j', 'd', 'b', 'by', 'p', 'py', 'N', 'q', 'sp'
            ], 2))
            symbols[None] = 0 # reserved for Epsilon
            self.syms = symbols
            self.penalty_table = {}

            # 音素間の類似度を求める, KL Divergence
            for t in itertools.combinations_with_replacement(symbols.keys(), 2):
                if t[0] is None or t[1] is None:
                    continue
                for p, q in [(t[0], t[1]), (t[1], t[0])]:
                    dist = (0.0 if p == q else 1.0)
                    if p == "sp": p = None
                    if q == "sp": q = None
                    # 母音が合わない場合はペナルティを増やす
                    if (p in semi_vowels or q in semi_vowels) and (p != q):
                        dist *= 5.0
                    # 母音抜かしを認めない
                    if not (p in vowels and q == None):
                        self.penalty_table[(symbols[p], symbols[q])] = dist
        else:
            with open(fname, "rb") as fr:
                self.penalty_table = pickle.load(fr)
                self.syms = pickle.load(fr)
        self.generate_fst()

    def write(self, fname):
        with open(fname, "wb") as fw:
            pickle.dump(self.penalty_table, fw, pickle.HIGHEST_PROTOCOL)
            pickle.dump(self.syms, fw, pickle.HIGHEST_PROTOCOL)

    def generate_fst(self):
        self.fst_penalty = fst.Fst()
        s = self.fst_penalty.add_state()
        self.fst_penalty.set_start(s)
        self.fst_penalty.set_final(s)
        for (p, q), dist in (self.penalty_table.items() if PY3 else self.penalty_table.iteritems()):
            self.fst_penalty.add_arc(s, fst.Arc(p, q, fst.Weight(self.fst_penalty.weight_type(), dist), s))
        self.fst_penalty.arcsort(sort_type="olabel")
