# Changelog

Senel follows semantic versions for the public language/tooling milestones. Generated
files remain derived artifacts: edit the semantic map or translator sources, regenerate,
and let CI prove that the committed outputs match.

## 1.9.0 — 2026-07-24

This is the first GitHub release candidate.

### Highlights

- Added a zero-install **Learn** mode beside the browser translator.
- Added an explorable map of all 16 semantic domains.
- Added a decoding drill with root breakdowns and a local streak counter.
- Added a robustness lesson that exposes the dense rhyme families and links to the full
  measured analysis.
- Kept the core language unchanged at 559 roots and 65 grammar words.

### Since the initial public version

- Expanded the English concept catalogue beyond 1,100 expressions with transparent
  aliases, derivations, and compounds rather than borrowed Senel vocabulary.
- Added contraction handling, candidate lemmatisation, longest-phrase matching, strict
  and practical unknown-word modes, and a deliberate in-browser concept resolver.
- Improved Senel-to-English possessives, comparatives, question inversion, and idiomatic
  rendering without changing Senel grammar.
- Added the vocabulary cookbook and a reproducible noise-robustness audit.
- Gated lexicon and browser-data reproducibility, documentation examples, translator
  regressions, everyday-English coverage, and Python/JavaScript parity in GitHub Actions.

### Known limits

- English-to-Senel translation must supply distinctions English omits, including
  evidential source and inclusive/exclusive “we”; the interface reports those choices.
- Unknown concepts remain visibly quoted or bracketed instead of receiving guessed
  meanings.
- Senel's systematic sound space is less tolerant of noise than English. This is an
  accepted design cost for an art project and teaching tool; see
  [ROBUSTNESS.md](ROBUSTNESS.md).

### Release verification

Run the same gates as CI before tagging `v1.9.0`:

```bash
python3 build_lexicon.py && git diff --exit-code lexicon.tsv
python3 senel.py validate
python3 tests/test_examples.py
python3 tests/test_translation.py
python3 tests/test_coverage.py
python3 translate.py data && git diff --exit-code docs/data.js docs/aliases.js
python3 tests/test_parity.py
```

The release has no binary assets: the translator and Learn lab are available on
[GitHub Pages](https://throwingogo-hub.github.io/senel/), while the Python tools run from
the source archive with Python 3 and no third-party dependencies.
