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

ALPHABET_MAP = {
    "A":"エー","B":"ビー","C":"シー","D":"ディー","E":"イー",
    "F":"エフ","G":"ジー","H":"エイチ","I":"アイ","J":"ジェー",
    "K":"ケー","L":"エル","M":"エム","N":"エヌ","O":"オー",
    "P":"ピー","Q":"キュー","R":"アール","S":"エス","T":"ティー",
    "U":"ユー","V":"ブイ","W":"ダブリュー","X":"エックス",
    "Y":"ワイ","Z":"ゼット",
    "a":"エー","b":"ビー","c":"シー","d":"ディー","e":"イー",
    "f":"エフ","g":"ジー","h":"エイチ","i":"アイ","j":"ジェー",
    "k":"ケー","l":"エル","m":"エム","n":"エヌ","o":"オー",
    "p":"ピー","q":"キュー","r":"アール","s":"エス","t":"ティー",
    "u":"ユー","v":"ブイ","w":"ダブリュー","x":"エックス",
    "y":"ワイ","z":"ゼット",
}

def replace_alphabet(text):
    return "".join(ALPHABET_MAP.get(ch, ch) for ch in text)

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

    i = 0

    while i < len(word):

        if i + 1 < len(word) and word[i + 1] in small_map:
            vowels.append(small_map[word[i + 1]])
            i += 2

        else:
            vowels.append(vowel_map.get(word[i], ""))
            i += 1

    return vowels


# ===========================
# Step3
# ふつう：途中の「う」を消す
# やわめ：途中の「う」「い」を消す
# ===========================


# ===========================
# 新仕様用関数
# ===========================

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

def preprocess_word(word):

    word = replace_alphabet(word)
    reading = kanafy(word)

    return reading

def compress_duplicate_vowels(seq):

    while True:

        changed = False

        i = 0

        while i < len(seq):

            j = i + 1

            while (
                j < len(seq)
                and seq[j] == seq[i]
            ):
                j += 1

            run_length = j - i

            target = (
                1 if run_length == 2
                else 2 if run_length >= 3
                else run_length
            )

            if run_length > target:

                candidate = (
                    seq[:i]
                    + seq[i+1:]
                )

                if len(candidate) < 4:
                    return seq, True

                seq = candidate
                changed = True
                break

            i = j

        if not changed:
            return seq, False

def extract_from_reading(
    reading,
    rule=2,
    use_step12=True
):

    word = apply_step0(reading)

    seq = apply_step1(word)

    if rule == 0:

        seq, stop = compress_duplicate_vowels(seq)

    else:

        seq, stop = remove_duplicates_with_last_rollback(seq)
    if stop:
        return "".join(remove_non_vowels(seq))

    vowels = remove_non_vowels(seq)

    if rule != 0:

        vowels, stop = (
            remove_duplicates_with_last_rollback(
                vowels
            )
        )

        if stop:
            return "".join(vowels)

    if rule >= 2:
        vowels, stop = remove_middle_vowel_from_left(vowels, "う")
        if stop:
            return "".join(vowels)

    if rule >= 3:
        vowels, stop = remove_middle_vowel_from_left(vowels, "い")
        if stop:
            return "".join(vowels)

    if rule != 0:

        vowels, stop = (
            remove_duplicates_with_last_rollback(
                vowels
            )
        )

        if stop:
            return "".join(vowels)

    if rule != 0 and use_step12:

        vowels, stop = compress_pair_repeat(vowels)

    return "".join(vowels)

def extract(
    word,
    rule=2,
    use_step12=True
):

    reading = preprocess_word(word)

    return extract_from_reading(
        reading,
        rule,
        use_step12
    )

# ===========================
# 母音検索用
# ④→⑥のみ
# ===========================

def extract_vowel_search(word):

    word = preprocess_word(word)

    seq = apply_step1(word)

    vowels = remove_non_vowels(seq)

    return "".join(vowels)


# ===========================
# words.txt
# ===========================

folder = os.path.dirname(os.path.abspath(__file__))
word_file = os.path.join(folder, "words.txt")

def build_dict(rule, use_step12):

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

            reading = preprocess_word(word)

            reading_len = len(reading)

            vowel = extract_from_reading(
                reading,
                rule,
                use_step12
            )

            if vowel not in new_dict:
                new_dict[vowel] = []

            new_dict[vowel].append(
                (word, reading_len)
            )

            new_count += 1

    for key in new_dict:
        new_dict[key].sort(key=lambda x: x[1])

    return new_dict, new_count


# ===========================
# GUI
# ===========================

import streamlit as st

st.set_page_config(page_title="母音検索システム", layout="wide")

st.title("母音検索システム")

rule_names = {
    "ばりかた": 0,
    "かため": 1,
    "ふつう": 2,
    "やわめ": 3,
}

rule_label = st.radio(
    "変換ルール",
    list(rule_names.keys()),
    horizontal=True,
    index=1
)

rule = rule_names[rule_label]

if rule == 0:
    use_step12 = False
else:
    use_step12 = st.checkbox(
        "⑫を適用する",
        value=True
    )

rule = rule_names[rule_label]
search_mode = st.radio(
    "検索方法",
    ["単語で検索", "母音で検索"],
    horizontal=True,
)

@st.cache_data
def load_dictionary(
    rule,
    use_step12
):
    return build_dict(
        rule,
        use_step12
    )

vowel_dict, count = load_dictionary(
    rule,
    use_step12
)

st.caption(f"登録単語数: {count:,}")

query = st.text_input("検索語")

if query:

    if search_mode == "単語で検索":
        key = extract(
            query,
            rule,
            use_step12
        )
    else:
        key = extract_vowel_search(query)

    results = vowel_dict.get(key, [])

    st.write("検索キー:", key)
    st.write("一致件数:", len(results))

    if results:

        result_text = "\n".join(
            word for word, _ in results
        )

        st.code(
            result_text,
            language=None
        )

    else:
        st.info("一致する単語はありません。")

with st.expander("変換テスト"):
    t = st.text_input("テスト文字列", key="test")
    if t:
        st.write("かな:", kanafy(t))
        st.write(
            "単語検索キー:",
            extract(
                t,
                rule,
                use_step12
            )
        )
        st.write("母音検索キー:", extract_vowel_search(t))
