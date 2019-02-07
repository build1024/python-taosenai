# -*- coding: utf-8 -*-

import collections
import itertools

import fst

import _tophones

# Python 2.6+
VocabTuple = collections.namedtuple("VocabTuple", ["kana", "info"])
class Vocabulary:
    delimiter = "|"
    ws_penalty = 4.0

    def __init__(self, syms, vocab_list):
        self.syms = syms

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
        self.fst_vocab = fst.Transducer(self.syms, self.syms)
        self.fst_vocab[0].final = True
        self.num_states = 1

    # FSTに単語（音素列）を追加する
    def insert_word(self, syms, state_from, state_to):
        self.fst_vocab.add_arc(state_from, self.num_states, fst.EPSILON, fst.EPSILON)
        self.num_states += 1
        for s in syms:
            self.fst_vocab.add_arc(self.num_states-1, self.num_states, s, s)
            self.num_states += 1
        self.fst_vocab.add_arc(self.num_states-1, state_to, fst.EPSILON, self.delimiter, self.ws_penalty)

    # FSTの最適化
    def optimize(self):
        self.fst_vocab = self.fst_vocab.determinize()
        self.fst_vocab.minimize()

    def generate(self):
        # FST作成
        self.init_fst_vocab()
        num_base = self.num_states

        for phonemes, lst in self.phonemes2vocab.iteritems():
            # 枝を追加する
            self.insert_word(phonemes, 0, 0)

        self.optimize()
