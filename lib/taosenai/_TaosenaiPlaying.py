# -*- coding: utf-8 -*-

import collections
import fst
import _tophones
from _Vocabulary import Vocabulary

# Python 2.6+
ResultTuple = collections.namedtuple("ResultTuple", ["info"])
class TaosenaiPlaying:
    def __init__(self, penalty, vocab_list):
        self.penalty = penalty
        self.vocab = Vocabulary(penalty.fst_penalty.osyms, vocab_list)

    def play(self, kana):
        ret = []
        input_phones = []
        phones = _tophones.tophones(kana, autopron=False)
        flag_done = False
        while not flag_done and len(phones) > 0:
            # 歌詞WFST
            fst_kashi = fst.linear_chain(phones, self.penalty.fst_penalty.isyms)
            # 歌詞への当てはめ方を検索
            fst_search = (fst_kashi >> self.penalty.fst_penalty) >> self.vocab.fst_vocab
            fst_shortest = fst_search.shortest_path(1)

            # 検索結果を単語列に変換
            fst_shortest.remove_epsilon()
            state = fst_shortest[fst_shortest.start]

            # 対応結果を1音素ずつ読み込む
            symbuf = []
            while not state.final:
                arc = list(state.arcs)[0]
                sym = self.vocab.fst_vocab.osyms.find(arc.olabel)
                if sym == fst.EPSILON:
                    pass
                elif sym == Vocabulary.delimiter:
                    # 単語境界が来たら、単語に変換
                    t = tuple(symbuf)
                    # 優先順位で並べる
                    selected_idx, selected_entry = \
                        sorted(enumerate(self.vocab.phonemes2vocab[t]),
                               key=lambda entry: self.key_func(entry[1].info))[0]
                    # 確定した単語を返す
                    self.selected(selected_entry.info)
                    ret.append(ResultTuple(info=selected_entry.info))
                    input_phones += list(t)
                    symbuf = []
                else:
                    # 記号を蓄積する
                    symbuf.append(sym)

                # 次の記号へ
                state = fst_shortest[arc.nextstate]
            if state.final:
                flag_done = True

        # スコアを計算しておく
        fst_mapped_stations = fst.linear_chain(input_phones, self.penalty.fst_penalty.osyms)
        fst_score = (fst_kashi >> self.penalty.fst_penalty) >> fst_mapped_stations
        fst_score = fst_score.shortest_path(1)
        state = fst_score[fst_score.start]
        weight_total = 0.0
        while not state.final:
            arc = list(state.arcs)[0]
            weight_total += float(arc.weight)
            state = fst_score[arc.nextstate]

        # 単語境界ペナルティを加算
        weight_total += len(ret) * Vocabulary.ws_penalty
        return (ret, weight_total)

    def key_func(self, info):
        # デフォルトでは登録順に返すのみ
        return 0

    def selected(self, info):
        # 選んだものを知らせるがデフォルトでは何もしない
        pass

    def _show(self, fstobj):
        # shortest_path(1) を呼んだ後のFSTの入出力を表示
        state = fstobj[fstobj.start]
        while not state.final:
            arc = list(state.arcs)[0]
            isym = self.vocab.fst_vocab.isyms.find(arc.ilabel)
            osym = self.vocab.fst_vocab.osyms.find(arc.olabel)
            if isym != fst.EPSILON or osym != fst.EPSILON:
                print isym, osym
            state = fstobj[arc.nextstate]            
