# Reference — Writing With Human Voice

Heavy reference for the `writing-with-human-voice` skill. Load when you need the full inventory, the science, or worked examples. The judgment lives in SKILL.md; this is the lookup table behind it.

---

## Why uniformity reads as machine (the detection science)

Understanding the mechanism lets you apply the principle in new situations instead of pattern-matching a list.

- **Perplexity** = how predictable each next word is. Models pick high-probability tokens, so AI text is *low-perplexity* — smooth, expected, never surprising. Human writers reach for the word that fits *and* surprises, spiking perplexity. GPTZero treats sustained low perplexity as the core machine signal.
- **Burstiness** = variance in sentence length/complexity across a piece. Humans are bursty: a dense 30-word sentence, then four words. Models are metronomic — uniform clause length, uniform paragraph length. One 2024 study cut detection ~40% just by manually varying sentence structure. **This is why "vary the rhythm" is not a style preference — it's the single highest-leverage edit.**
- **Function-word fingerprint** (Pennebaker/LIWC): pronoun, article, and preposition distributions leak authorship and authenticity, and they stay stable across prompts. Authentic writing = more "I/we/you" + concrete detail. Deceptive/performed writing = passive voice + abstraction. Reaching for first-person agency and concrete nouns isn't decoration; it moves the measurable signal.
- **The implication:** you cannot win at the word layer (humanizers prove this — they swap synonyms and detectors still catch the structure). You win by changing *what gets said* and *how it's shaped*: position, specificity, rhythm, located point of view.

---

## Full banned / high-signal inventory

Not absolute bans — high-signal words that, in aggregate, scream AI. One slip is fine; a cluster is fatal. Prefer the plain alternative.

### Verbs / verb phrases
delve, dive into, navigate (figurative), underscore, highlight (as filler), leverage, harness, foster, bolster, unlock, unleash, embark, elevate, streamline, showcase, spearhead, "serves as," "stands as," "pave the way," "shed light on," "speaks to," "lends itself to."

### Adjectives
robust, comprehensive, seamless, pivotal, crucial, vital, meticulous, intricate, profound, nuanced, holistic, multifaceted, cutting-edge, groundbreaking, transformative, revolutionary, commendable, rich (figurative), vibrant, bustling.

### Nouns / ornaments
tapestry, realm, landscape (as domain filler), ecosystem (figurative), paradigm, synergy, framework (as filler), journey (figurative), testament, treasure trove, game-changer, cornerstone, beacon, plethora, myriad.

### Adverbs (inflation tells)
quietly, deeply, fundamentally, remarkably, notably, certainly, undoubtedly, arguably, essentially, ultimately, truly, simply, seamlessly.

### Throat-clearing openers (delete)
"In today's [fast-paced/digital/competitive] world," "In an era of," "When it comes to," "It's worth noting that," "It's important to remember," "At its core," "Needless to say," "First and foremost," "Let's dive in," "Let's unpack/break this down/explore," "Great question!"

### Connective / structural tells
"Moreover," "Furthermore," "Additionally," "That being said," "In conclusion," "To sum up," "In summary," "Ultimately," "At the end of the day."

### Sentence-shape tells
- **Negative antithesis:** "It's not X, it's Y" / "Not A, but B" / "X isn't just about P — it's about Q." (≤1 per piece, earned.)
- **Self-posed rhetorical Q + instant answer:** "The result? A disaster." (Nobody asked.)
- **Dramatic countdown:** "Not this. Not that. Just this."
- **False range:** "From X to Y" where X and Y aren't on a real spectrum.
- **Present-participle appendage:** "…, highlighting/reflecting/underscoring/showcasing [significance]."
- **Tricolon stacking:** more than one rule-of-three in a row.

### Formatting tells
Bold-first bullets (`**Term:** explanation`), every section ending in a recap sentence, uniform paragraph length, emoji-bulleted lists in prose contexts, title-casing every heading like a brochure.

---

## Per-format before/after

### Cold email
**Before:** "I hope this email finds you well. I am reaching out to explore potential synergies between our organizations. Our revolutionary platform leverages cutting-edge AI to transform productivity."
**After:** "You wrote last month that note-taking tools mostly add overhead instead of removing it. That's the exact problem we built Notch around — and the reason I think 20 minutes of your time might be worth it. Can I send you what we're seeing with our first 400 users?"
*Fixes:* killed the greeting cliché and "synergies/revolutionary/leverages/cutting-edge"; opened with a real reason tied to *that* reader; honest, modest number; clear small ask.

### LinkedIn post
**Before:** "Success isn't about working harder. It's about working smarter. Here are 3 lessons that transformed my career: 1) Embrace failure 2) Network relentlessly 3) Never stop learning."
**After:** "I got promoted twice in the year I worked the *least* I ever had. Not because I'd cracked some productivity hack — I'd just stopped volunteering for work that made me look busy and started saying no to it out loud. Turns out the second part is the hard one."
*Fixes:* killed antithesis + tricolon listicle; one real story; a position; left the hard part slightly open.

### Essay opening
**Before:** "Productivity applications have become ubiquitous in modern life. While they offer numerous benefits, they also present certain challenges that are worth examining in detail."
**After:** "I once had eleven productivity apps. A task manager wired to my calendar, two note apps (one for 'real' notes), a habit tracker with streaks I guarded like savings. What I actually had was a beautifully organized list of everything I wasn't doing."
*Fixes:* killed "ubiquitous/numerous benefits/worth examining"; concrete uneven detail; voice and stance from line one.

### Technical post
**Before:** "It's crucial to understand that caching is a powerful technique that can significantly enhance performance. Let's delve into the various strategies available."
**After:** "Caching trades correctness risk for speed. That trade is usually worth it for reads and almost never worth it for a user's account balance. Three strategies, and when each one bites you:"
*Fixes:* killed "crucial/powerful/significantly/delve/let's"; stated the real tradeoff; set up honest caveats instead of a tour.

---

## Rationalization table (when tempted to skip the ear test)

| Excuse | Reality |
|--------|---------|
| "This draft already sounds fine." | Fine to you on screen ≠ fine read aloud. Read it aloud anyway — that's where the antitheses and monotone surface. |
| "One 'it's not X, it's Y' is fine." | One *is* fine. Go count. If it's your second, you're on autopilot — cut it. |
| "Round numbers are cleaner." | Clean numbers read as invented. Use the real (uneven) figure or none. |
| "The banned words are just normal words." | In isolation, yes. In a cluster they're the signal. You don't need "leverage" *and* "robust" *and* "seamless" in one paragraph. |
| "Short punchy sentences sound confident." | All-short is its own machine cadence. Burstiness means *varied*, not *short*. |
| "I don't have a strong opinion here." | Then find which way you lean and why. Neutral-survey prose is the thing readers (and detectors) flag as written-by-no-one. |
| "Format doesn't matter, good writing is good writing." | A great essay paragraph is a terrible Slack message. Calibrate register (Layer 3). |

---

## Distilled — tape to the wall

1. Have a position. Cut false balance.
2. Write to one person. Use "you."
3. Anchor every abstraction to one real, uneven detail.
4. Vary sentence length on purpose. Read it aloud.
5. One antithesis max. One aphorism max.
6. Real numbers or no numbers.
7. Calibrate register to the format.
8. If a stranger can't tell what you think, you're not done.
