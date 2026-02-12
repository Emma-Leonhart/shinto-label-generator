import re
import unicodedata
from itertools import product

# ----------------------------
# Kana → Romaji (minimal, unambiguous)
# ----------------------------

KANA_ROMAJI = {
    # vowels
    "あ": "a", "い": "i", "う": "u", "え": "e", "お": "o",

    # k
    "か": "ka", "き": "ki", "く": "ku", "け": "ke", "こ": "ko",
    "きゃ": "kya", "きゅ": "kyu", "きょ": "kyo",

    # s
    "さ": "sa", "し": "shi", "す": "su", "せ": "se", "そ": "so",
    "しゃ": "sha", "しゅ": "shu", "しょ": "sho",

    # t
    "た": "ta", "ち": "chi", "つ": "tsu", "て": "te", "と": "to",
    "ちゃ": "cha", "ちゅ": "chu", "ちょ": "cho",

    # n
    "な": "na", "に": "ni", "ぬ": "nu", "ね": "ne", "の": "no",
    "にゃ": "nya", "にゅ": "nyu", "にょ": "nyo",

    # h
    "は": "ha", "ひ": "hi", "ふ": "fu", "へ": "he", "ほ": "ho",
    "ひゃ": "hya", "ひゅ": "hyu", "ひょ": "hyo",

    # m
    "ま": "ma", "み": "mi", "む": "mu", "め": "me", "も": "mo",
    "みゃ": "mya", "みゅ": "myu", "みょ": "myo",

    # y
    "や": "ya", "ゆ": "yu", "よ": "yo",

    # r
    "ら": "ra", "り": "ri", "る": "ru", "れ": "re", "ろ": "ro",
    "りゃ": "rya", "りゅ": "ryu", "りょ": "ryo",

    # w
    "わ": "wa", "を": "wo",

    # n
    "ん": "n",

    # voiced (collapsed)
    "が": "ga", "ぎ": "gi", "ぐ": "gu", "げ": "ge", "ご": "go",
    "ぎゃ": "gya", "ぎゅ": "gyu", "ぎょ": "gyo",

    "ざ": "za", "じ": "ji", "ず": "su", "ぜ": "ze", "ぞ": "zo",
    "じゃ": "ja", "じゅ": "ju", "じょ": "jo",

    "だ": "da", "ぢ": "ji", "づ": "tu", "で": "de", "ど": "do",
    "ぢゃ": "ja", "ぢゅ": "ju", "ぢょ": "jo",

    "ば": "ba", "び": "bi", "ぶ": "bu", "べ": "be", "ぼ": "bo",
    "びゃ": "bya", "びゅ": "byu", "びょ": "byo",

    "ぱ": "pa", "ぴ": "pi", "ぷ": "pu", "ぺ": "pe", "ぽ": "po",
    "ぴゃ": "pya", "ぴゅ": "pyu", "ぴょ": "pyo",
}

# ----------------------------
# Romaji → Toki Pona core
# ----------------------------

BASE_MAP = {
    "a": "a", "i": "i", "u": "u", "e": "e", "o": "o",

    "ka": "ka", "ki": "ki", "ku": "ku", "ke": "ke", "ko": "ko",
    "sa": "sa", "shi": "si", "su": "su", "se": "se", "so": "so",
    "ta": "ta", "chi": "si", "tsu": "tu", "tu": "tu", "te": "te", "to": "to",
    "na": "na", "ni": "ni", "nu": "nu", "ne": "ne", "no": "no",
    "ma": "ma", "mi": "mi", "mu": "mu", "me": "me", "mo": "mo",
    "ya": "ja", "yu": "ju", "yo": "jo",
    "ra": "la", "ri": "li", "ru": "lu", "re": "le", "ro": "lo",
    "wa": "wa", "wo": "wo",
    "n": "n",

    # Voiced consonants (mapped to their unvoiced Toki Pona equivalents)
    "ga": "ka", "gi": "ki", "gu": "ku", "ge": "ke", "go": "ko",
    "za": "sa", "ji": "si", "zu": "su", "ze": "se", "zo": "so",
    "da": "ta", "di": "si", "du": "tu", "de": "te", "do": "to",
    "ba": "pa", "bi": "pi", "bu": "pu", "be": "pe", "bo": "po",

    # H-consonants (will be processed positionally: word-initial→k, elsewhere→p)
    "ha": "ha", "hi": "hi", "hu": "pu", "fu": "pu", "he": "he", "ho": "ho",
}

YOON_MAP = {
    "kya": "kija", "kyu": "kiju", "kyo": "kijo",
    "sha": "sija", "shu": "siju", "sho": "sijo",
    "cha": "teja", "chu": "teju", "cho": "tejo",
    "nya": "na",   "nyu": "niyu", "nyo": "no",
    "hya": "kija", "hyu": "kiju", "hyo": "kijo",
    "mya": "mija", "myu": "miju", "myo": "mijo",
    "rya": "liya", "ryu": "liyu", "ryo": "liyo",
    "gya": "kija", "gyu": "kiju", "gyo": "kijo",
    "ja":  "sija", "ju": "siju", "jo": "sijo",
    "bya": "pija", "byu": "piju", "byo": "pijo",
    "pya": "pija", "pyu": "piju", "pyo": "pijo",
    "dya": "teja", "dyu": "teju", "dyo": "tejo",
}

DIPTHONGS = {
    "aa": "a", "ai": "a", "au": "a", "ae": "awe", "ao": "o",
    "ia": "ija", "ii": "i", "iu": "iju", "ie": "ije", "io": "ijo",
    "ua": "uwa", "ui": "uwi", "uu": "u", "ue": "uwe", "uo": "o",
    "ea": "e", "ei": "e", "eu": "e", "ee": "e", "eo": "e",
    "oa": "owa", "oi": "owi", "ou": "o", "oe": "owe", "oo": "o",
}

# ----------------------------
# Core logic
# ----------------------------

def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.lower()
    text = re.sub(r"[^\w]", "", text)
    return text

def katakana_to_hiragana(text: str) -> str:
    """Convert katakana characters to hiragana (offset of 0x60)."""
    result = []
    for char in text:
        code = ord(char)
        # Katakana range: U+30A0 to U+30FF, Hiragana: U+3040 to U+309F
        if 0x30A1 <= code <= 0x30F6:
            result.append(chr(code - 0x60))
        else:
            result.append(char)
    return "".join(result)

def kana_to_romaji(text: str) -> str:
    text = katakana_to_hiragana(text)
    out = ""
    i = 0
    while i < len(text):
        if text[i:i+2] in KANA_ROMAJI:
            out += KANA_ROMAJI[text[i:i+2]]
            i += 2
        elif text[i] in KANA_ROMAJI:
            out += KANA_ROMAJI[text[i]]
            i += 1
        else:
            out += text[i]
            i += 1
    return out

def apply_dipthongs(text: str) -> str:
    for k, v in DIPTHONGS.items():
        text = text.replace(k, v)
    return text

def tokenize_romaji(text: str):
    tokens = []
    i = 0
    while i < len(text):
        for size in (3, 2, 1):
            chunk = text[i:i+size]
            if chunk in YOON_MAP or chunk in BASE_MAP:
                tokens.append(chunk)
                i += size
                break
        else:
            i += 1
    return tokens

def apply_h_position(syllables: list) -> list:
    """Apply positional h→k/p rule: word-initial h→k, elsewhere h→p."""
    result = []
    for i, syl in enumerate(syllables):
        if syl.startswith("h"):
            if i == 0:
                # Word-initial: h → k
                syl = "k" + syl[1:]
            else:
                # Elsewhere: h → p
                syl = "p" + syl[1:]
        result.append(syl)
    return result

def tokiponize(text: str):
    text = normalize(text)
    text = kana_to_romaji(text)
    text = apply_dipthongs(text)

    tokens = tokenize_romaji(text)

    syllables = []
    for t in tokens:
        if t in YOON_MAP:
            syllables.append(YOON_MAP[t])
        elif t in BASE_MAP:
            syllables.append(BASE_MAP[t])

    # Apply positional h→k/p rule
    syllables = apply_h_position(syllables)

    word = "".join(syllables)
    word = word.capitalize()

    return [word] if word else []

# ----------------------------
# Example
# ----------------------------

if __name__ == "__main__":
    print(tokiponize("Hachiman"))
    print(tokiponize("じづ"))
    print(tokiponize("トヨタマヒメ"))