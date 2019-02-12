#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import sys
import os
import codecs
import taosenai

class TaosenaiPlayingImpl(taosenai.TaosenaiPlaying):
    penalty_table = taosenai.PenaltyTable()
    def __init__(self, vocab_input):
        taosenai.TaosenaiPlaying.__init__(self, self.penalty_table, vocab_input)

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
