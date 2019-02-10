# -*- coding: utf-8 -*-

import sys

# 対応表
katakana2hiragana = {
        u'ア':u'あ', u'イ':u'い', u'ウ':u'う', u'エ':u'え', u'オ':u'お',
        u'カ':u'か', u'キ':u'き', u'ク':u'く', u'ケ':u'け', u'コ':u'こ',
        u'サ':u'さ', u'シ':u'し', u'ス':u'す', u'セ':u'せ', u'ソ':u'そ',
        u'タ':u'た', u'チ':u'ち', u'ツ':u'つ', u'テ':u'て', u'ト':u'と',
        u'ナ':u'な', u'ニ':u'に', u'ヌ':u'ぬ', u'ネ':u'ね', u'ノ':u'の',
        u'ハ':u'は', u'ヒ':u'ひ', u'フ':u'ふ', u'ヘ':u'へ', u'ホ':u'ほ',
        u'マ':u'ま', u'ミ':u'み', u'ム':u'む', u'メ':u'め', u'モ':u'も',
        u'ヤ':u'や', u'ユ':u'ゆ', u'ヨ':u'よ', u'ラ':u'ら', u'リ':u'り',
        u'ル':u'る', u'レ':u'れ', u'ロ':u'ろ', u'ワ':u'わ', u'ヲ':u'を',
        u'ン':u'ん',
        
        u'ガ':u'が', u'ギ':u'ぎ', u'グ':u'ぐ', u'ゲ':u'げ', u'ゴ':u'ご',
        u'ザ':u'ざ', u'ジ':u'じ', u'ズ':u'ず', u'ゼ':u'ぜ', u'ゾ':u'ぞ',
        u'ダ':u'だ', u'ヂ':u'ぢ', u'ヅ':u'づ', u'デ':u'で', u'ド':u'ど',
        u'バ':u'ば', u'ビ':u'び', u'ブ':u'ぶ', u'ベ':u'べ', u'ボ':u'ぼ',
        u'パ':u'ぱ', u'ピ':u'ぴ', u'プ':u'ぷ', u'ペ':u'ぺ', u'ポ':u'ぽ',
        
        u'ァ':u'ぁ', u'ィ':u'ぃ', u'ゥ':u'ぅ', u'ェ':u'ぇ', u'ォ':u'ぉ',
        u'ャ':u'ゃ', u'ュ':u'ゅ', u'ョ':u'ょ', u'ッ':u'っ'
      }

# 対応表
dic = {u"ア": "a"  , u"イ": "i"  , u"ウ": "u"  , u"エ": "e"  , u"オ": "o"  ,
       u"カ": "k a", u"キ": "k i", u"ク": "k u", u"ケ": "k e", u"コ": "k o",
       u"ガ": "g a", u"ギ": "g i", u"グ": "g u", u"ゲ": "g e", u"ゴ": "g o",
       u"サ": "s a", u"シ": "sh i",u"ス": "s u", u"セ": "s e", u"ソ": "s o",
       u"ザ": "z a", u"ジ": "j i", u"ズ": "z u", u"ゼ": "z e", u"ゾ": "z o",
       u"タ": "t a", u"チ": "ch i",u"ツ": "ts u",u"テ": "t e", u"ト": "t o",
       u"ダ": "d a", u"ヂ": "j i", u"ヅ": "z u", u"デ": "d e", u"ド": "d o",
       u"ナ": "n a", u"ニ": "n i", u"ヌ": "n u", u"ネ": "n e", u"ノ": "n o",
       u"ハ": "h a", u"ヒ": "h i", u"フ": "f u", u"ヘ": "h e", u"ホ": "h o",
       u"バ": "b a", u"ビ": "b i", u"ブ": "b u", u"ベ": "b e", u"ボ": "b o",
       u"パ": "p a", u"ピ": "p i", u"プ": "p u", u"ペ": "p e", u"ポ": "p o",
       u"マ": "m a", u"ミ": "m i", u"ム": "m u", u"メ": "m e", u"モ": "m o",
       u"ヤ": "y a", u"ユ": "y u", u"ヨ": "y o",
       u"ラ": "r a", u"リ": "r i", u"ル": "r u", u"レ": "r e", u"ロ": "r o",
       u"ワ": "w a", u"ヲ": "o",   u"ン": "N",
       u"ッ": "q"}

hiragana2katakana = {}
for k, h in katakana2hiragana.iteritems():
    hiragana2katakana[h] = k
       
# 読みから音素列への変換
def tophones(s, autopron=True):
    beg = True
    phones = []

    # 変換
    for ch in s:
        # ひらがな→カタカナ変換
        if ch in hiragana2katakana:
            ch = hiragana2katakana[ch]
            
        if (not beg) and ch == u"ー":
            # 母音の後にしか付けない
            if len(phones) > 0:
                if phones[-1][-1] in ["a", "i", "u", "e", "o"]:
                    phones.append(phones[-1][-1])
            beg = False
        elif ch == u"ャ":
            if len(phones) <= 1:
                phones += ["y", "a"]
            else:
                if (phones[-2][-1] != "h" and phones[-2] != "j" and phones[-2] != "d") or phones[-2] == "h":
                    phones[-2] += "y"
                phones[-1] = "a"
            beg = False
        elif ch == u"ュ":
            if len(phones) <= 1:
                phones += ["y", "u"]
            else:
                if (phones[-2][-1] != "h" and phones[-2] != "j" and phones[-2] != "t" and phones[-2] != "d") or phones[-2] == "h":
                    phones[-2] += "y"
                phones[-1] = "u"
            beg = False
        elif ch == u"ョ":
            if len(phones) <= 1:
                phones += ["y", "o"]
            else:
                if (phones[-2][-1] != "h" and phones[-2] != "j" and phones[-2] != "d") or phones[-2] == "h":
                    phones[-2] += "y"
                phones[-1] = "o"
            beg = False
        elif ch == u"ァ":
            if len(phones) == 0:
                phones.append("a")
            else:
                phones[-1] = "a"
            beg = False
        elif ch == u"ィ":
            if len(phones) == 0:
                phones.append("i")
            else:
                phones[-1] = "i"
            beg = False
        elif ch == u"ゥ":
            if len(phones) == 0:
                phones.append("u")
            else:
                phones[-1] = "u"
            beg = False
        elif ch == u"ェ":
            if len(phones) == 0:
                phones.append("e")
            else:
                phones[-1] = "e"
            beg = False
        elif ch == u"ォ":
            if len(phones) == 0:
                phones.append("o")
            else:
                phones[-1] = "o"
            beg = False
        elif (not beg) and ch == u"イ":
            # 二重母音の自動変換：「ケイセイウエノ」→「ケエセエウエノ」
            if autopron and (phones[-1][-1] in ["i", "e"]):
                phones.append(phones[-1][-1])
            else:
                phones += dic[ch].split(" ")
        elif (not beg) and ch == u"ウ":
            # 二重母音の自動変換：「トウキョウ」→「トオキョオ」
            if autopron and (phones[-1][-1] in ["u", "o"]):
                phones.append(phones[-1][-1])
            else:
                phones += dic[ch].split(" ")
        elif ch == u" ":
            beg = True
        else:
            if ch in dic:
                phones += dic[ch].split(" ")
                if beg:
                    beg = False
    return phones
