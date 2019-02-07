# -*- coding: utf-8 -*-

import os
import itertools
import gzip
import sys

import fst

class PenaltyTable:
    def __init__(self, indir=None):
        if indir is None:
            vowels = set(["a", "i", "u", "e", "o"])
            semi_vowels = set(["a", "i", "u", "e", "o", "y", "N"])
            symfile = os.path.dirname(__file__) + "/../model/phoneme.txt"
            self.fst_penalty = fst.Transducer()

            # 音素間の類似度を求める, KL Divergence
            with open(symfile, "r") as fsym:
                for t in itertools.combinations_with_replacement(
                    itertools.imap(lambda x: x.strip(), fsym), 2):
                    for p, q in [(t[0], t[1]), (t[1], t[0])]:
                        dist = (0.0 if p == q else 1.0)
                        if p == "sp": p = fst.EPSILON
                        if q == "sp": q = fst.EPSILON
                        # 母音が合わない場合はペナルティを増やす
                        if (p in semi_vowels or q in semi_vowels) and (p != q):
                            dist *= 5.0
                        # 母音抜かしを認めない
                        if not (p in vowels and q == fst.EPSILON):
                            self.fst_penalty.add_arc(0, 0, p, q, dist)
                    
            self.fst_penalty[0].final = True
            #self.fst_penalty[1].final = True
            self.fst_penalty.arc_sort_output()
        else:
            self.fst_penalty = fst.read(indir + "/fst")
            self.fst_penalty.isyms = fst.read_symbols(indir + "/isyms")
            self.fst_penalty.osyms = fst.read_symbols(indir + "/osyms")

    def write(self, outdir):
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        self.fst_penalty.write(outdir + "/fst")
        self.fst_penalty.isyms.write(outdir + "/isyms")
        self.fst_penalty.osyms.write(outdir + "/osyms")
