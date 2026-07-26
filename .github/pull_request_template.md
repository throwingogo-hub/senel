## What changed

<!-- Describe one focused change and the user-facing reason for it. -->

## Type

- [ ] Translator behaviour or coverage
- [ ] Learn mode or browser UI
- [ ] Documentation or examples
- [ ] Language design (link the accepted proposal issue)
- [ ] Tests or developer tooling

## Verification

- [ ] `python3 build_lexicon.py && git diff --exit-code lexicon.tsv`
- [ ] `python3 senel.py validate`
- [ ] `python3 tests/test_examples.py`
- [ ] `python3 tests/test_translation.py`
- [ ] `python3 tests/test_coverage.py`
- [ ] `python3 translate.py data && git diff --exit-code docs/data.js docs/aliases.js`
- [ ] `python3 tests/test_parity.py`
- [ ] I tested the browser UI at a relevant desktop and mobile width when the UI changed.

## Generated-file and claim checks

- [ ] I edited source files, not `lexicon.tsv`, `docs/data.js`, or `docs/aliases.js` directly.
- [ ] New Senel examples are covered by `tests/test_examples.py`.
- [ ] Any quantitative language claim is reproducible from repository tooling.
- [ ] Unknown English concepts remain explicit rather than being mapped approximately.

## Screenshots or examples

<!-- For UI work, add before/after screenshots. For translator work, add exact input/output. -->
