#!/usr/bin/env python3
"""Every Senel sentence printed in the documentation must actually parse.

Two checks per example:
  1. every token resolves to a word, a derivation or a compound
  2. the sentence really appears in README.md or SPEC.md, so the docs and the
     test list cannot drift apart
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import senel  # noqa: E402

EXAMPLES = [
    # README
    "Lol ka lo.",
    "Lol ka to.",
    "Lol ka mo.",
    "Lol ka yo.",
    "Min bal fa so.",
    "Til em i pin en sin lo.",
    "Sin fen he?",
    "Pe mun hen tal.",
    "Til es mi ur an tir lo.",
    # SPEC
    "Til nal sin lo.",
    "Min bal ta.",
    "Min bal ka.",
    "Min bal ma.",
    "Min bal fa.",
    "Min bal sa.",
    "Fen so.",
    "Sin nal ta til he?",
    "Min mal fu sin bal ta lo.",
    "Til fin lo.",
    "Ran lam har fum nu es i fom nu rum yo.",
]


def main():
    lex, affixes = senel.build_index()
    # Interlinear examples in the docs are padded for column alignment, so compare
    # with whitespace collapsed, and allow the final period to be absent.
    docs = " ".join("\n".join((ROOT / f).read_text(encoding="utf-8")
                              for f in ("README.md", "SPEC.md")).split())
    failures = []

    for sentence in EXAMPLES:
        for token in sentence.split():
            gloss, cls = senel.analyse(token, lex, affixes)
            if cls in ("UNKNOWN", "ILLEGAL"):
                failures.append(f"{sentence!r}: token {token!r} -> {gloss}")
        flat = " ".join(sentence.split())
        if flat not in docs and flat.rstrip(".?") not in docs:
            failures.append(f"{sentence!r} is in the test list but not in the docs")

    if failures:
        print(f"FAILED: {len(failures)} problem(s)")
        for f in failures:
            print("  " + f)
        return 1
    total = sum(len(s.split()) for s in EXAMPLES)
    print(f"PASS: {len(EXAMPLES)} documented examples, {total} tokens, all parse.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
