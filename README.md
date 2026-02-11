# Japanese-Tokiponizer

Converts Japanese names (Hepburn romanization, Nihon-shiki, Hiragana, Katakana) into Toki Pona phonology, following a custom phonological mapping system designed to preserve Japanese etymological distinctions (Yotsugana, H→K/P positional rules, etc.)

Currently used to generate Toki Pona labels for Shinto shrines sourced from Wikidata.

## Files

- `tokiponizer.py` — Core conversion library. Takes Japanese text in any script and produces Toki Pona-compatible name(s). Returns multiple variants when `zu` ambiguity exists.
- `fetch_shrines_tokiponize.py` — SPARQL pipeline that fetches all Shinto shrines with Indonesian labels from Wikidata, strips bracket content, detects `Kuil`/`Kuil Agung` prefix, tokiponizes the shrine name, and outputs `tomo sewi NAME` / `tomo sewi suli NAME` labels.
- `shrines_tokiponized.csv` — Output data: ~25,000 Shinto shrines with their Toki Pona labels.

## Usage

```bash
# Run the full pipeline (fetches from Wikidata, outputs CSV)
python fetch_shrines_tokiponize.py

# Use the tokiponizer directly
python -c "from tokiponizer import tokiponize; print(tokiponize('Hachiman'))"
```

## Phonological Rules

- Voiced consonants are devoiced (g→k, z→s, d→t, b→p)
- `zu` is ambiguous (could be す or づ), so both `su` and `tu` variants are output
- Initial H → K, medial H → P
- Long vowels collapse to short
- Diphthongs follow a fixed mapping table
- `r` → `l`, `chi` → `si`, `tsu` → `tu`
- Output is always capitalized with no spaces
