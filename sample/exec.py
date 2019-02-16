#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import sys
import codecs
import itertools
PY3 = sys.version_info[0] == 3
if PY3:
    import pickle
else:
    import cPickle as pickle

import taosenai

class PenaltyTableImpl(taosenai.PenaltyTable):
    vowels = set([u"a", u"i", u"u", u"e", u"o"])
    semi_vowels = set([u"a", u"i", u"u", u"e", u"o", u"y", u"N"])
    penalty_table = {}

    # 音素間の類似度を定義する
    for t in itertools.combinations_with_replacement(taosenai.PenaltyTable.symbols.keys(), 2):
        if t[0] is None and t[1] is None:
            continue
        for p, q in [(t[0], t[1]), (t[1], t[0])]:
            dist = (0.0 if p == q else 1.0)
            # 母音が合わない場合はペナルティを増やす
            if (p in semi_vowels or q in semi_vowels) and (p != q):
                dist *= 5.0
            # 母音抜かしを認めない
            if not (p in vowels and q == None):
                penalty_table[(p, q)] = dist

    @classmethod
    def sim(cls, p, q):
        return PenaltyTableImpl.penalty_table.get((p, q), None)

class TaosenaiPlayingImpl(taosenai.TaosenaiPlaying):
    def __init__(self, vocab_input):
        ws_penalty = 4.0
        taosenai.TaosenaiPlaying.__init__(self, PenaltyTableImpl(), vocab_input, ws_penalty)

def main():
    # 単語読み込み
    with codecs.open("vocab_municipalities.txt", "r", "UTF-8") as fr:
        vocab_all = [(lambda x: (x[0], (x[1], x[2])))(l.strip().split()) for l in fr]
    taosenai_playing = TaosenaiPlayingImpl(vocab_all)

    # 元の歌詞
    with codecs.open("input.txt", "r", "UTF-8") as fr:
        lyrics = [text.strip() for text in fr]

    with codecs.open("output.txt", "w", "UTF-8") as fw:
        for i, text in enumerate(lyrics, 1):
            # 歌詞作成
            result, weight_total = taosenai_playing.play(text)
            # 結果表示
            print(u"[{0}] {1}".format(i, text))
            print(u"".join([u"{0:15s}{1}\n".format(r.kana, u" ".join(r.info)) for r in result]))
            print(u"[{0}] {1}".format(i, text), file=fw)
            print(u"".join([u"{0:15s}{1}\n".format(r.kana, u" ".join(r.info)) for r in result]), file=fw)

if __name__ == "__main__":
    main()
