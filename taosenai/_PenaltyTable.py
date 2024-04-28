# -*- coding: utf-8 -*-

import sys
import itertools
import math

from . import pywrapfst as fst

PY3 = sys.version_info[0] == 3
if PY3:
    import pickle
else:
    import cPickle as pickle

class PenaltyTable:
    symbols = dict((x, i) for i, x in enumerate([
        'a', 'i', 'u', 'e', 'o', 'k', 'ky', 's', 'sh', 't', 'ts', 'ch',
        'n', 'ny', 'h', 'hy', 'f', 'm', 'my', 'y', 'r', 'ry', 'w', 'g',
        'gy', 'z', 'j', 'd', 'b', 'by', 'p', 'py', 'N', 'q'
    ], 2))
    symbols[None] = 0 # reserved for Epsilon

    def __init__(self):
        self.syms = PenaltyTable.symbols
        self.penalty_table = {}

        # 音素間の類似度を求める
        for t in itertools.product(self.syms.keys(), repeat=2):
            if not (t[0] is None and t[1] is None):
                dist = self.sim(t[0], t[1])
                if not (dist is None or math.isinf(dist)):
                    self.penalty_table[(self.syms[t[0]], self.syms[t[1]])] = dist
        self.generate_fst()

    # 入力音素p, 出力音素q間の非類似度（0以上の実数）を定義する。
    # オーバーライドして挙動を変更できる。
    # p, qが <eps> の場合は None が引数に渡される。
    # inf または None を返してもよい（p->qの変換は棄却される）
    @classmethod
    def sim(cls, p, q):
        # デフォルトで編集距離を返す。
        return (0.0 if p == q else 1.0)

    def generate_fst(self):
        self.fst_penalty = fst.VectorFst()
        s = self.fst_penalty.add_state()
        self.fst_penalty.set_start(s)
        self.fst_penalty.set_final(s)
        for (p, q), dist in (self.penalty_table.items() if PY3 else self.penalty_table.iteritems()):
            self.fst_penalty.add_arc(s, fst.Arc(p, q, fst.Weight(self.fst_penalty.weight_type(), dist), s))
        self.fst_penalty.arcsort(sort_type="olabel")
