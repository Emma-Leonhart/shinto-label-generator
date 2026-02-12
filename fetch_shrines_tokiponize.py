"""
Fetch Shinto shrines with Indonesian labels from Wikidata,
strip bracket content, remove Kuil/Kuil Agung prefix,
tokiponize the remaining Japanese name, and produce
tomo sewi [suli] NAME output.
"""

import re
import csv
import sys
import io
import requests
from tokiponizer import tokiponize

# Windows UTF-8 console fix
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"

SPARQL_QUERY = """
SELECT DISTINCT ?item ?itemLabel ?idLabel ?jaLabel WHERE {
  ?item wdt:P31/wdt:P279* wd:Q845945 .
  ?item rdfs:label ?idLabel . FILTER(LANG(?idLabel) = "id")
  FILTER NOT EXISTS { ?item rdfs:label ?tokLabel . FILTER(LANG(?tokLabel) = "tok") }
  OPTIONAL { ?item rdfs:label ?jaLabel . FILTER(LANG(?jaLabel) = "ja") }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
ORDER BY ?idLabel
"""

def fetch_shrines():
    """Fetch all Shinto shrines with Indonesian labels from Wikidata."""
    print("Querying Wikidata SPARQL for Shinto shrines with Indonesian labels...")
    r = requests.get(
        SPARQL_ENDPOINT,
        params={"query": SPARQL_QUERY, "format": "json"},
        headers={"User-Agent": "Japanese-Tokiponizer/1.0 (Shinto shrine label pipeline)"},
        timeout=120,
    )
    r.raise_for_status()
    data = r.json()
    results = data["results"]["bindings"]
    print(f"Got {len(results)} results from Wikidata.")
    return results

def process_label(id_label):
    """
    Process an Indonesian shrine label:
    1. Remove content in brackets (and the brackets themselves)
    2. Strip whitespace
    3. Detect prefix: 'Kuil Agung' or 'Kuil'
    4. Remove prefix
    5. Remove spaces and dashes
    6. Decapitalize
    Returns (prefix, cleaned_name) or None if no valid prefix found.
    """
    # Remove bracketed content: (stuff), [stuff], {stuff}
    cleaned = re.sub(r'\([^)]*\)', '', id_label)
    cleaned = re.sub(r'\[[^\]]*\]', '', cleaned)
    cleaned = re.sub(r'\{[^}]*\}', '', cleaned)
    cleaned = cleaned.strip()

    # Detect prefix
    if cleaned.startswith("Kuil Agung "):
        prefix = "Kuil Agung"
        name = cleaned[len("Kuil Agung "):]
    elif cleaned.startswith("Kuil "):
        prefix = "Kuil"
        name = cleaned[len("Kuil "):]
    else:
        # Not a Kuil-prefixed label, skip
        return None

    # Remove spaces and dashes, decapitalize
    name = name.replace(" ", "").replace("-", "")
    name = name.lower()

    return (prefix, name)

def make_tokipona_label(prefix, tokiponized_name):
    """Build the toki pona label: tomo sewi [suli] NAME"""
    if prefix == "Kuil Agung":
        return f"tomo sewi suli {tokiponized_name}"
    else:
        return f"tomo sewi {tokiponized_name}"

def main():
    results = fetch_shrines()

    # Deduplicate SPARQL results: keep first (qid, id_label) pair
    seen_qids = {}
    deduped = []
    for binding in results:
        qid = binding["item"]["value"].split("/")[-1]
        id_label = binding["idLabel"]["value"]
        key = (qid, id_label)
        if key not in seen_qids:
            seen_qids[key] = True
            deduped.append(binding)
    print(f"After dedup: {len(deduped)} unique (QID, id_label) pairs")

    rows = []
    seen_rows = set()
    skipped = 0

    for binding in deduped:
        qid = binding["item"]["value"].split("/")[-1]
        en_label = binding.get("itemLabel", {}).get("value", "")
        id_label = binding["idLabel"]["value"]
        ja_label = binding.get("jaLabel", {}).get("value", "")

        processed = process_label(id_label)
        if processed is None:
            skipped += 1
            continue

        prefix, cleaned_name = processed
        variants = tokiponize(cleaned_name)

        for variant in variants:
            row_key = (qid, variant)
            if row_key in seen_rows:
                continue
            seen_rows.add(row_key)
            tp_label = make_tokipona_label(prefix, variant)
            rows.append({
                "qid": qid,
                "en_label": en_label,
                "ja_label": ja_label,
                "id_label": id_label,
                "prefix": prefix,
                "cleaned_input": cleaned_name,
                "tokiponized": variant,
                "toki_pona_label": tp_label,
            })

    # Write CSV
    outfile = "shrines_tokiponized.csv"
    with open(outfile, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "qid", "en_label", "ja_label", "id_label",
            "prefix", "cleaned_input", "tokiponized", "toki_pona_label",
        ])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nDone! Wrote {len(rows)} rows to {outfile}")
    print(f"Skipped {skipped} entries (no Kuil/Kuil Agung prefix)")

    # Print first few for quick review
    print("\n--- Sample output ---")
    for row in rows[:20]:
        print(f"  {row['qid']:12s} | {row['id_label']:40s} -> {row['toki_pona_label']}")

if __name__ == "__main__":
    main()
