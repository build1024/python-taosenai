#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
import os
import itertools
import collections
import operator
import time

sys.path.append("../lib")
sys.path.append("../local/lib/python2.7/site-packages")
os.environ["PATH"] = os.environ.get("PATH", "") + ":../local/bin" # for cygwin
import taosenai

class TaosenaiPlayingImpl(taosenai.TaosenaiPlaying):
    # 置換ペナルティテーブル
    if os.path.exists("modeldir") and set(os.listdir("modeldir")) >= set(["fst", "syms"]):
       penalty_table = taosenai.PenaltyTable("modeldir")
    else:
        # キャッシュがないときは、作りなおす
        penalty_table = taosenai.PenaltyTable()
        penalty_table.write("modeldir")

    def __init__(self, vocab_input):
        taosenai.TaosenaiPlaying.__init__(self, self.penalty_table, vocab_input)

StationRecord = collections.namedtuple("StationRecord", ["index", "surf", "yomi", "place", "line"])

def main():
    # 単語読み込み
    vocab_all = [(lambda i, x: (x[0], StationRecord(i, x[1], x[2], x[3], " ".join(x[4:]))))(i, l.strip().split(None))
                   for i, l in enumerate(open("vocab20190101_ext.txt", "r"))]
    pref_set = set([x[1].place[0:6] for x in vocab_all])
    taosenai_playing = TaosenaiPlayingImpl(vocab_all)

    # 元の歌詞
    lyrics = [text.strip() for text in open("input.txt", "r")]

    with open("output.txt", "w") as fw:
        for i, text in enumerate(lyrics, 1):
            # 歌詞作成
            result, weight_total = taosenai_playing.play(text)
            # 結果表示
            print "[{0}] {1}".format(i, text)
            print "".join([" ".join(r.info[1:]) + "\n" for r in result])
            print >>fw, "[{0}] {1}".format(i, text)
            print >>fw, "".join([" ".join(r.info[1:]) + "\n" for r in result])

if __name__ == "__main__":
    main()
