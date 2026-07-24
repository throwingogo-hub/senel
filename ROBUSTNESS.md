# Noise-robustness: the one real cost, measured

Senel's central idea — a word's sound is built from its meaning — has a direct price:
related meanings sit next to each other in sound-space, so the lexicon is full of words
that are one slip-of-the-ear apart. This document measures exactly how bad it is and lays
out what could be done, without pretending the problem away. Run the numbers yourself:

```bash
python3 senel.py robust
```

## The measurement

Among **559 roots** there are **6,327 minimal pairs** (two roots differing by exactly one
letter). What matters is *which* letter:

| Difference | Consequence | Count | Share |
|---|---|---|---|
| **onset** (`bal`/`mal`) | different **domain** — the topic changes | 3,566 | **56%** |
| vowel (`ben`/`bon`) | different subdomain | 1,021 | 16% |
| coda (`kas`/`kak`) | same subdomain — a recoverable near-miss | 1,624 | 25% |

The design *wants* the coda case (eye→ear is a survivable near-miss). The problem is the
56%: an onset error turns `bal` (go) into `mal` (know) into `nal` (see) — a different
domain entirely, which context often cannot repair.

It is structural, not incidental. Because every root is `CVC` and the onset carries the
domain, the words that share a vowel+coda form a family that differs *only* in the first
consonant. Six families have **15 members each**:

```
-ar: bar dar far gar har kar lar mar nar par rar sar tar war yar
-ak: bak dak fak gak hak kak lak mak nak pak rak sak tak wak yak
```

The most connected roots — `hen` (eat), `ken` (heart), `ren` (parent) — each have **25**
one-phoneme neighbours. Weighting by use makes it worse, not better: **760** minimal
pairs are between *two common words* whose topics differ (`go`/`know`/`see`/`want`).

## What already protects against it

- **Digits break the scheme on purpose** — they are the most acoustically separated words
  in the language, because a misheard number is expensive.
- **The item sits in the weakest position** (coda), so the most likely error is the
  recoverable within-subdomain one.
- **`senel.py merge`** simulates a given L1's mergers; the grammar was designed to stay
  collision-free under every profile except two deliberately graceful pairs.
- **Echo-vowel safety** is checked, so CV-language speakers can release codas safely.

None of that touches the 56% onset problem. That is the open issue.

## Options (they trade against the core idea — pick by goal)

**A. Accept it — Senel is a precision / written language.** Spelling is unambiguous;
context and the obligatory evidential disambiguate. This is the honest current stance.
*Cost: none new. Keeps everything. Just not robust on a bad phone line.*

**B. Protect the high-frequency core.** Reassign the ~40 most-used roots so no two common
words are a minimal pair — e.g. give the top verbs distinct, widely-separated forms the
way digits already are. *Cost: those words stop being decodable from the semantic map, and
existing text changes. This is the biggest departure from the thesis, for the biggest
robustness gain.*

**C. Add controlled redundancy.** Lengthen only the highest-frequency roots to two
syllables (a redundant echo of the domain), or define a disambiguating particle used only
in noisy contexts. *Cost: gives back some of the −43% length win, but only on common
words, and only when needed.*

**D. Thin the dense families.** Spread the most common meanings across *different* vowels
and codas so the top-frequency words aren't all in one rhyme family. *Cost: smaller than B;
weakens the "same subdomain = same vowel" regularity a little.*

## Decision: Option A

Senel is an **art project and a teaching tool**, not a spoken auxiliary language.
**Option A is adopted.** The forms are left intact and the noise-robustness cost is
measured here rather than engineered away.

This is not a deferral — it is the coherent choice for what Senel is. The whole project
is an argument that vocabulary *can* be derived from meaning, stated honestly including
its price (SPEC §0 and §9). The 56% onset-collision figure is not a defect to hide; it is
the measured cost of the compression, and for an art project reporting it *is* the
integrity of the piece, while for a teaching tool the tension between density and
robustness *is* the lesson. Re-engineering the forms to look robust would falsify the
one thing the project exists to demonstrate.

Options B–D stay on record. If Senel is ever repurposed as a spoken language — where
robustness stops being optional — B or C becomes necessary, and this analysis is the
starting point. Until then, the forms do not change.
