# Japanese-Tokiponizer

## Project Context
Converts Japanese names to Toki Pona phonology. Used to generate Toki Pona labels for Shinto shrines from Wikidata.

## Key Files
- `tokiponizer.py` — Core phonological mapper (Japanese → Toki Pona)
- `fetch_shrines_tokiponize.py` — SPARQL pipeline: Wikidata → Indonesian labels → strip/clean → tokiponize → CSV
- `shrines_tokiponized.csv` — Output data (~25k shrines)

## Workflow Guidelines
- **Commit early and often.** Every meaningful change should be committed.
- **Use `python` not `python3`** on this Windows system.
- Data files (CSV) are tracked in git intentionally.

## Architecture
- `tokiponize(text)` returns a list of variants (multiple when `zu` ambiguity exists)
- Indonesian labels: "Kuil X" → "tomo sewi X", "Kuil Agung X" → "tomo sewi suli X"
- Bracket content stripped, spaces/dashes removed, decapitalized before conversion
