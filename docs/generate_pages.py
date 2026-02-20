"""
Generate GitHub Pages HTML for all QuickStatements languages.
Run from the repo root: python docs/generate_pages.py
Also called by the GitHub Actions regenerate workflow.
"""

import os
import html

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR  = os.path.join(REPO_ROOT, "docs")
QS_DIR    = os.path.join(REPO_ROOT, "quickstatements")

# (code, english name, native name, flag, methodology HTML)
LANGS = [
    ("tok", "Toki Pona", "Toki Pona", "🌍", """\
      <p>Fetches shrines and temples from Wikidata via SPARQL that have Indonesian labels
      but no Toki Pona label. The Indonesian label ("Kuil X" or "Kuil Agung X") is used
      to extract the proper name, which is then passed through a custom phonological mapper:</p>
      <ul>
        <li>Voiced consonants devoiced: g→k, z→s, d→t, b→p</li>
        <li>Initial H→K, medial H→P</li>
        <li>Long vowels collapsed to short; r→l; chi→si; tsu→tu</li>
        <li>The mora <em>zu</em> is ambiguous (す or づ) — both <em>su</em> and <em>tu</em> variants are emitted</li>
      </ul>
      <p>The label is prefixed with <strong>tomo sewi</strong> (shrine) or
      <strong>tomo sewi suli</strong> (grand shrine / Kuil Agung).</p>"""),

    ("ko", "Korean", "한국어", "🇰🇷", """\
      <p>Two paths depending on the shrine's country:</p>
      <ul>
        <li><strong>Japanese shrines:</strong> Indonesian label → strip prefix →
        <code>koreanize()</code> (maps Hepburn romanization to Hangul, preserving
        voiced/unvoiced distinctions; ん→ㄴ batchim) → append Korean suffix:
        신사 (jinja), 신궁 (jingū), 사원 (temple), 대사원 (grand temple).</li>
        <li><strong>Non-Japanese shrines:</strong> Japanese Kanji label →
        <code>hanja.translate()</code> for the sino-Korean reading.</li>
      </ul>"""),

    ("zh", "Chinese", "中文", "🇨🇳", """\
      <p>Takes the Japanese Kanji label and applies two transformations:</p>
      <ol>
        <li>Kana characters are replaced with man'yōgana-style Chinese equivalents
        (e.g. の→之, ヶ→个, ノ→乃).</li>
        <li>The result is passed through OpenCC's <strong>t2s</strong> converter to
        convert Japanese shinjitai (新字体) to simplified Chinese characters.</li>
      </ol>
      <p>Pure Kanji labels pass through with only the shinjitai→simplified step.</p>"""),

    ("de", "German", "Deutsch", "🇩🇪", """\
      <p>Fetches shrines missing a German label from Wikidata. Extracts the proper name
      from the Indonesian label (stripping "Kuil" / "Kuil Agung" prefix) and appends
      <strong>Schrein</strong>.</p>
      <p>Example: <em>Kuil Ise</em> → <em>Ise Schrein</em></p>"""),

    ("nl", "Dutch", "Nederlands", "🇳🇱", """\
      <p>Fetches shrines missing a Dutch label. Extracts the name from the Indonesian
      label and appends <strong>-shrijn</strong>.</p>
      <p>Example: <em>Kuil Ise</em> → <em>Ise-shrijn</em></p>"""),

    ("es", "Spanish", "Español", "🇪🇸", """\
      <p>Fetches shrines missing a Spanish label. Prepends
      <strong>Santuario</strong> to the extracted name.</p>
      <p>Example: <em>Kuil Ise</em> → <em>Santuario Ise</em></p>"""),

    ("it", "Italian", "Italiano", "🇮🇹", """\
      <p>Fetches shrines missing an Italian label. Prepends
      <strong>Santuario</strong> to the extracted name.</p>
      <p>Example: <em>Kuil Ise</em> → <em>Santuario Ise</em></p>"""),

    ("tr", "Turkish", "Türkçe", "🇹🇷", """\
      <p>Fetches shrines missing a Turkish label. Appends
      <strong>Tapınağı</strong> (shrine/temple) to the extracted name.</p>
      <p>Example: <em>Kuil Ise</em> → <em>Ise Tapınağı</em></p>"""),

    ("ru", "Russian", "Русский", "🇷🇺", """\
      <p>Fetches shrines missing a Russian label. The extracted name is transliterated
      to Cyrillic using the <strong>Polivanov system</strong> (the standard for
      Japanese→Russian in Russian linguistics). The final word of the name is then
      declined into the genitive case. Prefixed with <strong>Храм</strong> (temple/shrine).</p>
      <p>Example: <em>Kuil Ise</em> → <em>Храм Исэ</em></p>"""),

    ("uk", "Ukrainian", "Українська", "🇺🇦", """\
      <p>Fetches shrines missing a Ukrainian label. Uses the same Polivanov-based
      Cyrillic transliteration as Russian, with Ukrainian-specific substitutions
      (э→е, и→і). The final word is declined into the genitive case. Prefixed with
      <strong>Святилище</strong> (sanctuary).</p>
      <p>Example: <em>Kuil Ise</em> → <em>Святилище Ісе</em></p>"""),

    ("lt", "Lithuanian", "Lietuvių", "🇱🇹", """\
      <p>Fetches shrines missing a Lithuanian label. The name undergoes phonological
      adaptation (ch→č, sh→š, w→v) and the final word is declined into the genitive
      case using Lithuanian vowel-ending rules. The word <strong>maldykla</strong>
      (place of worship / shrine) is appended.</p>
      <p>Example: <em>Kuil Ise</em> → <em>Isės maldykla</em></p>"""),

    ("eu", "Basque", "Euskara", "🏔️", """\
      <p>Fetches shrines missing a Basque label. Appends
      <strong>santutegia</strong> (sanctuary) to the extracted name.</p>
      <p>Example: <em>Kuil Ise</em> → <em>Ise santutegia</em></p>"""),

    ("fa", "Farsi", "فارسی", "🇮🇷", """\
      <p>Fetches shrines missing a Farsi label. The extracted name is transliterated
      from romanized Japanese to Perso-Arabic script using a syllable-based mapping:</p>
      <ul>
        <li>Vowels at word-start take an alef carrier: <em>i</em> → ای, <em>u</em> → او</li>
        <li>Yōon syllables: <em>kyo</em> → کیو, <em>sha</em> → شا, <em>chi</em> → چی</li>
        <li>Voiced stops preserved: <em>ga</em> → گا, <em>ba</em> → با, <em>da</em> → دا</li>
        <li><em>tsu</em> → تسو, <em>fu</em> → فو, <em>ji</em> → جی</li>
      </ul>
      <p>Prefixed with <strong>معبد</strong> (shrine) or
      <strong>معبد بزرگ</strong> (grand shrine) for Kuil Agung.</p>
      <p>Example: <em>Kuil Hakone</em> → معبد هاکونه</p>"""),

    ("ar", "Arabic (MSA)", "العربية", "🇸🇦", """\
      <p>Fetches shrines missing an Arabic (MSA) label. The extracted name is transliterated
      from romanized Japanese to Arabic script using a syllable-based mapping.
      Key differences from the Farsi mapping:</p>
      <ul>
        <li>Initial vowels take a hamza carrier: <em>a</em> → أ, <em>i</em> → إي, <em>u</em> → أو</li>
        <li><em>g</em> → غ (ghain — Arabic has no گ): <em>ga</em> → غا, <em>gu</em> → غو</li>
        <li><em>ch</em> → تش (two letters — Arabic has no چ): <em>chi</em> → تشي</li>
        <li><em>p</em> → ب (Arabic has no پ): <em>pa</em> → با</li>
        <li>Mid-word <em>e</em> → ي (same as <em>i</em>, not ه as in Farsi)</li>
      </ul>
      <p>Prefixed with <strong>معبد</strong> (place of worship) or
      <strong>معبد … الكبير</strong> (grand shrine) for Kuil Agung.</p>
      <p>Example: <em>Kuil Hakone</em> → معبد هاكوني</p>"""),

    ("arz", "Egyptian Arabic", "مصري", "🇪🇬", """\
      <p>Identical to the MSA Arabic pipeline with one phonological difference:
      in Egyptian Arabic, ج is pronounced <em>/g/</em> (hard G), so Japanese <em>g</em>
      maps to ج rather than MSA's غ. The غ→ج substitution is applied after transliteration.</p>
      <ul>
        <li><em>ga</em> → جا, <em>gu</em> → جو, <em>gi</em> → جي (vs MSA غا, غو, غي)</li>
        <li>All other syllables identical to MSA Arabic</li>
      </ul>
      <p>Prefixed with <strong>معبد</strong> or <strong>معبد … الكبير</strong> for Kuil Agung.</p>
      <p>Example: <em>Kuil Kamigamo</em> → معبد كاميجامو (vs MSA كاميغامو)</p>"""),

    ("hi", "Hindi", "हिन्दी", "🇮🇳", """\
      <p>Fetches shrines missing a Hindi label. The extracted name is transliterated
      from romanized Japanese to Devanagari script using a syllable-based mapping:</p>
      <ul>
        <li>Vowels at word-start use independent Devanagari vowel letters:
        <em>a</em> → अ, <em>i</em> → इ, <em>u</em> → उ, <em>e</em> → ए, <em>o</em> → ओ</li>
        <li>Consonant syllables use inherent-vowel notation: <em>ka</em> → क, <em>ki</em> → कि,
        <em>ku</em> → कु, <em>ke</em> → के, <em>ko</em> → को</li>
        <li>Sibilants and affricates: <em>shi</em> → शि (श), <em>chi</em> → चि (च),
        <em>tsu</em> → त्सु, <em>fu</em> → फ़ु</li>
        <li>Voiced stops preserved: <em>ga</em> → ग, <em>ba</em> → ब, <em>da</em> → द</li>
        <li>Yōon syllables use consonant clusters: <em>kya</em> → क्य, <em>sha</em> → श,
        <em>ryu</em> → र्यु</li>
        <li>Moraic nasal ん → न</li>
      </ul>
      <p>Appended with <strong>मंदिर</strong> (shrine/temple) or
      <strong>महा मंदिर</strong> (grand shrine) for Kuil Agung.</p>
      <p>Example: <em>Kuil Ise</em> → <em>इसे मंदिर</em></p>"""),
]

PAGE_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{english} QuickStatements — Shrine Labels</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: system-ui, -apple-system, sans-serif;
      background: #0f1117; color: #e2e8f0;
      min-height: 100vh; padding: 2rem 1.5rem;
    }}
    .container {{ max-width: 860px; margin: 0 auto; }}
    .breadcrumb {{ font-size: 0.8rem; color: #475569; margin-bottom: 1.25rem; }}
    .breadcrumb a {{ color: #6366f1; text-decoration: none; }}
    .breadcrumb a:hover {{ text-decoration: underline; }}
    h1 {{ font-size: 1.4rem; color: #a5b4fc; margin-bottom: 0.3rem; }}
    .meta {{ font-size: 0.82rem; color: #475569; margin-bottom: 1.25rem; }}
    .copy-bar {{
      display: flex; align-items: center; gap: 1rem; margin-bottom: 0.6rem;
    }}
    .copy-btn {{
      background: #4f46e5; border: none; color: #fff; border-radius: 6px;
      padding: 0.45rem 1.2rem; font-size: 0.85rem; cursor: pointer;
      transition: background 0.15s;
    }}
    .copy-btn:hover {{ background: #4338ca; }}
    .copy-btn.copied {{ background: #16a34a; }}
    .qs-link {{ font-size: 0.82rem; color: #475569; text-decoration: none; }}
    .qs-link:hover {{ color: #a5b4fc; }}
    textarea {{
      width: 100%; height: 560px;
      background: #0a0c14; border: 1px solid #1e2130; border-radius: 8px;
      color: #cbd5e1;
      font-family: 'Cascadia Code', 'Fira Code', 'JetBrains Mono', monospace;
      font-size: 0.72rem; line-height: 1.55; padding: 0.75rem;
      resize: vertical; outline: none; margin-bottom: 1.5rem;
    }}
    textarea:focus {{ border-color: #4f46e5; }}
    details {{
      background: #13151f; border: 1px solid #1e2130; border-radius: 8px;
      padding: 0.9rem 1.1rem;
    }}
    summary {{
      font-size: 0.85rem; color: #c4b5fd; cursor: pointer;
      font-weight: 600; user-select: none;
    }}
    summary:hover {{ color: #a5b4fc; }}
    .method-body {{
      margin-top: 0.85rem;
      font-size: 0.83rem; color: #94a3b8; line-height: 1.7;
    }}
    .method-body p {{ margin-bottom: 0.6rem; }}
    .method-body ul, .method-body ol {{
      padding-left: 1.4rem; margin-bottom: 0.6rem;
    }}
    .method-body li {{ margin-bottom: 0.25rem; }}
    .method-body code {{
      background: #1e2130; border-radius: 3px; padding: 0.1rem 0.35rem;
      font-family: monospace; font-size: 0.9em; color: #a5b4fc;
    }}
    .method-body strong {{ color: #c4b5fd; }}
    .method-body em {{ color: #94a3b8; }}
  </style>
</head>
<body>
<div class="container">
  <p class="breadcrumb"><a href="index.html">&larr; All languages</a></p>
  <h1>{flag} {english} ({native})</h1>
  <p class="meta">
    Wikidata QuickStatements &mdash; language code
    <code style="background:#1e2130;border-radius:3px;padding:0.1rem 0.35rem;font-size:0.9em;color:#a5b4fc">{code}</code>
    &mdash; {count} statements
  </p>

  <div class="copy-bar">
    <button class="copy-btn" id="copy-btn" onclick="copyAll()">Copy all</button>
    <a class="qs-link" href="https://quickstatements.toolforge.org/#/batch"
       target="_blank" rel="noopener">Open QuickStatements ↗</a>
  </div>

  <textarea id="ta" spellcheck="false" autocorrect="off" autocomplete="off"{rtl_attr}>{content}</textarea>

  <details>
    <summary>How this was generated</summary>
    <div class="method-body">
      {methodology}
    </div>
  </details>
</div>
<script>
  function copyAll() {{
    const ta  = document.getElementById('ta');
    const btn = document.getElementById('copy-btn');
    navigator.clipboard.writeText(ta.value).then(() => {{
      btn.textContent = 'Copied!';
      btn.classList.add('copied');
      setTimeout(() => {{ btn.textContent = 'Copy all'; btn.classList.remove('copied'); }}, 1800);
    }});
  }}
</script>
</body>
</html>
"""

RTL_LANGS = {"fa", "ar", "arz", "he", "ur"}

def main():
    for code, english, native, flag, methodology in LANGS:
        txt_path = os.path.join(QS_DIR, code + ".txt")
        raw = open(txt_path, encoding="utf-8").read()
        count = len([l for l in raw.splitlines() if l.strip()])
        escaped = html.escape(raw)

        rtl_attr = ' dir="rtl"' if code in RTL_LANGS else ""
        out = PAGE_TEMPLATE.format(
            code=code,
            english=english,
            native=native,
            flag=flag,
            count=f"{count:,}",
            content=escaped,
            methodology=methodology,
            rtl_attr=rtl_attr,
        )
        out_path = os.path.join(DOCS_DIR, code + ".html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(out)
        size_kb = os.path.getsize(out_path) // 1024
        print(f"  {code}.html — {count:,} statements, {size_kb} KB")

    print("Done.")

if __name__ == "__main__":
    main()
