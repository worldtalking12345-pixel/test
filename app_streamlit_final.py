import os
import re

from fugashi import Tagger
from kanjize import number2kanji

tagger = Tagger()

def convert_numbers(text):

    def repl(m):
        try:
            return number2kanji(int(m.group()))
        except:
            return m.group()

    return re.sub(r"\d+", repl, text)


def kanafy(text):

    text = convert_numbers(text)

    text = text.replace("&", "アンド")
    text = text.replace("＆", "アンド")

    result = []

    for word in tagger(text):

        kana = None

        try:
            kana = word.feature.kana
        except:
            pass

        if not kana:
            try:
                kana = word.feature.kanaBase
            except:
                pass

        if kana:
            result.append(kana)
        else:
            result.append(word.surface)

    return "".join(result)


# ===========================
# Step0
# お段+う、え段+い を短縮
# ===========================

def apply_step0(word):

    word = word.replace("ー", "")
    word = word.replace("っ", "")
    word = word.replace("ッ", "")

    word = word.replace("ょう", "ょ")
    word = word.replace("ョウ", "ョ")

    # お段 + う
    for kana in [
        'こ', 'そ', 'と', 'の', 'ほ', 'も',
        'よ', 'ろ', 'を', 'ご', 'ぼ', 'ぽ',
        'ど', 'お'
    ]:
        word = word.replace(kana + "う", kana)

    for kana in [
        'コ', 'ソ', 'ト', 'ノ', 'ホ', 'モ',
        'ヨ', 'ロ', 'ヲ', 'ゴ', 'ボ', 'ポ',
        'ド', 'オ'
    ]:
        word = word.replace(kana + "ウ", kana)

    # え段 + い
    for kana in [
        'え',
        'け', 'せ', 'て', 'ね', 'へ', 'め', 'れ',
        'げ', 'ぜ', 'で', 'べ', 'ぺ'
    ]:
        word = word.replace(kana + "い", kana)

    for kana in [
        'エ',
        'ケ', 'セ', 'テ', 'ネ', 'ヘ', 'メ', 'レ',
        'ゲ', 'ゼ', 'デ', 'ベ', 'ペ'
    ]:
        word = word.replace(kana + "イ", kana)

    return word


# ===========================
# Step1 母音化
# ===========================

vowel_map = {
    'あ':'あ','い':'い','う':'う','え':'え','お':'お',

    'か':'あ','き':'い','く':'う','け':'え','こ':'お',
    'さ':'あ','し':'い','す':'う','せ':'え','そ':'お',
    'た':'あ','ち':'い','つ':'う','て':'え','と':'お',
    'な':'あ','に':'い','ぬ':'う','ね':'え','の':'お',
    'は':'あ','ひ':'い','ふ':'う','へ':'え','ほ':'お',
    'ま':'あ','み':'い','む':'う','め':'え','も':'お',

    'や':'あ','ゆ':'う','よ':'お',

    'ら':'あ','り':'い','る':'う','れ':'え','ろ':'お',

    'わ':'あ','を':'お',

    'が':'あ','ぎ':'い','ぐ':'う','げ':'え','ご':'お',
    'ざ':'あ','じ':'い','ず':'う','ぜ':'え','ぞ':'お',
    'だ':'あ','ぢ':'い','づ':'う','で':'え','ど':'お',
    'ば':'あ','び':'い','ぶ':'う','べ':'え','ぼ':'お',
    'ぱ':'あ','ぴ':'い','ぷ':'う','ぺ':'え','ぽ':'お',

    'ん':'ん',

    'ヴ':'う',
    'ゔ':'う',

    'ア':'あ','イ':'い','ウ':'う','エ':'え','オ':'お',

    'カ':'あ','キ':'い','ク':'う','ケ':'え','コ':'お',
    'サ':'あ','シ':'い','ス':'う','セ':'え','ソ':'お',
    'タ':'あ','チ':'い','ツ':'う','テ':'え','ト':'お',
    'ナ':'あ','ニ':'い','ヌ':'う','ネ':'え','ノ':'お',
    'ハ':'あ','ヒ':'い','フ':'う','ヘ':'え','ホ':'お',
    'マ':'あ','ミ':'い','ム':'う','メ':'え','モ':'お',

    'ヤ':'あ','ユ':'う','ヨ':'お',

    'ラ':'あ','リ':'い','ル':'う','レ':'え','ロ':'お',

    'ワ':'あ','ヲ':'お',

    'ガ':'あ','ギ':'い','グ':'う','ゲ':'え','ゴ':'お',
    'ザ':'あ','ジ':'い','ズ':'う','ゼ':'え','ゾ':'お',
    'ダ':'あ','ヂ':'い','ヅ':'う','デ':'え','ド':'お',
    'バ':'あ','ビ':'い','ブ':'う','ベ':'え','ボ':'お',
    'パ':'あ','ピ':'い','プ':'う','ペ':'え','ポ':'お'
}

small_map = {
    'ゃ':'あ',
    'ゅ':'う',
    'ょ':'お',

    'ャ':'あ',
    'ュ':'う',
    'ョ':'お',

    'ぁ':'あ',
    'ぃ':'い',
    'ぅ':'う',
    'ぇ':'え',
    'ぉ':'お',

    'ァ':'あ',
    'ィ':'い',
    'ゥ':'う',
    'ェ':'え',
    'ォ':'お'
}


def apply_step1(word):

    vowels = []
    positions = []

    i = 0

    while i < len(word):

        if i + 1 < len(word) and word[i + 1] in small_map:
            vowels.append(small_map[word[i + 1]])
            positions.append(i + 1)
            i += 2

        else:
            vowels.append(vowel_map.get(word[i], ""))
            positions.append(i)
            i += 1

    return vowels, positions


# ===========================
# Step3
# ふつう：途中の「う」を消す
# やわめ：途中の「う」「い」を消す
# ===========================


# ===========================
# 新仕様用関数
# ===========================

def compress_ei_ou(seq):
    result = []
    i = 0
    while i < len(seq):
        if i + 1 < len(seq) and seq[i] == "え" and seq[i + 1] == "い":
            result.append("え")
            i += 2
        elif i + 1 < len(seq) and seq[i] == "お" and seq[i + 1] == "う":
            result.append("お")
            i += 2
        else:
            result.append(seq[i])
            i += 1
    return result


def remove_duplicates_with_last_rollback(seq):

    while True:

        changed = False

        i = 0

        while i < len(seq) - 1:

            if seq[i] == seq[i + 1]:

                candidate = seq[:i + 1] + seq[i + 2:]

                if len(candidate) < 4:
                    return seq, True

                seq = candidate
                changed = True
                break

            i += 1

        if not changed:
            return seq, False


def remove_non_vowels(seq):
    return [x for x in seq if x in ["あ","い","う","え","お"]]


def remove_middle_vowel_from_left(vowels, target):
    while True:
        removed = False
        for i in range(1, len(vowels)-1):
            if vowels[i] == target:
                candidate = vowels[:i] + vowels[i+1:]
                if len(candidate) < 4:
                    return vowels, True
                vowels = candidate
                removed = True
                break
        if not removed:
            return vowels, False


def compress_pair_repeat(vowels):

    i = 0
    while i < len(vowels) - 3:

        found = False

        for size in range(2, (len(vowels) - i)//2 + 1):

            block = vowels[i:i+size]
            repeat = 1

            while vowels[i+repeat*size:i+(repeat+1)*size] == block:
                repeat += 1

            if repeat >= 2:

                keep = 1 if repeat == 2 else 2

                candidate = (
                    vowels[:i]
                    + block * keep
                    + vowels[i + repeat*size:]
                )

                if len(candidate) < 4:
                    return vowels, True

                vowels = candidate
                found = True
                break

        if not found:
            i += 1

    return vowels, False


# ===========================
# 母音抽出（新仕様）
# ===========================

def extract(word, rule=2):

    word = kanafy(word)

    word = apply_step0(word)

    seq, _ = apply_step1(word)

    # ② えい→え、おう→お
    seq = compress_ei_ou(seq)

    # ③ 3連続母音圧縮
    seq, stop = remove_duplicates_with_last_rollback(seq)
    if stop:
        return "".join(remove_non_vowels(seq))

    # ④ 母音以外削除
    vowels = remove_non_vowels(seq)

    # ⑤ 連続母音圧縮
    vowels, stop = remove_duplicates_with_last_rollback(vowels)
    if stop:
        return "".join(vowels)

    # ⑥
    if rule >= 2:
        vowels, stop = remove_middle_vowel_from_left(vowels, "う")
        if stop:
            return "".join(vowels)

    # ⑦
    if rule >= 3:
        vowels, stop = remove_middle_vowel_from_left(vowels, "い")
        if stop:
            return "".join(vowels)

    # ⑧
    vowels, stop = remove_duplicates_with_last_rollback(vowels)
    if stop:
        return "".join(vowels)

    # ⑨
    vowels, stop = compress_pair_repeat(vowels)

    return "".join(vowels)

# ===========================
# words.txt
# ===========================

folder = os.path.dirname(os.path.abspath(__file__))
word_file = os.path.join(folder, "words.txt")

current_rule = None
vowel_dict = {}
count = 0


def build_dict(rule):

    new_dict = {}
    used = set()
    new_count = 0

    with open(word_file, encoding="utf-8") as f:

        for line in f:

            word = line.strip()

            if not word:
                continue

            if word.startswith("#"):
                continue

            if word in used:
                continue

            used.add(word)

            vowel = extract(word, rule)

            if vowel not in new_dict:
                new_dict[vowel] = []

            new_dict[vowel].append(word)

            new_count += 1

    return new_dict, new_count


def rule_name(rule):

    if rule == 1:
        return "かため"

    if rule == 2:
        return "ふつう"

    if rule == 3:
        return "やわめ"

    return "不明"


def rebuild_if_needed():

    global current_rule
    global vowel_dict
    global count

    rule = rule_var.get()

    if current_rule == rule:
        return

    vowel_dict, count = build_dict(rule)
    current_rule = rule

    count_label.config(text=f"登録単語数 : {count}")
    rule_label.config(text=f"現在のルール : {rule_name(rule)}")


# ===========================
# 検索
# ===========================

def search(event=None):

    rebuild_if_needed()

    key = entry.get().strip()

    result_box.delete(0, tk.END)

    if not key:
        info_label.config(text="母音を入力してください")
        return

    if key in vowel_dict:

        words = sorted(vowel_dict[key])

        info_label.config(text=f"{len(words)}件ヒット")

        for w in words:
            result_box.insert(tk.END, w)

    else:

        info_label.config(text="0件ヒット")
        result_box.insert(tk.END, "該当なし")


def auto_search(event=None):
    search()


def change_rule():

    rebuild_if_needed()
    search()


# ===========================
# テスト表示
# ===========================

def show_test():

    rebuild_if_needed()

    samples = [
        "横行闊歩",
        "映画",
        "オールドファッション",
        "倍々ファイト",
        "あうあうおう"
    ]

    result_box.delete(0, tk.END)

    for word in samples:
        result_box.insert(
            tk.END,
            f"{word} → {extract(word, rule_var.get())}"
        )

    info_label.config(text="変換テストを表示しました")


# ===========================
# GUI
# ===========================



import pandas as pd
import streamlit as st

st.set_page_config(page_title="母音検索システム", layout="wide")

st.title("母音検索システム")

rule_names = {"かため": 1, "ふつう": 2, "やわめ": 3}

rule_label = st.radio(
    "変換ルール",
    list(rule_names.keys()),
    horizontal=True,
    index=1
)
rule = rule_names[rule_label]

@st.cache_data
def load_dictionary(rule):
    return build_dict(rule)

vowel_dict, count = load_dictionary(rule)

st.caption(f"登録単語数: {count:,}")

query = st.text_input("検索語")

if query:
    key = extract(query, rule)
    results = vowel_dict.get(key, [])

    st.write("母音キー:", key)
    st.write("一致件数:", len(results))

    if results:
        st.dataframe(
            pd.DataFrame({"単語": results}),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("一致する単語はありません。")

with st.expander("変換テスト"):
    t = st.text_input("テスト文字列", key="test")
    if t:
        st.write("かな:", kanafy(t))
        st.write("抽出:", extract(t, rule))
