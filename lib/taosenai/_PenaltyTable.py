# -*- coding: utf-8 -*-

import os
import itertools
import gzip
import sys
import pickle

import pywrapfst as fst

class PenaltyTable:
    def __init__(self, indir=None):
        if indir is None:
            vowels = set(["a", "i", "u", "e", "o"])
            semi_vowels = set(["a", "i", "u", "e", "o", "y", "N"])
            symfile = os.path.dirname(__file__) + "/../model/phoneme.txt"
            self.fst_penalty = fst.Fst()
            s = self.fst_penalty.add_state()
            self.fst_penalty.set_start(s)
            self.fst_penalty.set_final(s)

            # シンボル（音素）読み込み
            with open(symfile, "r") as fsym:
                symbols = dict((x.rstrip(), i) for i, x in enumerate(fsym, 2))
                symbols[None] = 0 # Epsilon
            self.syms = symbols

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
                        self.fst_penalty.add_arc(s, fst.Arc(symbols[p], symbols[q], fst.Weight(self.fst_penalty.weight_type(), dist), s))

            self.fst_penalty.arcsort(sort_type="olabel")
        else:
            self.fst_penalty = fst.Fst.read(indir + "/fst")
            with open(indir + "/syms", "rb") as fr:
                self.syms = pickle.load(fr)

    def write(self, outdir):
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        self.fst_penalty.write(outdir + "/fst")
        with open(outdir + "/syms", "wb") as fw:
            pickle.dump(self.syms, fw)
