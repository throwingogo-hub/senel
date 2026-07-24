# Contributing to Senel

The language has one hard rule: **no word is ever invented arbitrarily.** A root's
sound is a consequence of its meaning. If you keep that, everything else follows.

## Do not edit `lexicon.tsv`

It is generated. Edit [`build_lexicon.py`](build_lexicon.py) — the semantic map is the
real source — then run:

```bash
python3 build_lexicon.py
python3 senel.py validate
python3 tests/test_examples.py
python3 tests/test_translation.py
python3 tests/test_coverage.py
python3 tests/test_parity.py
```

CI regenerates the lexicon and fails if the committed file differs, so a hand-edit will
be caught.

## Extending English translator coverage

Do not add a Senel root merely because an English surface form is missing. First decide
whether it is a synonym, inflection, idiom, transparent derivation, compound or genuinely
new concept.

- Add synonyms, idioms and canonical English renderings to
  [`english_aliases.tsv`](english_aliases.tsv). Everyday concepts are best expressed as
  **compounds of existing roots**, the same way the language builds them — `lunch` is
  `yenhem` (`yen` day + `hem` meal), `red` is `ninkel` (`nin` colour + `kel` blood),
  `son` is `relrom` (`rel` child + `rom` male). Store the concatenated form (e.g.
  `lunch  noun  yenhem`); it is recognised as a `COMPOUND` and reverse-glosses back to
  the canonical English word. Reach for a new root only when no composition is honest.
- Never edit `docs/aliases.js` by hand: it is generated. After editing the TSV (or any
  English table such as `MODALS`), run `python3 translate.py data`, which regenerates
  both `docs/data.js` and `docs/aliases.js`. CI diffs both, and
  `tests/test_translation.py` asserts the embedded TSV block is byte-identical.
- Add representative sentences to `tests/coverage_corpus.txt`; the unknown-token rate
  may not exceed 5%, and every generated Senel token must parse.
- Add everyday words to `tests/common_words.txt`; `tests/test_coverage.py` requires
  every one of them to translate without a `«quoted»` or `[bracketed]` fallback.
- Add semantic edge cases to `tests/parity_cases.json`, so Python and JavaScript cannot
  diverge on contractions, morphology, compounds or fallback behaviour.

Unknown concepts must remain explicit: practical mode quotes them with `«…»`; strict mode
uses `[…]`. Never map an unfamiliar word to an approximate concept merely to suppress a
warning.

## Adding a root

1. **Find its domain** (first consonant). 16 exist; the concept must genuinely belong
   to one. If it doesn't fit any, that is interesting — open an issue rather than
   forcing it.
2. **Find its subdomain** (vowel), among the five in that domain.
3. **Take a free coda.** `-em -im -om -um` are free in every domain, since only `C-am`
   is reserved for determiners. Use the `EXTRA` table for these.
4. Put contrasts that listeners commonly confuse on **semantically adjacent** members,
   so a mishearing produces vagueness rather than a wrong meaning.

Before proposing a new root, check whether derivation already covers it. `henwa`
(eat-place) needs no root. Neither does `nafum` (not-free). Roots are for concepts that
cannot be composed.

## Adding a domain or subdomain

Much higher bar. The 16 domains use all 15 consonants plus the zero onset, so a new
domain means displacing an existing one. Expect to argue for it in an issue first.

## Changing grammar words

The 65 grammar words are chosen so that **no two collide under any single common L1
merger profile**. Before changing one, run:

```bash
python3 senel.py merge
```

and confirm the `GRAMMAR` line still reads `clean` for every profile except the pairs
listed as deliberately graceful. A change that makes `hu` (if) collide with `fu` (that)
for some listener is a regression even if it looks tidier on paper.

## Documentation

Every Senel sentence printed in `README.md` or `SPEC.md` must appear in the list in
[`tests/test_examples.py`](tests/test_examples.py), which checks both that it parses and
that it really occurs in the docs. Docs and tests cannot drift.

## Claims

Any efficiency claim in the docs must be reproducible with a command in the repo. If
you cannot show it with `senel.py`, do not write it down. The project's credibility
rests on the fact that the numbers can be re-run, including the unflattering ones — the
confusability count and the noise-robustness cost stay in the README.
