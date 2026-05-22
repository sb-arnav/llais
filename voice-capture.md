# Voice capture — writing in a specific person's voice

Generic "human" writing is a low bar. The real unlock is writing in *one particular* voice — your own, a client's, a brand's, a character's. This is where AI writing usually collapses: it averages toward a pleasant, anonymous middle. A voice is the opposite of an average.

This doc shows how to extract a writer's fingerprint from samples and write toward it.

## What "voice" actually is (so you can copy it)

Voice is not a vibe. It decomposes into measurable, imitable parts:

1. **Rhythm** — sentence-length distribution: the average, and how much it swings (burstiness). Some writers run long and looping; some clip short; the strong ones swing wide.
2. **Diction** — word choice: formal vs plain, Latinate vs Anglo-Saxon, the signature words they reach for, whether they contract.
3. **Syntax habits** — how they open sentences, whether they front clauses, how many commas per sentence, fondness for fragments, dashes, parentheticals.
4. **Stance** — how they relate to the reader and the subject: certain or hedged, warm or cool, direct address or distance.
5. **Detail texture** — what *kind* of specifics they reach for (numbers, names, sensory, anecdote).

The first three are measurable. The analyzer reads them off samples for you. The last two you read by eye — but the metrics tell you where to look.

## Step 1 — Gather samples

Collect 300+ words the target actually wrote, in the register you're targeting (their casual tweets ≠ their formal essays — capture the right mode). Paste into a file, e.g. `samples.md`. More is better; 800–1500 words gives a stable fingerprint.

## Step 2 — Profile

```
python llais.py --profile samples.md
```

You get something like:

```
 mean_sentence_len          18.4
 sentence_len_stdev         11.2
 burstiness_cv              0.61      ← how much sentence length swings
 shortest_sentence          3
 longest_sentence           44
 syllables_per_word         1.47
 type_token_ratio           0.72
 mtld                       96.0      ← vocabulary range (higher = wider)
 hapax_rate                 0.61      ← share of words used exactly once
 contractions_per_sentence  0.9       ← informality
 commas_per_sentence        1.8       ← clause density
 em_dashes_per_100w         0.3
 flesch_reading_ease        58.0      ← reading level
 top_content_words          ...       ← their signature vocabulary
 Target voice: ~18-word sentences (range 3-44, CV 0.61), 0.9 contractions/sentence,
               reading ease ~58, 1.8 commas/sentence.
```

## Step 3 — Read what the numbers mean

| Reading | What it tells you to do when writing |
|--------|---------------------------------------|
| **Mean sentence length** | Match their default sentence size. An 11-word writer and a 24-word writer feel completely different. |
| **Burstiness CV** | High (>0.6) → they swing between very short and very long; do the same. Low (<0.45) → they're steady; don't suddenly fragment. |
| **Shortest / longest** | Their actual range. Give yourself permission to go as short and as long as they do. |
| **Contractions/sentence** | High → write loose and spoken. Near zero → they stay formal; respect it. |
| **Commas/sentence** | High → they build with subordinate clauses. Low → they prefer clean declaratives. |
| **Reading ease / syllables-per-word** | Their complexity level. Don't out-fancy or under-shoot them. |
| **MTLD / hapax** | Wide vocabulary → reach for varied, surprising words. Narrow → they repeat a tight set; don't sprinkle thesaurus words they'd never use. |
| **Top content words** | Their signature vocabulary and obsessions. Reuse the ones that fit naturally. |

## Step 4 — Write toward the spec, then verify

Draft in the target voice using the spec as a constraint. Then check your draft against theirs:

```
python llais.py --profile your_draft.md
```

Compare the two fingerprints. If your sentences average 12 words and theirs average 20, you're writing in your voice, not theirs. Adjust and re-profile until the numbers sit close.

Then run the normal slop check so you didn't drift into tells:
```
python llais.py your_draft.md
```

## What the numbers can't capture

Metrics get you rhythm, diction, and syntax — most of the way. They don't capture **stance** and **detail texture**, which you match by reading the samples directly and asking:

- Does this writer *commit* or hedge? Where do they show certainty?
- Do they address the reader ("you"), or hold them at arm's length?
- What do they find funny? What do they refuse to say plainly?
- When they get specific, do they reach for a number, a name, a smell, a story?

Match those by ear. The fingerprint tells you the body; you supply the temperament.

## A note on ethics

Voice-matching is for writing *as yourself*, for clients who've hired you, for brands you work on, or for fiction. Don't use it to impersonate real people deceptively. The tool measures public, surface stylistics — it's a craft aid, not a forgery kit.
