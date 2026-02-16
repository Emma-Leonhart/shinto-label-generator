"""
Generate Korean (ko) labels for Shinto shrines and Buddhist temples.

Two paths:
- Japan shrines (P17=Q17): Indonesian label → strip prefix → koreanize → append Korean suffix
- Non-Japan shrines: Japanese label (kanji) → hanja.translate() for sino-Korean reading

Fallback: if a Japan shrine has no Indonesian label, use hanja path on Japanese label.

Output: quickstatements/ko.txt
"""

import os
import sys
import io
import re
import requests
import hanja
from koreanizer import koreanize
from fetch_shrines_tokiponize import process_label

# Windows UTF-8 console fix
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"

SPARQL_QUERY = """
SELECT DISTINCT ?item ?jaLabel ?idLabel ?country WHERE {
  {
    ?item wdt:P31/wdt:P279* wd:Q845945 .
  }
  UNION
  {
    ?item wdt:P31 wd:Q5393308 .
    ?item wdt:P17 wd:Q17 .
  }
  OPTIONAL { ?item rdfs:label ?jaLabel . FILTER(LANG(?jaLabel) = "ja") }
  OPTIONAL { ?item rdfs:label ?idLabel . FILTER(LANG(?idLabel) = "id") }
  OPTIONAL { ?item wdt:P17 ?country . }
  FILTER NOT EXISTS { ?item rdfs:label ?koLabel . FILTER(LANG(?koLabel) = "ko") }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
ORDER BY ?item
"""

# Indonesian prefix → Korean suffix mapping
KOREAN_SUFFIX = {
    "Kuil":        "신사",      # shrine
    "Kuil Agung":  "신궁",      # grand shrine
    "Wihara":      "사원",      # temple
    "Wihara Agung": "대사원",   # grand temple
}


def fetch_shrines():
    """Fetch shrines missing Korean labels from Wikidata."""
    print("Querying Wikidata for shrines without Korean labels...")
    r = requests.get(
        SPARQL_ENDPOINT,
        params={"query": SPARQL_QUERY, "format": "json"},
        headers={"User-Agent": "Japanese-Tokiponizer/1.0 (Korean label pipeline)"},
        timeout=120,
    )
    r.raise_for_status()
    data = r.json()
    results = data["results"]["bindings"]
    print(f"Got {len(results)} results from Wikidata.")
    return results


def japanese_to_korean_hanja(ja_label):
    """Convert a Japanese kanji label to Korean using sino-Korean readings.

    Uses the hanja library to get Korean readings of CJK characters.
    Kana characters are transliterated via koreanize().
    """
    if not ja_label:
        return None

    # Split the label into kanji segments and kana segments
    # Process kanji via hanja, kana via koreanize
    result_parts = []
    current_kana = []
    current_kanji = []

    for char in ja_label:
        if '\u3040' <= char <= '\u309F' or '\u30A0' <= char <= '\u30FF':
            # Hiragana or Katakana
            if current_kanji:
                kanji_str = "".join(current_kanji)
                translated = hanja.translate(kanji_str, "substitution")
                result_parts.append(translated)
                current_kanji = []
            current_kana.append(char)
        elif '\u4E00' <= char <= '\u9FFF' or '\u3400' <= char <= '\u4DBF':
            # CJK Unified Ideograph
            if current_kana:
                kana_str = "".join(current_kana)
                result_parts.append(koreanize(kana_str))
                current_kana = []
            current_kanji.append(char)
        else:
            # Other characters (spaces, punctuation) — flush both
            if current_kanji:
                kanji_str = "".join(current_kanji)
                translated = hanja.translate(kanji_str, "substitution")
                result_parts.append(translated)
                current_kanji = []
            if current_kana:
                kana_str = "".join(current_kana)
                result_parts.append(koreanize(kana_str))
                current_kana = []

    # Flush remaining
    if current_kanji:
        kanji_str = "".join(current_kanji)
        translated = hanja.translate(kanji_str, "substitution")
        result_parts.append(translated)
    if current_kana:
        kana_str = "".join(current_kana)
        result_parts.append(koreanize(kana_str))

    result = "".join(result_parts)
    # If hanja couldn't translate (returned original kanji), return None
    if any('\u4E00' <= c <= '\u9FFF' or '\u3400' <= c <= '\u4DBF' for c in result):
        return None
    return result if result else None


def make_korean_label_japan(id_label, ja_label):
    """Build Korean label for a Japan-based shrine using Indonesian label.

    Returns Korean label string or None.
    """
    if not id_label:
        # Fallback: use hanja on Japanese label
        if ja_label:
            return japanese_to_korean_hanja(ja_label)
        return None

    processed = process_label("id", id_label)
    if processed is None:
        # Indonesian label didn't match known prefix — try hanja fallback
        if ja_label:
            return japanese_to_korean_hanja(ja_label)
        return None

    prefix, cleaned_name = processed
    suffix = KOREAN_SUFFIX.get(prefix, "신사")

    # Koreanize the shrine name
    korean_name = koreanize(cleaned_name)
    if not korean_name:
        return None

    return f"{korean_name} {suffix}"


def make_korean_label_nonjapan(ja_label):
    """Build Korean label for a non-Japan shrine using hanja readings."""
    return japanese_to_korean_hanja(ja_label)


def main():
    results = fetch_shrines()

    # Deduplicate by QID (keep first occurrence)
    seen = set()
    deduped = []
    for binding in results:
        qid = binding["item"]["value"].split("/")[-1]
        if qid not in seen:
            seen.add(qid)
            deduped.append(binding)
    print(f"After dedup: {len(deduped)} unique shrines without Korean labels")

    rows = []
    skipped = 0

    for binding in deduped:
        qid = binding["item"]["value"].split("/")[-1]
        ja_label = binding.get("jaLabel", {}).get("value", "")
        id_label = binding.get("idLabel", {}).get("value", "")
        country = binding.get("country", {}).get("value", "")
        is_japan = country.endswith("/Q17") if country else False

        if is_japan:
            ko_label = make_korean_label_japan(id_label, ja_label)
        else:
            ko_label = make_korean_label_nonjapan(ja_label)

        if ko_label:
            rows.append({"qid": qid, "ko_label": ko_label})
        else:
            skipped += 1

    # Write QuickStatements
    outdir = "quickstatements"
    os.makedirs(outdir, exist_ok=True)
    filepath = os.path.join(outdir, "ko.txt")
    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            label = row["ko_label"].replace('"', '""')
            f.write(f'{row["qid"]}\tLko\t"{label}"\n')

    print(f"\nDone! Wrote {len(rows)} Korean QuickStatements to {filepath}")
    print(f"Skipped {skipped} items (no translatable label)")

    # Sample output
    print("\n--- Sample output ---")
    for row in rows[:20]:
        print(f"  {row['qid']:12s} | {row['ko_label']}")


if __name__ == "__main__":
    main()
