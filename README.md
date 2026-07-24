<h1 align="center">Senel</h1>

<p align="center">
  <b>A constructed language where the sound of a word is derived from its meaning.</b><br>
  No borrowed vocabulary. No irregular forms. The whole grammar is 65 one-syllable words.
</p>

<p align="center">
  <a href="https://github.com/throwingogo-hub/senel/actions/workflows/validate.yml"><img alt="validate" src="https://github.com/throwingogo-hub/senel/actions/workflows/validate.yml/badge.svg"></a>
  <img alt="roots" src="https://img.shields.io/badge/roots-559-blue">
  <img alt="irregular forms" src="https://img.shields.io/badge/irregular%20forms-0-brightgreen">
  <img alt="license" src="https://img.shields.io/badge/license-MIT-lightgrey">
</p>

<p align="center">
  <a href="https://throwingogo-hub.github.io/senel/"><b>→ Try the translator in your browser ←</b></a>
</p>

---

## The idea

In every human language, the sound of a word tells you nothing about its meaning.
*Dog*, *perro*, *chien*, *狗* — all arbitrary, all memorised one at a time. That
arbitrariness is the single largest cost in learning any language.

In Senel, a word is **built out of its meaning**:

```
   t      i      l    →   til   "dog"
   │      │      │
   │      │      └────── which item in that set
   │      └───────────── subdomain: familiar animals
   └──────────────────── domain: living kinds
```

So you don't memorise 559 unrelated words. You learn **16 domains**, and the rest
decodes itself:

| | | | | |
|---|---|---|---|---|
| **k‑** parts | `kal` head | `kas` eye | `kak` ear | `kap` mouth |
| **b‑** motion | `bal` go | `bar` come | `bas` stop | `bek` climb |
| **t‑** living kinds | `tar` tree | `til` dog | `tir` cat | `tel` bird |
| **y‑** time | `yen` day | `yel` night | `yer` year | `yal` now |
| **l‑** light & weather | `lin` sun | `lol` rain | `lul` fire | `lel` cold |

Hear a word you've never met beginning with `m`? It's about the mind. With `f`? Feeling
or value. No natural language can do that.

## Every sentence says how you know it

One syllable, mandatory on every statement:

```
Lol ka lo.    It's raining — I can see it.
Lol ka to.    It's raining — someone told me.
Lol ka mo.    It's raining — I infer it (wet umbrellas).
Lol ka yo.    It rains here — established fact.
```

English needs *"apparently"*, *"I heard"*, *"it seems"* — and usually just drops them,
leaving you to guess. In Senel, dropping it is ungrammatical.

## Numbers have a trick

```
al 1   ak 2   at 3   ap 4   os 5
                              ↓  a → o adds five
ol 6   ok 7   ot 8   op 9   om 0
```

`ak` 2 → `ok` 7. `at` 3 → `ot` 8. Then `il` 10, `ik` 100, `it` 1000 — so `ak il at` = 23.
No teens, no irregular tens, no long-scale/short-scale billion problem.

## The entire grammar

65 one-syllable words. Nothing else exists — no conjugation, no declension, no
agreement, no gender, no articles, **no irregular anything**. And the vowel of a grammar
word tells you its category before you know the word:

| Vowel | Category | Examples |
|---|---|---|
| bare | role | `a` agent · `e` object · `o` to · `i` at · `u` by |
| `‑a` | aspect | `ta` completed · `ka` ongoing · `fa` about to |
| `‑e` | mood | `ne` not · `he` question · `we` command |
| `‑i` | degree | `mi` more · `ti` most · `bi` very |
| `‑o` | evidence | `lo` seen · `to` told · `mo` inferred |
| `‑u` | connective | `nu` and · `hu` if · `du` then · `ku` because |

Word order is Subject–Verb–Object, and role markers are *optional* in that order —
you only pay for word-order freedom when you actually use it.

## Say something

```
Min bal fa so.              I'm about to go.            [my own intent]
Til em i pin en sin lo.     Your house has a dog.       [I saw it]
Sin fen he?                 Are you happy?
Pe mun hen tal.             Let's eat together.
Til es mi ur an tir lo.     The dog is bigger than the cat.
```

## There's a translator

**[throwingogo-hub.github.io/senel](https://throwingogo-hub.github.io/senel/)** — English
⇄ Senel, running entirely in your browser. No server, no network requests, no API key.

It is rule-based rather than statistical, which for this language is the right choice:
Senel was designed to be unambiguous, so Senel → English is close to exact. English →
Senel is the hard direction. Its front end now expands contractions, tests several
plausible lemmas instead of blindly stripping suffixes, performs longest-phrase matching,
and builds transparent Senel derivations and compounds where possible. Everyday
vocabulary — food, animals, colours, the body, family, weather — is covered the way the
language itself works: `lunch` is `yenhem` ("day-meal"), `red` is `ninkel`
("colour-of-blood"), `son` is `relrom` ("male-child"), all composed from existing roots
rather than borrowed. The catalogue contains more than 1,100 English expressions while
the language itself remains almost entirely the same 559-root system.

English also omits things Senel requires — and rather than quietly guessing, the
translator tells you what it had to decide:

> **English 'we' is ambiguous; Senel requires a choice.** Used `mon` (we, NOT including
> you) — swap to `mun` to include them.

> **Senel requires an evidential; guessed `lo` (you witnessed it).** Use `to` if told,
> `mo` if inferred, `yo` if general knowledge, `so` if internal.

Every translation also comes with a word-by-word breakdown showing which semantic domain
each word came from, so the page teaches the system while it translates. A concept that
is genuinely absent is preserved honestly as `«a quoted foreign term»`; strict mode uses
`[untranslated]` instead. In the browser, each unresolved term also receives a concept
resolver: the user may map it deliberately to any existing English–Senel concept and the
sentence is reanalysed with that choice. Neither mode silently assigns an invented meaning.

From the terminal:

```bash
python3 translate.py en2sn "I am going to your house."
# Min bal ka o pin en sin lo.

python3 translate.py sn2en "Til em i pin en sin lo."
# The dog exists at the building of you.  [I saw it]

python3 translate.py en2sn --strict "An unknownword remains."
# [unknownword] bas lo.
```

## Try it in 30 seconds

```bash
git clone https://github.com/throwingogo-hub/senel.git && cd senel
python3 senel.py validate                # prove the language obeys its own rules
python3 senel.py gloss "Lol ka mo."      # interlinear gloss
python3 senel.py count "Ran lam har fum nu es i fom nu rum yo."
python3 senel.py merge japanese          # which words collapse for a given L1's ear
python3 build_lexicon.py                 # regenerate all 559 roots from the semantic map
python3 translate.py en2sn "I don't know."
python3 tests/test_examples.py           # every example in the docs must parse
python3 tests/test_translation.py        # contractions, morphology and fallback regressions
python3 tests/test_coverage.py           # representative everyday-English coverage gate
python3 tests/test_parity.py             # the Python and browser translators must agree
```

No dependencies. Python 3 standard library only.

## It's checked, not asserted

The vocabulary isn't a hand-written list — it's **generated** from a semantic map in
[`build_lexicon.py`](build_lexicon.py), and every structural claim is verified in CI:

```
lexicon            638 entries
  content roots    559  (559 monosyllabic, 100%)
  grammar words    65   (all monosyllabic)
  irregular forms  0    (no root ever changes shape)

PASS: phonotactics, shape rules and uniqueness all hold.
echo-vowel safety: 0 unsafe root(s)  (clean)
```

`senel.py merge` goes further and simulates a listener whose first language can't
distinguish two given sounds, reporting exactly which words collapse. The grammar was
then designed around the results — for example the "or" pair `bu`/`pu` sits deliberately
on a contrast that some listeners merge, because collapsing *inclusive or* into
*exclusive or* yields vagueness rather than a wrong reading.

## Measured

Universal Declaration of Human Rights, Article 1:

| | Syllables |
|---|---|
| English original | 44 |
| **Senel** | **25** (−43%) |

| Learning load | Senel | English |
|---|---|---|
| Irregular verb forms | 0 | ~200 |
| Irregular plurals | 0 | ~100 |
| Grammar words | 65 | ~150 |
| Spelling–sound rules | 20 | several hundred |
| Arbitrary root meanings | **0** | all of them |

## What it's worse at

A design document that only lists wins is advertising. Senel's real costs:

- **Noise.** A systematic vocabulary puts related meanings in adjacent sound-space.
  The validator counts 6,202 one-phoneme-apart root pairs. 42% of those errors land in
  the same domain (a recoverable near-miss like `kas` eye → `kak` ear), but 58% change
  the first consonant and therefore the topic. English is more redundant and survives a
  bad phone line better. This is the direct cost of the compression.
- **Speech rate.** Denser syllables get pronounced more slowly. A 43% syllable saving
  will not become 43% less time.
- **No idiom, no register, no honorifics.** Politeness has to be said outright.
- **Adoption.** Design quality has never been what decides whether a constructed
  language gets used. Nothing here changes that.

Also worth saying plainly: **no language can be "more efficient than all others" in
every sense.** Measured speech carries roughly the same information rate in every
language studied. What can genuinely be optimised is learning load, written
compression, parse ambiguity and irregularity — which is what this project targets.

## Read more

- **[SPEC.md](SPEC.md)** — complete reference grammar: phonology, the full semantic map,
  every grammar word, subordination, numbers, and the measurements
- **[COOKBOOK.md](COOKBOOK.md)** — how to build any word (reuse, derive, compound) and
  say complex sentences, with the productive patterns
- **[lexicon.tsv](lexicon.tsv)** — all 638 entries with their derivations
- **[examples/phrasebook.md](examples/phrasebook.md)** — everyday phrases, with literal glosses
- **[CONTRIBUTING.md](CONTRIBUTING.md)** — how to add roots without breaking the system

## License

MIT. Use it, fork it, teach it to something.
