---
name: writing-with-human-voice
description: Use when writing or editing any prose for a human reader — essays, blog posts, emails, LinkedIn/X posts, marketing copy, fiction, scripts, docs, messages — or when text reads as robotic, generic, AI-generated, or "slop," or when asked to humanize, de-slop, or give voice to writing.
---

# Writing With Human Voice

## The core principle

AI prose is detectable not because of its vocabulary but because of its **stance**. The model writes from nowhere, to no one, hedging everything, and decorates empty claims with pleasing rhythm. A human writes from a located point of view, to one specific person, committed to a position, with detail only they would have.

**Fix the stance and most surface tells vanish on their own. Then clean up the few that remain.**

Every other "anti-AI-slop" tool is a banned-word list. They fail because they edit the symptom (the word "delve") not the cause (writing that has no one home). This skill works the other direction: build the voice first (Layer 1), strip the residue (Layer 2), calibrate to the format (Layer 3), then run the ear test and the analyzer (Layer 4).

## When to use

- Any prose meant to be read by a human: essays, posts, emails, copy, fiction, docs, replies, scripts, captions.
- When a draft reads generic, corporate, "AI-ish," or like it was written by a committee.
- When asked to humanize / de-slop / "make this sound like me" / "less robotic."

**When NOT to use:** pure structured data, code, config, API payloads, terse status lines where voice is noise.

## Layer 1 — Build the voice (do these first)

This is the engine. Skipping it and going straight to the ban-list is why other tools produce weird, lurching text.

| Move | Why it works | How to apply |
|------|-------------|--------------|
| **Take a position** | AI's #1 tell is epistemic timidity — hedging and false balance ("on one hand…"). A real writer has a stance. | State what you actually think. Cut "it depends," "both have merits," reflexive both-sidesing. If the truth is balanced, say *which way you lean and why*. |
| **Write to one person** | Grice: real communication assumes a specific reader and omits the obvious. Writing "to an audience" produces performance. | Picture one reader. Use "you." Cut anything you'd only say to impress a room, not tell a friend. |
| **Specificity over abstraction** | Concrete words fire sensory memory (dual-coding). Abstraction is where AI hides when it has nothing real. | Anchor every abstraction to one concrete thing: not "rich heritage" but "the festival has run every April since 1987." Use *real, uneven* detail. |
| **First-person agency + detail** | Pennebaker: authenticity = "I/we" + concrete sensory detail *together*. Passive + vague = the deception signature. | Name who did what. Prefer active verbs over nominalizations ("we decided" not "a decision was made"). |
| **Vary the rhythm** | Provost: monotone sentence length is the auditory signature of machine prose. The ear tunes out sameness. | Mix short, medium, and long *deliberately*. A three-word sentence after a winding one lands. Don't make *every* sentence short and punchy either — that's its own AI cadence. |
| **Show the joints of thinking** | Pinker's curse of knowledge: good writing reveals the path, not just the conclusion. | "You'd expect X, but…" / "what threw me was…" Let some reasoning show. Leave one loop open instead of resolving everything (curiosity gap). |

## Layer 2 — Kill these tells (after the voice exists)

Ordered by signal strength. The top three are what current models actually overuse — more than any banned word.

1. **Reflexive antithesis — THE deepest tell.** "It's not X, it's Y." "Not A, but B." "X isn't about P — it's about Q." The model reaches for this constantly because it *sounds* profound while committing to nothing. **Budget: at most one per piece, and only when the contrast is real.**
2. **Aphorism-compulsion.** Ending every paragraph on a clever mic-drop. Real writing lets most beats end plainly. One earned aphorism per piece beats five manufactured ones.
3. **Manufactured-clean specificity.** Suspiciously round, invented-feeling numbers ("12,000 users, 40% retention"). Real numbers are uneven (11,400; ~38%) or honestly absent. Don't fabricate precision.
4. **Tricolon stacking.** Rule-of-three once is fine. Three parallel triples in a row is pattern failure.
5. **Em-dash density.** Cap ~1 per 150 words.
6. **Signposted structure.** Delete "In conclusion," "Let's unpack/dive in," "It's worth noting that," "In today's world."
7. **Bold-first bullets** (`**Term:** explanation`) and **fractal summaries** (intro→body→recap at every level).
8. **Present-participle appendages.** "…, highlighting its importance." Cut or make it a real sentence.
9. **Vague authority.** "Experts say," "studies show" with no name or date.
10. **Banned vocabulary.** delve, tapestry, underscore, realm, leverage, navigate, robust, comprehensive, seamless, pivotal, crucial, meticulous, testament, showcase. Full list in `reference.md`.

## Layer 3 — Calibrate to the format

Voice is constant; register changes. Quick table below; full per-format specs (length, what to lean on, what to cut, openers/closers) in **`formats.md`**.

| Format | Register | Lean on | Avoid |
|--------|----------|---------|-------|
| Cold email | Brief, respects time | One concrete reason you're writing *them*; a small ask | Flattery, "hope this finds you well" |
| LinkedIn/X | Conversational, one idea | A real opinion or story | The "punchy fragment + aphorism" AI cadence |
| Essay/blog | Considered, voiced | A thesis, a path of thought, lived detail | Listicle skeleton, section recaps |
| Marketing | Vivid, benefit-led | Concrete outcome the reader feels | Superlatives, "revolutionary," empty hype |
| Technical | Precise, plain | Exact terms, real examples, honest caveats | Dumbing-down, over-hedging |
| Fiction | Whatever the voice demands | Sensory detail, subtext | Purple prose, tidy morals |
| Slack/text | Loose, human | Contractions, fragments | Formal structure, sign-offs |

## Layer 4 — The ear test + the analyzer (always run before done)

1. **Read it aloud.** Paul Graham's test: *would I say this to a friend?* Rewrite anything that sounds like a press release.
2. **Run the analyzer.** `llais.py` sits in this skill's own folder — zero dependencies, no API key. Run it on the draft:
   ```
   python llais.py draft.md          # from the skill folder
   # or, from anywhere: python /path/to/this-skill/llais.py draft.md
   ```
   It scores the draft 0–100 and flags the exact offending spans (antithesis, aphorism, em-dash, banned vocab, manufactured numbers, monotone rhythm). If you're an agent, add `--json` and parse the `findings` array. Fix the highest-severity findings first, then re-run.
3. **Loop** until the score clears your bar (≥ 85 for published work), then read aloud one more time. The number is a floor, not the goal — a 90 that sounds dead still fails the ear test.

```
draft  →  llais draft.md  →  fix top findings  →  re-run  →  (score ≥ 85?) → read aloud → ship
                  ↑________________________________________|  no
```

## Writing in someone's voice

To match a specific person's style (yours, a client's, a brand's), profile their existing writing first:
```
python llais.py --profile their_samples.md
```
It returns their fingerprint — sentence-length range and burstiness, contraction rate, reading ease, vocabulary diversity, signature words — and a one-line target spec to write toward. Full method in **`voice-capture.md`**.

## One before/after

> **Before (AI default):** "It's not just about hiring talent — it's about hiring the *right* talent. In today's competitive landscape, your first engineer is a pivotal decision that can make or break your startup's trajectory."
>
> **After (voiced):** "Your first engineer sets the bar everyone after them either clears or doesn't. Most founders chase a FAANG résumé when what they need is someone who'll ship ugly code, talk to customers, and rewrite it next week without sulking."

The fix wasn't swapping words. It was killing the antithesis, dropping "pivotal/landscape," taking a position, and adding real detail.

## Common mistakes

- **Going straight to the ban-list.** Removing "delve" from gutless prose gives you gutless prose without "delve." Build the voice first.
- **Over-correcting into choppiness.** All-short-punchy sentences are *also* an AI cadence. Vary, don't shrink.
- **Faking imperfection.** Don't bolt on typos or forced slang. Voice comes from stance and detail, not damage.
- **Chasing the score.** The analyzer catches structural tells, not dead writing. A high score with no point of view is still failure.

## Files in this skill

- `reference.md` — full banned inventory, the detection science (perplexity & burstiness), per-format rewrites, rationalization table.
- `formats.md` — deep per-format register specs.
- `voice-capture.md` — how to fingerprint and match a specific writer's voice.
- `llais.py` — the analyzer, in this folder. `python llais.py FILE` (also `--profile`, `--json`, `--min-score N`).
