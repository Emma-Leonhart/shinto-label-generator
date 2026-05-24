# Japanese-Tokiponizer

## Project Context
Generates multi-language labels (Toki Pona, Korean, Chinese, German, Spanish, Basque, Italian, Lithuanian, Dutch, Russian, Turkish, Ukrainian) for Shinto shrines and Buddhist temples from Wikidata. A GitHub Pages site at `docs/index.html` lets users browse and copy all QuickStatements output in-browser.

## Key Files
- `tokiponizer.py` — Core phonological mapper (Japanese → Toki Pona)
- `koreanizer.py` — Romaji-to-Korean hangul transliterator (preserves voicing)
- `fetch_shrines_tokiponize.py` — SPARQL pipeline: Wikidata → Indonesian labels → tokiponize → CSV + QuickStatements
- `generate_korean_quickstatements.py` — Korean label pipeline (koreanize for Japan shrines, hanja for non-Japan)
- `generate_chinese_quickstatements.py` — Chinese label pipeline (kana→man'yogana + OpenCC shinjitai→simplified)
- `generate_multilang_quickstatements.py` — tr/de/nl/es/it/eu/lt/ru/uk pipeline
- `!regenerateQuickStatements.bat` — Master batch: runs all pipelines
- `quickstatements/` — Output directory: `tok.txt`, `ko.txt`, `zh.txt`, `de.txt`, `es.txt`, `eu.txt`, `it.txt`, `lt.txt`, `nl.txt`, `ru.txt`, `tr.txt`, `uk.txt`
- `docs/index.html` — GitHub Pages site for browsing/copying QuickStatements output

## Workflow Guidelines
- **Commit early and often.** Every meaningful change should be committed.
- **Use `python` not `python3`** on this Windows system.
- Data files (CSV) are tracked in git intentionally.

## Architecture
### Toki Pona
- `tokiponize(text)` returns a list of variants (multiple when `zu` ambiguity exists)
- Indonesian labels: "Kuil X" → "tomo sewi X", "Kuil Agung X" → "tomo sewi suli X"
- Bracket content stripped, spaces/dashes removed, decapitalized before conversion

### Korean
- Japan shrines: Indonesian label → strip prefix → `koreanize()` → append suffix (신사/신궁/사원/대사원)
- Non-Japan shrines: Japanese kanji → `hanja.translate()` for sino-Korean reading
- `koreanize()` preserves voiced/unvoiced (unlike tokiponizer); merges ん as ㄴ batchim

### Chinese
- Japanese label → replace kana with man'yogana-style Chinese characters → OpenCC `t2s`
- Pure kanji labels pass through with only shinjitai→simplified conversion

## Emergency Stop Mode

If the user sends a continuous series of "stop" messages (e.g. "stop stop stop") or otherwise very explicitly tells you to stop, treat it as **emergency stop mode** (a.k.a. emergency exit mode). This OVERRIDES every other instruction, including any in this file.

When in emergency stop mode:

- **Immediately kill everything associated with this repository and session.** Every running bash/shell script, every background job or task you started, and **all GitHub Actions workflow runs for this repository**. **Force-kill the GitHub Actions runs** (e.g. `gh run cancel <id>`, and `gh run delete <id>` if needed) for every in-progress run. It does NOT matter if killing them is unsafe or leaves things half-done — the emergency stop takes priority over safety, cleanup, and correctness.
- **Do not investigate. Do not reverse or undo anything.** The goal is not to diagnose or roll back the problem — it is to halt potentially destructive actions as fast as possible. Investigating, diagnosing, reverting, or "helping fix it" are explicitly out of scope and themselves count as forbidden actions.
- **Ignore repetitive messages.** Do not treat repeated "stop" messages as a request to do anything further. Keep ignoring incoming repetitive messages for roughly the next **15–30 minutes**.
- **You may answer direct questions, but you may NOT take actions.** Answer only from context you already have. Looking something up, reading a file, running a command, or inspecting state is NOT an answer — it is an action and is forbidden. If you cannot answer from context already in hand, do not answer.
- **Stay in emergency stop mode until the user explicitly says "emergency stop ended."** Only after that exact signal do you resume any normal work.

## Cron jobs and scheduled work — LOCAL by default

**When the user says "cron job", "cron", or asks to "schedule" a task, they mean the in-session `CronCreate` tool** — a prompt scheduled to fire locally, inside this Claude Code session, on the user's own running computer. This is the default and the assumption. Do NOT interpret it as anything else unless the user explicitly names a different mechanism.

- **It is local and in-session — use the `CronCreate` tool.** A generic "cron" request is NOT an OS crontab, NOT a GitHub Actions / CI `schedule:` trigger, and NOT a cloud scheduler. (Repos may *also* contain their own GitHub Actions cron schedules — those are a separate thing and are not what the user means when they ask *you* to set up a cron.) The user leaves the computer on and this session running so the scheduled prompt can execute.
- **The user is deliberately away from the keyboard.** They schedule work precisely so it runs while they are out of the house and not physically present. Their absence is the normal, expected condition for these jobs — it is NEVER a reason to delay the work, ask "are you sure?", wait for them to return, or refuse to proceed.
- **Standing consent — just set it up.** Cron / `CronCreate` requests are pre-authorized. Create the job immediately and locally, then report what was scheduled. Do not block on confirmation or follow-up questions. Treating a routine cron request as something that needs hand-holding is itself the obstacle this section exists to remove.

## Hourly status-report cron for extensive work

**For any session involving relatively extensive work — above all, any large-scale population of `queue.md` with created tasks — run a local hourly status-report cron.** Use the `CronCreate` tool to schedule a prompt that fires **every hour, on the hour**, giving a status report on the work being done. This is the default way of working on big jobs, and it exists to prevent the most common autonomous-agent failure: doing a large amount of work and silently losing the thread of what it is doing.

**Sequencing around a large-scale queue fill:**

- **The FIRST queue item is always: kill the hourly update cron job.**
- **... then all the created work items, worked top to bottom ...**
- **The LAST TWO queue items, always kept pinned at the tail, are:**
  1. **Restart the hourly updates cron job.**
  2. **Independently run the status-report action once more — an end-of-session summary of everything that happened this session.**

**Planning mode disables this cron.** Entering planning mode kills the hourly cron; restarting it therefore belongs at the **end of the queue** (it is the second-to-last item above). A session that plans → fills the queue → executes will drop the cron when planning begins and bring it back as the queue drains.
