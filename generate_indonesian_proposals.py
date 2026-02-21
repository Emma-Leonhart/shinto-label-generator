"""
Generate proposed Indonesian labels for Japanese-only shrines/temples.
1. Query Wikidata for items with 'ja' label but NO 'id' label.
2. Fetch 'ja' label and optional Kana reading (P1814/P5461).
3. Convert to Romaji (Hepburn) using pykakasi (or Kana reading if available).
4. Format as "Kuil [Name]" (Shrine) or "Wihara [Name]" (Temple).
5. Output to 'proposed_indonesian_labels.csv' and 'quickstatements/id_proposed.txt'.
"""

import os
import sys
import csv
import re
import requests
import pykakasi

# Initialize pykakasi (v2.3.0 API)
kks = pykakasi.kakasi()
# No setMode needed for basic conversion in v2+

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"

# Queries split by type to avoid timeouts
SPARQL_SHRINES = """
SELECT DISTINCT ?item ?jaLabel ?kanaName ?kanaReading WHERE {
  ?item wdt:P31/wdt:P279* wd:Q845945 .
  ?item rdfs:label ?jaLabel . FILTER(LANG(?jaLabel) = "ja")
  FILTER NOT EXISTS { ?item rdfs:label ?idLabel . FILTER(LANG(?idLabel) = "id") }
  OPTIONAL { ?item wdt:P1814 ?kanaName . }
  OPTIONAL { ?item wdt:P5461 ?kanaReading . }
}
"""

SPARQL_TEMPLES = """
SELECT DISTINCT ?item ?jaLabel ?kanaName ?kanaReading WHERE {
  ?item wdt:P31 wd:Q5393308 .
  ?item wdt:P17 wd:Q17 .
  ?item rdfs:label ?jaLabel . FILTER(LANG(?jaLabel) = "ja")
  FILTER NOT EXISTS { ?item rdfs:label ?idLabel . FILTER(LANG(?idLabel) = "id") }
  OPTIONAL { ?item wdt:P1814 ?kanaName . }
  OPTIONAL { ?item wdt:P5461 ?kanaReading . }
}
"""

def fetch_candidates():
    results = []
    
    # Fetch Shrines
    print("Querying Wikidata for Japanese-only Shrines...")
    try:
        r = requests.get(
            SPARQL_ENDPOINT,
            params={"query": SPARQL_SHRINES, "format": "json"},
            headers={"User-Agent": "Japanese-Tokiponizer/1.0 (Indonesian proposal pipeline)"},
            timeout=300,
        )
        r.raise_for_status()
        data = r.json()
        bindings = data["results"]["bindings"]
        print(f"Got {len(bindings)} shrines.")
        for b in bindings:
            b["type"] = {"value": "shrine"} # Add type manually
            results.append(b)
    except Exception as e:
        print(f"Error fetching shrines: {e}")

    # Fetch Temples
    print("Querying Wikidata for Japanese-only Temples...")
    try:
        r = requests.get(
            SPARQL_ENDPOINT,
            params={"query": SPARQL_TEMPLES, "format": "json"},
            headers={"User-Agent": "Japanese-Tokiponizer/1.0 (Indonesian proposal pipeline)"},
            timeout=300,
        )
        r.raise_for_status()
        data = r.json()
        bindings = data["results"]["bindings"]
        print(f"Got {len(bindings)} temples.")
        for b in bindings:
            b["type"] = {"value": "temple"} # Add type manually
            results.append(b)
    except Exception as e:
        print(f"Error fetching temples: {e}")
        
    return results

def to_romaji(text):
    """Convert Japanese text (Kanji/Kana) to Hepburn Romaji."""
    # Clean text (remove parens etc)
    cleaned = re.sub(r'\(.*?\)', '', text).strip()
    cleaned = re.sub(r'（.*?）', '', cleaned).strip()
    
    result = kks.convert(cleaned)
    # result is a list of dicts with keys like 'orig', 'hira', 'kana', 'hepburn', 'kunrei', 'passport'
    
    romaji_parts = [item['hepburn'] for item in result]
    # Join with space for readability
    name = " ".join(romaji_parts).title()
    
    # Strip common Japanese shrine/temple suffixes to avoid redundancy in "Kuil [Name]"
    # e.g. "Meiji Jingu" -> "Meiji", "Senso Ji" -> "Senso"
    suffixes = [
        " Jinja", " Jingu", " Taisha", " Tenmangu", " Gu", 
        " Ji", " Tera", " Dera", " In", " An"
    ]
    for suffix in suffixes:
        if name.endswith(suffix):
            name = name[:-len(suffix)].strip()
            break
            
    return name

def generate_label(romaji, item_type):
    """Generate Indonesian label: Kuil [Name] or Wihara [Name]."""
    prefix = "Kuil" if item_type == "shrine" else "Wihara"
    return f"{prefix} {romaji}"

def main():
    results = fetch_candidates()
    
    proposals = []
    
    print("Processing items...")
    for binding in results:
        qid = binding["item"]["value"].split("/")[-1]
        ja_label = binding["jaLabel"]["value"]
        kana_name = binding.get("kanaName", {}).get("value")
        kana_reading = binding.get("kanaReading", {}).get("value")
        item_type = binding["type"]["value"]
        
        # Prioritize kana sources for conversion
        source_text = kana_name if kana_name else (kana_reading if kana_reading else ja_label)
        
        try:
            romaji = to_romaji(source_text)
            
            # Simple cleanup for Indonesian style (optional)
            # Remove macrons if pykakasi produces them (Hepburn usually does).
            romaji = romaji.replace("ā", "a").replace("ī", "i").replace("ū", "u").replace("ē", "e").replace("ō", "o")
            
            label = generate_label(romaji, item_type)
            
            proposals.append({
                "qid": qid,
                "ja_label": ja_label,
                "romaji": romaji,
                "type": item_type,
                "proposed_label": label
            })
        except Exception as e:
            print(f"Error processing {qid} ({ja_label}): {e}")
            continue
        
    # Write CSV
    csv_file = "proposed_indonesian_labels.csv"
    with open(csv_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["qid", "ja_label", "romaji", "type", "proposed_label"])
        writer.writeheader()
        writer.writerows(proposals)
    print(f"Wrote {len(proposals)} proposals to {csv_file}")
    
    # Write QuickStatements
    qs_dir = "quickstatements"
    os.makedirs(qs_dir, exist_ok=True)
    qs_file = os.path.join(qs_dir, "id_proposed.txt")
    with open(qs_file, "w", encoding="utf-8", newline="\n") as f:
        for p in proposals:
            lbl = p["proposed_label"].replace('"', '""')
            f.write(f'{p["qid"]}\tLid\t"{lbl}"\n')
    print(f"Wrote QuickStatements to {qs_file}")

if __name__ == "__main__":
    main()
