# llais

**llais** is Welsh for *voice*. It makes AI writing sound human — and proves it with a number.

Two things that work together:

1. **An analyzer** (`llais.py`) that scores any prose 0–100 on how human vs. AI-generated it reads, and points at the exact sentences giving it away. Zero dependencies. Pure Python.
2. **A writing skill** (`skill/`) that teaches an agent — or you — to write with an actual voice, not just avoid trigger words. Works as a [Claude Code](https://docs.claude.com/en/docs/claude-code) skill or as a plain reference.

```text
$ python llais.py examples/slop.md
────────────────────────────────────────────────────────
 Human Voice Score: 30/100  (AI slop)
────────────────────────────────────────────────────────
  !! [antithesis] (line 3) reflexive antithesis ("not X — it's Y"); budget is 1 per piece
        ↳ …trajectory. It's not just about finding talent — it's about finding the *righ…
  !  [vocabulary] (line 9) high-signal AI word: "delve"
  !  [structure] (line 5) signpost / throat-clearing: "let's dive in"
  ·  [numbers]   (line 7) tidy percentage: "80%" — real numbers are messier
  ... 23 more

$ python llais.py examples/voiced.md
 Human Voice Score: 100/100  (human)
 No structural tells found. Read it aloud anyway.
```

## Why this exists

Every "humanizer" tool and "anti-AI-slop" prompt out there is a **banned-word list**. Strip the em-dashes, swap "delve" for "explore", vary the sentence length, done. They don't work — and worse, they make writing weirder, because they edit the *symptom* instead of the *cause*.

The cause isn't vocabulary. Current models are well past "tapestry." The reason AI prose reads as AI is **stance**: it's written from nowhere, to no one, hedging everything, decorating empty claims with pleasant rhythm. The tells that actually give it away are structural, and a word-list never catches them:

- **Reflexive antithesis** — "It's not X, it's Y," reached for again and again because it *sounds* insightful while committing to nothing.
- **Aphorism-compulsion** — every paragraph landing a tidy mic-drop.
- **Manufactured-precise numbers** — suspiciously round "12,000 users, 40% retention" that smell invented.
- **Monotone rhythm** — sentences of uniform length; the auditory signature of a machine.

`llais` measures these directly. The skill fixes them at the source: take a position, write to one person, anchor every abstraction in real detail, vary the rhythm. Fix the stance and the surface tells mostly disappear on their own.

## Quick start

No install, no dependencies. Python 3.10+.

```bash
git clone https://github.com/sb-arnav/llais.git
cd llais

python llais.py path/to/draft.md      # full scored report
cat draft.md | python llais.py -      # or pipe via stdin
python llais.py --quiet draft.md      # just the score
python llais.py --json draft.md       # machine-readable
```

Gate it in CI or an editing loop:

```bash
python llais.py --min-score 85 --quiet draft.md   # exits non-zero if below 85
```

## What the analyzer catches

| Category | What it flags |
|----------|---------------|
| **antithesis** | "It's not X — it's Y" and its variants (the deepest current-model tell) |
| **rhythm** | Monotone sentence length (low burstiness), all-short staccato, uniform paragraphs |
| **aphorism** | Paragraphs that keep ending on a short mic-drop |
| **vocabulary** | ~80 high-signal AI words + filler phrases, narrow vocabulary |
| **structure** | Signposts ("In conclusion," "Let's dive in"), throat-clearing openers |
| **numbers** | Suspiciously round figures and tidy percentages |
| **punctuation** | Em-dash overuse (per-100-word rate) |
| **formatting** | Bold-first bullets (`**Term:** ...`) |
| **authority** | "Experts say" / "studies show" with no name, date, or number |
| **participle** | Fake-depth appendages ("…, highlighting its importance") |

Each finding includes the line number and the offending excerpt, so you fix the text, not chase a score.

## Writing in a specific voice

Generic "human" is a low bar. To write as *one particular* person — you, a client, a brand — profile their writing first:

```bash
python llais.py --profile their_samples.md
```

You get their fingerprint — sentence-length range and burstiness, contraction rate, reading ease, vocabulary diversity (MTLD), signature words — plus a one-line target spec to write toward. Full method in [`skill/voice-capture.md`](skill/voice-capture.md).

## Using the writing skill

The `skill/` directory is a self-contained writing system:

- [`SKILL.md`](skill/SKILL.md) — the method: build the voice, kill the tells, calibrate to format, run the ear test + analyzer loop.
- [`reference.md`](skill/reference.md) — the full banned inventory, the detection science (perplexity & burstiness), per-format rewrites.
- [`formats.md`](skill/formats.md) — register specs for cold email, LinkedIn, essay, marketing, technical, fiction, chat.
- [`voice-capture.md`](skill/voice-capture.md) — fingerprinting and matching a writer's voice.

**In Claude Code**, install it as a personal skill:

```bash
cp -r skill ~/.claude/skills/writing-with-human-voice
```

It then triggers automatically whenever you write or edit prose. Other agent setups: point your system prompt at `skill/SKILL.md`.

## How it works

The analyzer is heuristic and deliberately model-free, so it runs anywhere with no API and no dependencies. It combines regex pattern detection (for the structural tells) with classic stylometry and readability metrics:

- **Burstiness** — coefficient of variation of sentence lengths. Human prose runs ~0.5–0.9; AI clusters at 0.3–0.5.
- **Readability** — Flesch Reading Ease and Flesch-Kincaid grade.
- **Lexical diversity** — type-token ratio, MTLD (length-robust), Yule's K, hapax-legomena rate.
- **Surface stats** — contraction rate, comma density, em-dash rate per 100 words.

Findings are weighted by severity and capped per category, then subtracted from 100. The thresholds are grounded in stylometry and AI-detection research (Pennebaker/LIWC on function-word authenticity, Provost on rhythm, the documented "delve" frequency spikes, GPTZero's perplexity/burstiness framing). It is **not** a detector-evasion tool — it doesn't try to fool GPTZero, it tries to make the writing genuinely better.

### Deliberate limits

- No part-of-speech features (those need a tagger; this stays zero-dependency). 
- Heuristic syllable counting — fine in aggregate, occasionally off on edge words.
- A high score means "no structural tells," not "good writing." Dead prose with a point of view problem can still score well. The ear test is not optional.
- It targets *prose*. Documents that quote AI tells as examples (this README, the skill files) score low on purpose — the analyzer can't tell a specimen from a sin. Reference docs also lean on bold bullets and dashes that are fine in a README and flagged in an essay. Point it at real drafts.

## Develop

```bash
python -m unittest -v     # 25 tests, no dependencies
```

CI runs the suite on Python 3.10–3.12. Contributions welcome — especially new tells (with a test that fails before your fix) and better example pairs.

## License

MIT. See [LICENSE](LICENSE).
