"""
Generate labels in multiple languages for Shinto shrines, all derived from
Indonesian (id) labels on Wikidata.

Languages handled:
  Simple suffix/prefix: tr, de, nl, es, it, eu
  Lithuanian (declension): lt
  Cyrillic (declension): ru, uk
  Farsi (Perso-Arabic script): fa

Output: quickstatements/{lang}.txt for each language
"""

import os
import sys
import io
import re
import unicodedata
import requests
from tokiponizer import kana_to_romaji, tokenize_romaji

# Windows UTF-8 console fix
if hasattr(sys.stdout, 'buffer') and not isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
elif hasattr(sys.stdout, 'encoding') and sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"

# ----------------------------
# Cyrillic maps (Polivanov system)
# ----------------------------

CYRILLIC_BASE = {
    "a": "а", "i": "и", "u": "у", "e": "э", "o": "о",
    "ka": "ка", "ki": "ки", "ku": "ку", "ke": "кэ", "ko": "ко",
    "sa": "са", "shi": "си", "su": "су", "se": "сэ", "so": "со",
    "ta": "та", "chi": "ти", "tsu": "цу", "tu": "цу", "te": "тэ", "to": "то",
    "na": "на", "ni": "ни", "nu": "ну", "ne": "нэ", "no": "но",
    "ha": "ха", "hi": "хи", "hu": "фу", "fu": "фу", "he": "хэ", "ho": "хо",
    "ma": "ма", "mi": "ми", "mu": "му", "me": "мэ", "mo": "мо",
    "ya": "я", "yu": "ю", "yo": "ё",
    "ra": "ра", "ri": "ри", "ru": "ру", "re": "рэ", "ro": "ро",
    "wa": "ва", "wi": "ви", "we": "вэ", "wo": "о",
    "n": "н",
    "ga": "га", "gi": "ги", "gu": "гу", "ge": "гэ", "go": "го",
    "za": "дза", "ji": "дзи", "zu": "дзу", "ze": "дзэ", "zo": "дзо",
    "da": "да", "di": "дзи", "du": "дзу", "de": "дэ", "do": "до",
    "ba": "ба", "bi": "би", "bu": "бу", "be": "бэ", "bo": "бо",
    "pa": "па", "pi": "пи", "pu": "пу", "pe": "пэ", "po": "по",
}

CYRILLIC_YOON = {
    "kya": "кя", "kyu": "кю", "kyo": "кё",
    "sha": "ся", "shu": "сю", "sho": "сё",
    "cha": "тя", "chu": "тю", "cho": "тё",
    "nya": "ня", "nyu": "ню", "nyo": "нё",
    "hya": "хя", "hyu": "хю", "hyo": "хё",
    "mya": "мя", "myu": "мю", "myo": "мё",
    "rya": "ря", "ryu": "рю", "ryo": "рё",
    "gya": "гя", "gyu": "гю", "gyo": "гё",
    "ja": "дзя", "ju": "дзю", "jo": "дзё",
    "bya": "бя", "byu": "бю", "byo": "бё",
    "pya": "пя", "pyu": "пю", "pyo": "пё",
    "dya": "дя", "dyu": "дю", "dyo": "дё",
}

# ----------------------------
# Farsi maps (Perso-Arabic script)
# ----------------------------

# Initial vowels need an alef carrier in Farsi
FARSI_INITIAL = {"a": "ا", "i": "ای", "u": "او", "e": "ای", "o": "او"}

FARSI_BASE = {
    "a": "ا", "i": "ی", "u": "و", "e": "ه", "o": "و",
    "ka": "کا", "ki": "کی", "ku": "کو", "ke": "که", "ko": "کو",
    "sa": "سا", "shi": "شی", "su": "سو", "se": "سه", "so": "سو",
    "ta": "تا", "chi": "چی", "tsu": "تسو", "tu": "تسو", "te": "ته", "to": "تو",
    "na": "نا", "ni": "نی", "nu": "نو", "ne": "نه", "no": "نو",
    "ha": "ها", "hi": "هی", "hu": "هو", "fu": "فو", "he": "هه", "ho": "هو",
    "ma": "ما", "mi": "می", "mu": "مو", "me": "مه", "mo": "مو",
    "ya": "یا", "yu": "یو", "yo": "یو",
    "ra": "را", "ri": "ری", "ru": "رو", "re": "ره", "ro": "رو",
    "wa": "وا", "wi": "وی", "we": "وه", "wo": "و",
    "n": "ن",
    "ga": "گا", "gi": "گی", "gu": "گو", "ge": "گه", "go": "گو",
    "za": "زا", "ji": "جی", "zu": "زو", "ze": "زه", "zo": "زو",
    "da": "دا", "di": "دی", "du": "دو", "de": "ده", "do": "دو",
    "ba": "با", "bi": "بی", "bu": "بو", "be": "به", "bo": "بو",
    "pa": "پا", "pi": "پی", "pu": "پو", "pe": "په", "po": "پو",
}

FARSI_YOON = {
    "kya": "کیا", "kyu": "کیو", "kyo": "کیو",
    "sha": "شا",  "shu": "شو",  "sho": "شو",
    "cha": "چا",  "chu": "چو",  "cho": "چو",
    "nya": "نیا", "nyu": "نیو", "nyo": "نیو",
    "hya": "هیا", "hyu": "هیو", "hyo": "هیو",
    "mya": "میا", "myu": "میو", "myo": "میو",
    "rya": "ریا", "ryu": "ریو", "ryo": "ریو",
    "gya": "گیا", "gyu": "گیو", "gyo": "گیو",
    "ja":  "جا",  "ju":  "جو",  "jo":  "جو",
    "bya": "بیا", "byu": "بیو", "byo": "بیو",
    "pya": "پیا", "pyu": "پیو", "pyo": "پیو",
    "dya": "دیا", "dyu": "دیو", "dyo": "دیو",
}


def _farsify_word(word):
    """Transliterate a single romanized Japanese word to Farsi script."""
    w = unicodedata.normalize("NFKC", word).lower()
    w = w.replace("ā", "a").replace("ī", "i").replace("ū", "u").replace("ē", "e").replace("ō", "o")
    w = re.sub(r"[^\w]", "", w)
    w = kana_to_romaji(w)
    tokens = tokenize_romaji(w)
    parts = []
    for idx, t in enumerate(tokens):
        if t in FARSI_YOON:
            parts.append(FARSI_YOON[t])
        elif t in FARSI_BASE:
            if idx == 0 and t in FARSI_INITIAL:
                parts.append(FARSI_INITIAL[t])
            else:
                parts.append(FARSI_BASE[t])
    return "".join(parts)


def farsify(name):
    """Convert a romanized Japanese name to Farsi script. Handles multi-word names."""
    words = name.split()
    farsi_words = [_farsify_word(w) for w in words if w]
    return " ".join(w for w in farsi_words if w)


# ----------------------------
# Name extraction
# ----------------------------

def extract_name(id_label):
    """Extract shrine name from Indonesian label, preserving original casing.
    Returns (name, is_grand) or None."""
    cleaned = re.sub(r'\([^)]*\)', '', id_label)
    cleaned = re.sub(r'\[[^\]]*\]', '', cleaned)
    cleaned = cleaned.strip()
    for prefix, is_grand in [("Kuil Agung ", True), ("Kuil ", False)]:
        if cleaned.startswith(prefix):
            name = cleaned[len(prefix):].strip()
            return (name, is_grand) if name else None
    return None

# ----------------------------
# Cyrillicization (Polivanov system)
# ----------------------------

def _cyrillicize_word(word):
    """Cyrillicize a single romanized Japanese word."""
    w = unicodedata.normalize("NFKC", word).lower()
    w = w.replace("ā", "a").replace("ī", "i").replace("ū", "u").replace("ē", "e").replace("ō", "o")
    w = re.sub(r"[^\w]", "", w)
    w = kana_to_romaji(w)
    tokens = tokenize_romaji(w)
    parts = []
    for t in tokens:
        if t in CYRILLIC_YOON:
            parts.append(CYRILLIC_YOON[t])
        elif t in CYRILLIC_BASE:
            parts.append(CYRILLIC_BASE[t])
    result = "".join(parts)
    return result.capitalize() if result else ""


def cyrillicize(name, lang="ru"):
    """Convert a romanized Japanese name to Cyrillic. Handles multi-word names."""
    words = name.split()
    cyrillic_words = [_cyrillicize_word(w) for w in words if w]
    result = " ".join(w for w in cyrillic_words if w)
    if lang == "uk":
        result = result.replace("э", "е").replace("и", "і")
    return result

# ----------------------------
# Lithuanian romanization
# ----------------------------

def lithuanize(name):
    """Apply Lithuanian phonological adjustments to a romanized Japanese name."""
    # ch → č (case-preserving)
    result = name.replace("Ch", "Č").replace("ch", "č")
    result = result.replace("Sh", "Š").replace("sh", "š")
    result = result.replace("W", "V").replace("w", "v")
    return result

# ----------------------------
# Declension functions
# ----------------------------

def _decline_word_lithuanian(word):
    """Apply Lithuanian genitive to the last word."""
    lower = word.lower()
    for ending, repl in [("an", "ano"), ("in", "ino"), ("un", "uno"),
                         ("en", "eno"), ("on", "ono")]:
        if lower.endswith(ending):
            return word[:-len(ending)] + repl
    for ending, repl in [("a", "os"), ("i", "io"), ("u", "us"),
                         ("e", "ės"), ("o", "o")]:
        if lower.endswith(ending):
            return word[:-len(ending)] + repl
    return word


def decline_lithuanian(name):
    words = name.split()
    if not words:
        return name
    words[-1] = _decline_word_lithuanian(words[-1])
    return " ".join(words)


def _decline_word_russian(word):
    for ending, repl in [("ан", "ана"), ("ин", "ина"), ("ун", "уна"),
                         ("эн", "эна"), ("он", "она")]:
        if word.endswith(ending):
            return word[:-len(ending)] + repl
    if word.endswith("а"):
        if len(word) >= 2 and word[-2] in "гкхжчшщ":
            return word[:-1] + "и"
        return word[:-1] + "ы"
    return word


def decline_russian(name):
    words = name.split()
    if not words:
        return name
    words[-1] = _decline_word_russian(words[-1])
    return " ".join(words)


def _decline_word_ukrainian(word):
    for ending, repl in [("ан", "ана"), ("ін", "іна"), ("ун", "уна"),
                         ("ен", "ена"), ("он", "она")]:
        if word.endswith(ending):
            return word[:-len(ending)] + repl
    if word.endswith("а"):
        return word[:-1] + "и"
    return word


def decline_ukrainian(name):
    words = name.split()
    if not words:
        return name
    words[-1] = _decline_word_ukrainian(words[-1])
    return " ".join(words)

# ----------------------------
# Label formatters per language
# ----------------------------

def format_label(lang, name, is_grand=False):
    """Format a shrine name into a target-language label."""
    if lang == "tr":
        return f"{name} Büyük Tapınağı" if is_grand else f"{name} Tapınağı"
    if lang == "de":
        return f"{name} Großschrein" if is_grand else f"{name} Schrein"
    if lang == "nl":
        return f"{name}-shrijn"   # no distinction
    if lang == "es":
        return f"Gran Santuario {name}" if is_grand else f"Santuario {name}"
    if lang == "it":
        return f"Grande Santuario {name}" if is_grand else f"Santuario {name}"
    if lang == "eu":
        return f"{name} santutegia nagusia" if is_grand else f"{name} santutegia"
    if lang == "lt":
        lt_name = lithuanize(name)
        lt_name = decline_lithuanian(lt_name)
        return f"{lt_name} maldykla"  # no distinction
    if lang == "ru":
        cy_name = cyrillicize(name, "ru")
        cy_name = decline_russian(cy_name)
        return f"Большой храм {cy_name}" if is_grand else f"Храм {cy_name}"
    if lang == "uk":
        cy_name = cyrillicize(name, "uk")
        cy_name = decline_ukrainian(cy_name)
        return f"Велике святилище {cy_name}" if is_grand else f"Святилище {cy_name}"
    if lang == "fa":
        fa_name = farsify(name)
        return f"معبد بزرگ {fa_name}" if is_grand else f"معبد {fa_name}"
    return None

# ----------------------------
# SPARQL
# ----------------------------

ALL_LANGS = ["tr", "de", "nl", "es", "it", "eu", "lt", "ru", "uk", "fa"]


def make_sparql(lang_code):
    return f"""
SELECT DISTINCT ?item ?idLabel WHERE {{
  {{
    ?item wdt:P31/wdt:P279* wd:Q845945 .
  }}
  UNION
  {{
    ?item wdt:P31 wd:Q5393308 .
    ?item wdt:P17 wd:Q17 .
  }}
  ?item rdfs:label ?idLabel . FILTER(LANG(?idLabel) = "id")
  FILTER NOT EXISTS {{ ?item rdfs:label ?existing . FILTER(LANG(?existing) = "{lang_code}") }}
}}
ORDER BY ?item
"""


def run_sparql(query, label):
    print(f"  Querying Wikidata: {label}...")
    r = requests.get(
        SPARQL_ENDPOINT,
        params={"query": query, "format": "json"},
        headers={"User-Agent": "Japanese-Tokiponizer/1.0 (multilang label pipeline)"},
        timeout=300,
    )
    r.raise_for_status()
    data = r.json()
    results = data["results"]["bindings"]
    print(f"  Got {len(results)} results.")
    return results

# ----------------------------
# Main
# ----------------------------

def main():
    outdir = "quickstatements"
    os.makedirs(outdir, exist_ok=True)

    for lang in ALL_LANGS:
        print(f"\n=== {lang.upper()} ===")
        results = run_sparql(make_sparql(lang), f"shrines missing {lang} label")

        # Deduplicate by QID
        seen = set()
        rows = []
        skipped = 0

        for binding in results:
            qid = binding["item"]["value"].split("/")[-1]
            if qid in seen:
                continue
            seen.add(qid)

            id_label = binding["idLabel"]["value"]
            extracted = extract_name(id_label)
            if not extracted:
                skipped += 1
                continue
            name, is_grand = extracted

            label = format_label(lang, name, is_grand)
            if label:
                rows.append({"qid": qid, "label": label})
            else:
                skipped += 1

        # Write QuickStatements
        filepath = os.path.join(outdir, f"{lang}.txt")
        with open(filepath, "w", encoding="utf-8", newline="\n") as f:
            for row in rows:
                escaped = row["label"].replace('"', '""')
                f.write(f'{row["qid"]}\tL{lang}\t"{escaped}"\n')

        print(f"  Wrote {len(rows)} to {filepath} (skipped {skipped})")

        # Sample
        for row in rows[:5]:
            print(f"    {row['qid']:12s} | {row['label']}")

    print("\nDone!")


if __name__ == "__main__":
    main()
