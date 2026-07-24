#!/usr/bin/env python3
"""Coverage and validity gates for ordinary English input."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import senel  # noqa: E402
import translate  # noqa: E402


def read_words(path: Path):
    words, seen = [], set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        for word in line.split():
            if word not in seen:
                seen.add(word)
                words.append(word)
    return words


def check_word_list(lex, affixes) -> int:
    """Every everyday word must translate without a «quoted» or [bracketed] fallback."""
    words = read_words(ROOT / "tests" / "common_words.txt")
    assert len(words) >= 400, f"common word list shrank to {len(words)} words"
    missing, invalid = [], []
    for word in words:
        output, _ = translate.en2sn(word)
        if "«" in output or "[" in output:
            missing.append(word)
        for token in re.findall(r"[A-Za-z]+", output):
            _, kind = senel.analyse(token.lower(), lex, affixes)
            if kind in ("UNKNOWN", "ILLEGAL"):
                invalid.append((word, token))
    for word in missing:
        print(f"UNCOVERED everyday word: {word}")
    for word, token in invalid:
        print(f"INVALID Senel {token!r} for word {word!r}")
    assert not missing, f"{len(missing)} everyday words fall back to a quote/bracket"
    assert not invalid, f"{len(invalid)} invalid Senel tokens generated for everyday words"
    return len(words)


def main() -> int:
    corpus = [line.strip() for line in
              (ROOT / "tests" / "coverage_corpus.txt").read_text(encoding="utf-8").splitlines()
              if line.strip() and not line.startswith("#")]
    assert len(corpus) >= 50, "coverage corpus became too small"

    catalog = translate.build_english_catalog()
    assert len(catalog) >= 1100, f"English catalogue shrank to {len(catalog)} entries"

    total_tokens = 0
    unknown_tokens = []
    invalid_senel = []
    lex, affixes = senel.build_index()

    for sentence in corpus:
        total_tokens += len(translate.normalise_english(sentence))
        output, _ = translate.en2sn(sentence, strict=True)
        unknown = re.findall(r"\[([^\]]+)\]", output)
        unknown_tokens.extend((sentence, word) for word in unknown)
        for token in re.findall(r"[A-Za-z]+", output):
            _, kind = senel.analyse(token.lower(), lex, affixes)
            if kind in ("UNKNOWN", "ILLEGAL"):
                invalid_senel.append((sentence, token, output))

    unknown_rate = len(unknown_tokens) / total_tokens
    if unknown_tokens:
        for sentence, word in unknown_tokens:
            print(f"UNKNOWN {word!r}: {sentence}")
    if invalid_senel:
        for sentence, token, output in invalid_senel:
            print(f"INVALID {token!r}: {sentence}\n  {output}")

    assert total_tokens >= 300, "coverage corpus has too few tokens"
    assert unknown_rate <= 0.05, f"unknown-token rate {unknown_rate:.1%} exceeds 5%"
    assert not invalid_senel, f"{len(invalid_senel)} invalid Senel tokens generated"

    word_count = check_word_list(lex, affixes)

    print(f"PASS: {len(corpus)} sentences, {total_tokens} English tokens, "
          f"{len(unknown_tokens)} unknown ({unknown_rate:.1%}); "
          f"{word_count} everyday words all covered; every Senel token parses.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
