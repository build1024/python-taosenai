# -*- coding: utf-8 -*-

import pywrapfst as fst
import _tophones
from _Vocabulary import Vocabulary

class TaosenaiPlaying:
    def __init__(self, penalty, vocab_list):
        self.penalty = penalty
        self.symbols = penalty.syms
        self.symbols_rev = dict((j, i) for (i, j) in self.symbols.iteritems())
        self.symbols_rev[1] = u"|"
        self.vocab = Vocabulary(self.symbols, vocab_list)

    def play(self, kana):
        ret = []
        input_phones = []
        phones = _tophones.tophones(kana, autopron=False)
        flag_done = False
        while not flag_done and len(phones) > 0:
            # 歌詞WFST
            fst_kashi = fst.Fst()
            new_st = fst_kashi.add_state()
            fst_kashi.set_start(new_st)
            for ph in phones:
                old_st = new_st
                new_st = fst_kashi.add_state()
                fst_kashi.add_arc(old_st, fst.Arc(self.symbols[ph], self.symbols[ph], fst.Weight.One(fst_kashi.weight_type()), new_st))
            fst_kashi.set_final(new_st)
            fst_kashi.arcsort(sort_type="olabel")

            # 歌詞への当てはめ方を検索
            fst_search = fst.compose(fst.compose(fst_kashi, self.penalty.fst_penalty), self.vocab.fst_vocab)
            fst_shortest = fst.shortestpath(fst_search, nshortest=1)
            #self._show(fst_shortest)

            # 検索結果を単語列に変換
            fst_shortest.rmepsilon()
            state = fst_shortest.start()

            # 対応結果を1音素ずつ読み込む
            symbuf = []
            while True:
                arcs = list(fst_shortest.arcs(state))
                if len(arcs) == 0:
                    # final state
                    break
                arc = arcs[0]
                if arc.olabel == 0: # Epsilon
                    pass
                elif arc.olabel == 1: # Delimiter:
                    # 単語境界が来たら、単語に変換
                    t = tuple(symbuf)
                    # 優先順位で並べる
                    selected_idx, selected_entry = \
                        sorted(enumerate(self.vocab.phonemes2vocab[t]),
                               key=lambda entry: self.key_func(entry[1].info))[0]
                    # 確定した単語を返す
                    self.selected(selected_entry)
                    ret.append(selected_entry)
                    input_phones += list(t)
                    symbuf = []
                else:
                    # 記号を蓄積する
                    sym = self.symbols_rev[arc.olabel]
                    symbuf.append(sym)

                # 次の記号へ
                state = arc.nextstate
            if fst_shortest.final(state) != fst.Weight.Zero(fst_shortest.weight_type()):
                flag_done = True

        # スコアを計算しておく
        """
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
        """
        weight_total = 0
        return (ret, weight_total)

    def key_func(self, info):
        # デフォルトでは登録順に返すのみ
        return 0

    def selected(self, info):
        # 選んだものを知らせるがデフォルトでは何もしない
        pass

    def _show(self, fstobj):
        # shortestpath() を呼んだ後のFSTの入出力を表示
        state = fstobj.start()
        while True:
            arcs = list(fstobj.arcs(state))
            if len(arcs) == 0:
                # final state
                break
            arc = arcs[0]
            if arc.ilabel != 0 or arc.olabel != 0:
                isym = self.symbols_rev[arc.ilabel]
                osym = self.symbols_rev[arc.olabel]
                print "{0}\t{1}".format(isym, osym)
            state = arc.nextstate
