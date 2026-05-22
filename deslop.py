#!/usr/bin/env python3
"""
deslop — score prose on how human vs. AI-generated it reads, and flag the exact spans.

Zero dependencies. Pure standard library. Works on any .md/.txt or stdin.

It does NOT try to defeat detectors by swapping synonyms. It measures the
*structural* signatures that current language models actually overproduce —
reflexive antithesis, aphorism-compulsion, manufactured-precise numbers,
monotone sentence rhythm, em-dash spam, and a high-signal vocabulary — then
points at the offending text so you can fix the cause, not the symptom.

Usage:
    deslop FILE                 # scored report for a file
    cat FILE | deslop -         # read from stdin
    deslop --json FILE          # machine-readable report
    deslop --quiet FILE         # just the score line
    deslop --profile FILE       # extract a writer's style fingerprint (voice capture)

See the writing skill in skill/ for how to act on the findings.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass, field, asdict
from typing import Callable


# --------------------------------------------------------------------------- #
# Text segmentation                                                           #
# --------------------------------------------------------------------------- #

_SENT_SPLIT = re.compile(r"(?<=[.!?])[\"')\]]?\s+(?=[A-Z0-9\"'(\[])")
_WORD = re.compile(r"[A-Za-z][A-Za-z'’-]*")
_ABBREV = {"mr", "mrs", "ms", "dr", "vs", "etc", "e.g", "i.e", "st", "inc", "co"}


def strip_markdown(text: str) -> str:
    """Drop code and blockquotes so we score the author's prose, not quoted matter."""
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"`[^`]+`", " ", text)
    text = re.sub(r"(?m)^\s*>.*$", " ", text)  # blockquotes are quotations, not authored prose
    return text


def split_sentences(text: str) -> list[str]:
    # Protect common abbreviations from being treated as sentence ends.
    chunks = _SENT_SPLIT.split(text.strip())
    out: list[str] = []
    for c in chunks:
        c = c.strip()
        if not c:
            continue
        if out and out[-1].rstrip(".").split(" ")[-1].lower() in _ABBREV:
            out[-1] = out[-1] + " " + c
        else:
            out.append(c)
    return out


def split_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def words(text: str) -> list[str]:
    return _WORD.findall(text)


def count_syllables(word: str) -> int:
    word = word.lower()
    word = re.sub(r"[^a-z]", "", word)
    if not word:
        return 0
    n = len(re.findall(r"[aeiouy]+", word))
    if word.endswith("e"):
        # Consonant + "le" keeps its syllable (ta-ble); other trailing e is silent.
        if not (word.endswith("le") and len(word) > 2 and word[-3] not in "aeiouy"):
            n -= 1
    return max(1, n)


# --------------------------------------------------------------------------- #
# Findings                                                                     #
# --------------------------------------------------------------------------- #

@dataclass
class Finding:
    category: str
    severity: int          # 1 (minor) .. 3 (severe)
    message: str
    excerpt: str = ""
    line: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


def _line_of(text: str, idx: int) -> int:
    return text.count("\n", 0, idx) + 1


def _excerpt(text: str, start: int, end: int, pad: int = 24) -> str:
    a = max(0, start - pad)
    b = min(len(text), end + pad)
    s = text[a:b].replace("\n", " ").strip()
    return ("…" if a > 0 else "") + s + ("…" if b < len(text) else "")


# --------------------------------------------------------------------------- #
# High-signal vocabulary                                                       #
# --------------------------------------------------------------------------- #

BANNED_WORDS = {
    # verbs
    "delve", "delves", "delving", "leverage", "leverages", "leveraging",
    "harness", "harnesses", "underscore", "underscores", "underscoring",
    "foster", "fosters", "bolster", "bolsters", "unlock", "unlocks",
    "unleash", "unleashes", "embark", "elevate", "elevates", "streamline",
    "streamlines", "showcase", "showcases", "showcasing", "spearhead",
    # adjectives
    "robust", "comprehensive", "seamless", "seamlessly", "pivotal", "crucial",
    "vital", "meticulous", "meticulously", "intricate", "profound",
    "multifaceted", "holistic", "cutting-edge", "groundbreaking",
    "transformative", "revolutionary", "commendable", "vibrant", "bustling",
    # nouns / ornaments
    "tapestry", "realm", "ecosystem", "paradigm", "synergy", "testament",
    "treasure", "cornerstone", "beacon", "plethora", "myriad",
    # adverbs
    "quietly", "deeply", "fundamentally", "remarkably", "notably",
    "undoubtedly", "arguably", "essentially", "ultimately",
}

BANNED_PHRASES = [
    "navigate the", "navigating the", "dive into", "diving into",
    "shed light on", "pave the way", "paving the way", "speaks to",
    "lends itself", "serves as", "stands as", "when it comes to",
    "at its core", "it's worth noting", "it is worth noting",
    "needless to say", "first and foremost", "let's dive", "let's unpack",
    "let's explore", "let's break", "in today's", "in an era",
    "in conclusion", "to sum up", "in summary", "at the end of the day",
    "that being said", "a testament to", "rich tapestry", "treasure trove",
    "game-changer", "game changer", "ever-evolving", "ever-changing",
]

SIGNPOSTS = [
    "in conclusion", "to sum up", "in summary", "to summarize",
    "let's dive in", "let's unpack", "let's explore", "let's break this down",
    "it's worth noting that", "it is worth noting that", "needless to say",
    "first and foremost", "at its core", "in today's", "in an era of",
    "great question", "when it comes to",
]


# --------------------------------------------------------------------------- #
# Detectors                                                                    #
# --------------------------------------------------------------------------- #

# Reflexive antithesis: the deepest current-model tell.
ANTITHESIS_PATTERNS = [
    re.compile(r"\bit'?s\s+not\s+(?:just\s+)?[^.,;]{1,60}?[,—-]+\s*it'?s\b", re.I),
    re.compile(r"\bisn'?t\s+(?:just\s+)?[^.,;]{1,60}?[,—-]+\s*it'?s\b", re.I),
    re.compile(r"\bnot\s+(?:just\s+)?(?:about\s+)?[^.,;]{1,50}?\s+[—-]+\s*it'?s\b", re.I),
    re.compile(r"\bnot\s+because\s+[^.,;]{1,60}?,\s*but\s+because\b", re.I),
    re.compile(r"\bthey'?re\s+not\s+[^.,;]{1,50}?\.\s+They'?re\b", re.I),
    re.compile(r"\bnot\s+(?:an?\s+)?[^.,;]{1,30}?[.,]\s+(?:A|An|The)?\s*[^.,;]{1,30}?\s+(?:instead|rather)\b", re.I),
]

# Staccato rule-of-three: "Not X. Not Y. Just Z."
STACCATO = re.compile(r"(?:\b(?:Not|No|Just|Only)\b[^.!?]{1,40}[.!?]\s*){3}", re.I)

# Tricolon: "a, b, and c" parallel triples.
TRICOLON = re.compile(r"\b[\w'-]+,\s+[\w'-]+,\s+(?:and|or)\s+[\w'-]+\b")

# Present-participle appendage tacked on the end of a clause for fake depth.
PARTICIPLE_APPENDAGE = re.compile(
    r",\s+(highlighting|reflecting|underscoring|showcasing|emphasizing|"
    r"demonstrating|representing|signaling|cementing|reinforcing|marking)\b[^.]{0,80}\.",
    re.I,
)

# Vague authority with no name/number/year nearby.
VAGUE_AUTHORITY = re.compile(
    r"\b(experts?\s+(?:say|agree|argue|believe)|studies\s+show|"
    r"research\s+(?:shows|suggests|indicates)|scientists\s+(?:say|believe)|"
    r"it\s+is\s+widely\s+(?:believed|known|accepted))\b",
    re.I,
)

# Bold-first markdown bullet: "- **Term:** explanation"
BOLD_BULLET = re.compile(r"(?m)^\s*[-*+]\s+\*\*[^*]+\*\*\s*[:—-]")

# Manufactured-precise numbers: clean round figures and tidy percentages.
ROUND_NUM = re.compile(r"\b(\d{1,3}(?:,\d{3})+|\d+0{2,})\b")
CLEAN_PCT = re.compile(r"\b(\d{1,3})\s?%")
_CLEAN_PCT_SET = {0, 5, 10, 15, 20, 25, 30, 40, 50, 60, 70, 75, 80, 90, 95, 99, 100}

EM_DASH = re.compile(r"—|(?<=\w)\s+--?\s+(?=\w)")
CONTRACTION = re.compile(r"\b\w+['’](?:s|re|ve|ll|d|t|m)\b", re.I)


def detect_vocab(text: str) -> list[Finding]:
    out: list[Finding] = []
    low = text.lower()
    for m in _WORD.finditer(text):
        w = m.group(0).lower()
        if w in BANNED_WORDS:
            out.append(Finding("vocabulary", 2, f'high-signal AI word: "{m.group(0)}"',
                               _excerpt(text, m.start(), m.end()), _line_of(text, m.start())))
    for ph in BANNED_PHRASES:
        start = 0
        while True:
            i = low.find(ph, start)
            if i == -1:
                break
            out.append(Finding("vocabulary", 2, f'filler phrase: "{ph}"',
                               _excerpt(text, i, i + len(ph)), _line_of(text, i)))
            start = i + len(ph)
    return out


def detect_signposts(text: str) -> list[Finding]:
    out: list[Finding] = []
    low = text.lower()
    for sp in SIGNPOSTS:
        i = low.find(sp)
        while i != -1:
            out.append(Finding("structure", 2, f'signpost / throat-clearing: "{sp}"',
                               _excerpt(text, i, i + len(sp)), _line_of(text, i)))
            i = low.find(sp, i + len(sp))
    return out


def _regex_findings(text: str, pat: re.Pattern, category: str, severity: int,
                    message: str) -> list[Finding]:
    out: list[Finding] = []
    for m in pat.finditer(text):
        out.append(Finding(category, severity, message,
                           _excerpt(text, m.start(), m.end()), _line_of(text, m.start())))
    return out


def detect_antithesis(text: str) -> list[Finding]:
    out: list[Finding] = []
    seen: set[int] = set()
    for pat in ANTITHESIS_PATTERNS:
        for m in pat.finditer(text):
            if any(abs(m.start() - s) < 8 for s in seen):
                continue
            seen.add(m.start())
            out.append(Finding("antithesis", 3,
                               'reflexive antithesis ("not X — it\'s Y"); budget is 1 per piece',
                               _excerpt(text, m.start(), m.end()), _line_of(text, m.start())))
    return out


def detect_numbers(text: str) -> list[Finding]:
    out: list[Finding] = []
    for m in ROUND_NUM.finditer(text):
        out.append(Finding("numbers", 1, f'suspiciously round figure: "{m.group(0)}" — is it real?',
                           _excerpt(text, m.start(), m.end()), _line_of(text, m.start())))
    for m in CLEAN_PCT.finditer(text):
        if int(m.group(1)) in _CLEAN_PCT_SET:
            out.append(Finding("numbers", 1, f'tidy percentage: "{m.group(0)}" — real numbers are messier',
                               _excerpt(text, m.start(), m.end()), _line_of(text, m.start())))
    return out


def detect_rhythm(text: str, sents: list[str]) -> tuple[list[Finding], dict]:
    out: list[Finding] = []
    lengths = [len(words(s)) for s in sents if words(s)]
    stats = {"sentences": len(lengths)}
    if len(lengths) < 3:
        stats.update({"mean_len": round(sum(lengths) / len(lengths), 1) if lengths else 0,
                      "cv": None})
        return out, stats
    mean = sum(lengths) / len(lengths)
    var = sum((x - mean) ** 2 for x in lengths) / len(lengths)
    sd = math.sqrt(var)
    cv = sd / mean if mean else 0
    stats.update({"mean_len": round(mean, 1), "stdev": round(sd, 1),
                  "cv": round(cv, 2), "min_len": min(lengths), "max_len": max(lengths)})
    # Humans run ~0.5-0.9 CV; LLM prose clusters low.
    if cv < 0.35:
        out.append(Finding("rhythm", 3,
                           f"monotone rhythm: sentence-length variation is very low (CV={cv:.2f}); "
                           f"vary short and long deliberately", "", 0))
    elif cv < 0.5:
        out.append(Finding("rhythm", 2,
                           f"flat rhythm: low sentence-length variation (CV={cv:.2f}); "
                           f"break the pattern with a very short or very long sentence", "", 0))
    # All-short staccato is its own machine cadence.
    if mean < 11 and cv < 0.5:
        out.append(Finding("rhythm", 2,
                           f"uniformly short sentences (avg {mean:.0f} words); "
                           f"burstiness means varied, not just short", "", 0))
    return out, stats


def detect_aphorism(text: str, paras: list[str]) -> list[Finding]:
    """Paragraphs that end on a short punchy mic-drop, repeatedly."""
    out: list[Finding] = []
    punchy = 0
    total = 0
    for p in paras:
        ss = split_sentences(p)
        if len(ss) < 2:
            continue
        total += 1
        last = ss[-1]
        wl = len(words(last))
        if wl <= 8 and (last.endswith(".") or last.endswith("!")):
            punchy += 1
    if total >= 3 and punchy >= max(3, total * 0.6):
        out.append(Finding("aphorism", 2,
                           f"aphorism-compulsion: {punchy}/{total} paragraphs end on a short mic-drop; "
                           f"let most beats end plainly", "", 0))
    return out


# --------------------------------------------------------------------------- #
# Report assembly                                                              #
# --------------------------------------------------------------------------- #

# Category weights: penalty-per-finding scaled by severity, then capped.
WEIGHTS = {
    "antithesis": 9, "rhythm": 8, "aphorism": 7, "structure": 5,
    "vocabulary": 4, "numbers": 3, "punctuation": 4, "formatting": 4,
    "authority": 4, "participle": 5, "tricolon": 3,
}
CATEGORY_CAP = {  # max total penalty a single category can contribute
    "antithesis": 30, "rhythm": 22, "aphorism": 14, "structure": 18,
    "vocabulary": 22, "numbers": 10, "punctuation": 12, "formatting": 12,
    "authority": 10, "participle": 12, "tricolon": 9,
}


@dataclass
class Report:
    score: int
    grade: str
    findings: list[Finding] = field(default_factory=list)
    stats: dict = field(default_factory=dict)
    by_category: dict = field(default_factory=dict)


def grade_for(score: int) -> str:
    if score >= 90:
        return "human"
    if score >= 75:
        return "mostly human"
    if score >= 55:
        return "mixed"
    if score >= 35:
        return "AI-leaning"
    return "AI slop"


def analyze(raw: str) -> Report:
    text = strip_markdown(raw)
    sents = split_sentences(text)
    paras = split_paragraphs(text)
    wcount = len(words(text))

    findings: list[Finding] = []
    findings += detect_antithesis(text)
    findings += detect_vocab(text)
    findings += detect_signposts(text)
    findings += detect_numbers(text)
    findings += _regex_findings(text, STACCATO, "structure", 3,
                                'staccato rule-of-three ("Not X. Not Y. Just Z.")')
    findings += _regex_findings(text, PARTICIPLE_APPENDAGE, "participle", 2,
                                'present-participle appendage (fake depth tacked on a clause)')
    findings += _regex_findings(text, VAGUE_AUTHORITY, "authority", 2,
                                'vague authority with no name/date/number')
    findings += _regex_findings(raw, BOLD_BULLET, "formatting", 2,
                                'bold-first bullet ("**Term:** ...") — reads as unedited AI')

    # tricolon density
    tri = list(TRICOLON.finditer(text))
    if wcount and len(tri) / max(1, wcount) * 100 > 0.6:
        for m in tri[:6]:
            findings.append(Finding("tricolon", 1, "rule-of-three (used repeatedly)",
                                    _excerpt(text, m.start(), m.end()), _line_of(text, m.start())))

    # em-dash density
    em = list(EM_DASH.finditer(text))
    em_rate = len(em) / max(1, wcount) * 100
    if em_rate > 0.7:
        findings.append(Finding("punctuation", 2,
                                f"em-dash overuse: {len(em)} in {wcount} words "
                                f"({em_rate:.1f}/100w; aim < 0.7)", "", 0))

    rhythm_findings, rhythm_stats = detect_rhythm(text, sents)
    findings += rhythm_findings
    findings += detect_aphorism(text, paras)

    # Uniform paragraph length is a documented document-level tell.
    para_lens = [len(words(p)) for p in paras if words(p)]
    if len(para_lens) >= 4 and _cv(para_lens) < 0.3:
        findings.append(Finding("rhythm", 2,
                                f"uniform paragraph lengths (CV {_cv(para_lens):.2f}); "
                                f"let some paragraphs run long and others land in one line", "", 0))

    # lexical diversity (length-robust-ish: TTR over first 400 tokens)
    toks = [w.lower() for w in words(text)]
    window = toks[:400]
    ttr = len(set(window)) / len(window) if window else 0
    if window and ttr < 0.42:
        findings.append(Finding("vocabulary", 2,
                                f"narrow vocabulary (type-token ratio {ttr:.2f})", "", 0))

    contraction_rate = len(CONTRACTION.findall(text)) / max(1, len(sents))

    # ---- scoring ----
    cat_pen: dict[str, float] = {}
    for f in findings:
        w = WEIGHTS.get(f.category, 4)
        cat_pen[f.category] = cat_pen.get(f.category, 0) + w * (f.severity / 2)
    for cat in cat_pen:
        cat_pen[cat] = min(cat_pen[cat], CATEGORY_CAP.get(cat, 15))
    penalty = sum(cat_pen.values())
    score = max(0, min(100, round(100 - penalty)))

    stats = {
        "words": wcount,
        "sentences": len(sents),
        "paragraphs": len(paras),
        "type_token_ratio": round(ttr, 2),
        "contractions_per_sentence": round(contraction_rate, 2),
        "em_dashes_per_100w": round(em_rate, 2),
        "flesch_reading_ease": flesch_reading_ease(text, sents),
        **rhythm_stats,
    }

    return Report(score=score, grade=grade_for(score), findings=findings,
                  stats=stats, by_category={k: round(v, 1) for k, v in cat_pen.items()})


def flesch_reading_ease(text: str, sents: list[str]) -> float:
    w = words(text)
    if not w or not sents:
        return 0.0
    syll = sum(count_syllables(x) for x in w)
    fre = 206.835 - 1.015 * (len(w) / len(sents)) - 84.6 * (syll / len(w))
    return round(fre, 1)


def fk_grade(text: str, sents: list[str]) -> float:
    w = words(text)
    if not w or not sents:
        return 0.0
    syll = sum(count_syllables(x) for x in w)
    return round(0.39 * (len(w) / len(sents)) + 11.8 * (syll / len(w)) - 15.59, 1)


def hapax_rate(toks: list[str]) -> float:
    """Share of word *types* that appear exactly once. Humans ~0.4-0.6; AI lower."""
    if not toks:
        return 0.0
    counts: dict[str, int] = {}
    for t in toks:
        counts[t] = counts.get(t, 0) + 1
    hapax = sum(1 for c in counts.values() if c == 1)
    return round(hapax / len(counts), 2)


def yules_k(toks: list[str]) -> float:
    """Vocabulary concentration. Lower = more diverse. Length-robust."""
    if not toks:
        return 0.0
    counts: dict[str, int] = {}
    for t in toks:
        counts[t] = counts.get(t, 0) + 1
    n = len(toks)
    freq_of_freq: dict[int, int] = {}
    for c in counts.values():
        freq_of_freq[c] = freq_of_freq.get(c, 0) + 1
    s = sum(v * (i ** 2) for i, v in freq_of_freq.items())
    return round(10_000 * (s - n) / (n * n), 1) if n else 0.0


def mtld(toks: list[str], threshold: float = 0.72) -> float:
    """Length-robust lexical diversity (McCarthy & Jarvis). Higher = richer. Human prose ~70-100."""
    if len(toks) < 10:
        return 0.0

    def _pass(seq: list[str]) -> float:
        factors = 0.0
        types: set[str] = set()
        count = 0
        for t in seq:
            count += 1
            types.add(t)
            if len(types) / count <= threshold:
                factors += 1
                types, count = set(), 0
        if count > 0:
            ttr = len(types) / count
            factors += (1 - ttr) / (1 - threshold)
        return len(seq) / factors if factors else len(seq)

    return round((_pass(toks) + _pass(toks[::-1])) / 2, 1)


def _cv(xs: list[int]) -> float:
    if len(xs) < 2:
        return 0.0
    m = sum(xs) / len(xs)
    if not m:
        return 0.0
    sd = math.sqrt(sum((x - m) ** 2 for x in xs) / len(xs))
    return sd / m


# --------------------------------------------------------------------------- #
# Voice fingerprint (capture)                                                  #
# --------------------------------------------------------------------------- #

FUNCTION_WORDS = frozenset((
    "the", "a", "an", "and", "but", "or", "so", "of", "to", "in", "for", "on",
    "with", "as", "that", "this", "these", "those", "it", "is", "was", "are",
    "were", "be", "been", "being", "am", "i", "you", "your", "we", "our", "they",
    "them", "their", "he", "she", "his", "her", "him", "its", "my", "me", "us",
    "at", "by", "from", "into", "onto", "over", "under", "out", "up", "down",
    "off", "than", "then", "when", "where", "which", "who", "whom", "what",
    "have", "has", "had", "do", "does", "did", "will", "would", "could", "should",
    "can", "may", "might", "must", "not", "no", "if", "because", "while", "about",
    "just", "also", "very", "much", "more", "most", "some", "any", "all", "like",
    "there", "here", "how", "why", "get", "got", "one", "two", "make", "made",
))


def profile(raw: str) -> dict:
    text = strip_markdown(raw)
    sents = split_sentences(text)
    w = words(text)
    lengths = [len(words(s)) for s in sents if words(s)]
    mean = sum(lengths) / len(lengths) if lengths else 0
    sd = math.sqrt(sum((x - mean) ** 2 for x in lengths) / len(lengths)) if lengths else 0
    toks = [x.lower() for x in w]
    counts: dict[str, int] = {}
    for t in toks:
        counts[t] = counts.get(t, 0) + 1
    content = {k: v for k, v in counts.items()
               if k not in FUNCTION_WORDS and len(k) > 3}
    top_content = sorted(content.items(), key=lambda kv: -kv[1])[:12]
    syll = sum(count_syllables(x) for x in w) if w else 0
    return {
        "words": len(w),
        "sentences": len(sents),
        "mean_sentence_len": round(mean, 1),
        "sentence_len_stdev": round(sd, 1),
        "burstiness_cv": round(sd / mean, 2) if mean else 0,
        "shortest_sentence": min(lengths) if lengths else 0,
        "longest_sentence": max(lengths) if lengths else 0,
        "avg_word_len": round(sum(len(x) for x in w) / len(w), 2) if w else 0,
        "syllables_per_word": round(syll / len(w), 2) if w else 0,
        "type_token_ratio": round(len(set(toks)) / len(toks), 2) if toks else 0,
        "mtld": mtld(toks),
        "yules_k": yules_k(toks),
        "hapax_rate": hapax_rate(toks),
        "contractions_per_sentence": round(len(CONTRACTION.findall(text)) / max(1, len(sents)), 2),
        "commas_per_sentence": round(text.count(",") / max(1, len(sents)), 2),
        "em_dashes_per_100w": round(len(EM_DASH.findall(text)) / max(1, len(w)) * 100, 2),
        "flesch_reading_ease": flesch_reading_ease(text, sents),
        "fk_grade": fk_grade(text, sents),
        "top_content_words": [k for k, _ in top_content],
    }


def profile_target_line(p: dict) -> str:
    return (f"Target voice: ~{p['mean_sentence_len']:.0f}-word sentences "
            f"(range {p['shortest_sentence']}-{p['longest_sentence']}, "
            f"burstiness CV {p['burstiness_cv']}), "
            f"{p['contractions_per_sentence']} contractions/sentence, "
            f"reading ease ~{p['flesch_reading_ease']:.0f}, "
            f"{p['commas_per_sentence']} commas/sentence.")


# --------------------------------------------------------------------------- #
# CLI / rendering                                                              #
# --------------------------------------------------------------------------- #

BAR = "─" * 56


def render(report: Report) -> str:
    lines = [BAR,
             f" Human Voice Score: {report.score}/100  ({report.grade})",
             BAR]
    s = report.stats
    lines.append(f" {s.get('words', 0)} words · {s.get('sentences', 0)} sentences · "
                 f"avg {s.get('mean_len', '?')} w/sent · burstiness CV {s.get('cv', '?')}")
    lines.append(f" reading ease {s.get('flesch_reading_ease', '?')} · "
                 f"TTR {s.get('type_token_ratio', '?')} · "
                 f"em-dashes {s.get('em_dashes_per_100w', '?')}/100w · "
                 f"contractions {s.get('contractions_per_sentence', '?')}/sent")
    if report.by_category:
        lines.append("")
        lines.append(" Penalty by category (higher = more slop):")
        for cat, pen in sorted(report.by_category.items(), key=lambda kv: -kv[1]):
            lines.append(f"   {cat:<12} -{pen}")
    if report.findings:
        lines.append("")
        lines.append(f" Findings ({len(report.findings)}):")
        order = {3: 0, 2: 1, 1: 2}
        for f in sorted(report.findings, key=lambda x: (order[x.severity], x.category)):
            mark = {3: "!!", 2: "! ", 1: "· "}[f.severity]
            loc = f" (line {f.line})" if f.line else ""
            lines.append(f"  {mark} [{f.category}]{loc} {f.message}")
            if f.excerpt:
                lines.append(f"        ↳ {f.excerpt}")
    else:
        lines.append("\n No structural tells found. Read it aloud anyway.")
    lines.append(BAR)
    return "\n".join(lines)


def read_input(path: str) -> str:
    if path == "-" or path is None:
        return sys.stdin.read()
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="deslop",
        description="Score prose on how human vs. AI-generated it reads, and flag the spans.")
    ap.add_argument("file", nargs="?", default="-",
                    help="file to analyze, or - for stdin (default)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--quiet", "-q", action="store_true", help="print only the score line")
    ap.add_argument("--profile", action="store_true",
                    help="extract the writer's style fingerprint (voice capture)")
    ap.add_argument("--min-score", type=int, default=None,
                    help="exit non-zero if score is below this threshold (for CI / loops)")
    args = ap.parse_args(argv)

    try:
        raw = read_input(args.file)
    except OSError as e:
        print(f"deslop: cannot read {args.file}: {e}", file=sys.stderr)
        return 2

    if not raw.strip():
        print("deslop: empty input", file=sys.stderr)
        return 2

    if args.profile:
        p = profile(raw)
        if args.json:
            print(json.dumps(p, indent=2))
        else:
            print(BAR)
            print(" Voice fingerprint")
            print(BAR)
            for k, v in p.items():
                if k == "top_content_words":
                    print(f" {k:<26} {', '.join(v)}")
                else:
                    print(f" {k:<26} {v}")
            print(BAR)
            print(" " + profile_target_line(p))
            print(BAR)
        return 0

    report = analyze(raw)

    if args.json:
        print(json.dumps({"score": report.score, "grade": report.grade,
                          "stats": report.stats, "by_category": report.by_category,
                          "findings": [f.to_dict() for f in report.findings]}, indent=2))
    elif args.quiet:
        print(f"{report.score}/100 ({report.grade})")
    else:
        print(render(report))

    if args.min_score is not None and report.score < args.min_score:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
