# -*- coding: utf-8 -*-

import collections
import itertools
import sys

from . import pywrapfst as fst
from . import _tophones

PY3 = sys.version_info[0] == 3

VocabTuple = collections.namedtuple("VocabTuple", ["kana", "info"])
class Vocabulary:
    delimiter = "|"
    ws_penalty = 4.0

    def __init__(self, syms, vocab_list):
        self.syms = dict(syms)
        self.syms[self.delimiter] = 1

        # 単語登録
        self.phonemes2vocab = collections.defaultdict(list)
        for kana, info in vocab_list:
            # 1列目に読み
            phonemes = _tophones.tophones(kana)
            t = tuple(phonemes)
            # 付加情報込みで管理
            self.phonemes2vocab[t].append(VocabTuple(kana, info))

        # FST作成
        self.generate()

    # FST初期化
    def init_fst_vocab(self):
        self.fst_vocab = fst.Fst()
        s = self.fst_vocab.add_state()
        self.fst_vocab.set_start(s)
        self.fst_vocab.set_final(s)

    # FSTに単語（音素列）を追加する
    def insert_word(self, syms, state_from, state_to):
        new_st = self.fst_vocab.add_state()
        self.fst_vocab.add_arc(state_from, fst.Arc(0, 0, fst.Weight.One(self.fst_vocab.weight_type()), new_st))
        for s in syms:
            old_st = new_st
            new_st = self.fst_vocab.add_state()
            self.fst_vocab.add_arc(old_st, fst.Arc(self.syms[s], self.syms[s], fst.Weight.One(self.fst_vocab.weight_type()), new_st))
        self.fst_vocab.add_arc(new_st, fst.Arc(0, self.syms[self.delimiter], fst.Weight(self.fst_vocab.weight_type(), self.ws_penalty), state_to))

    # FSTの最適化
    def optimize(self):
        self.fst_vocab = fst.determinize(self.fst_vocab)
        self.fst_vocab.minimize()

    def generate(self):
        # FST作成
        self.init_fst_vocab()
        for phonemes, lst in (self.phonemes2vocab.items() if PY3 else self.phonemes2vocab.iteritems()):
            # 枝を追加する
            self.insert_word(phonemes, 0, 0)
        self.optimize()
