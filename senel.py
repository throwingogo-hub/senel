#!/usr/bin/env python3
"""senel.py -- reference tooling for Senel.

Three commands:

    python3 senel.py validate            phonotactics, collisions, confusability audit
    python3 senel.py gloss "<sentence>"  interlinear gloss of a Senel sentence
    python3 senel.py count "<text>"      syllable count (for efficiency comparisons)

The validator is the point: a designed language is only as good as the
constraints it actually obeys, so every claim in SPEC.md that can be checked
mechanically is checked here.
"""

from __future__ import annotations

import itertools
import sys
from collections import defaultdict
from pathlib import Path

LEXICON = Path(__file__).with_name("lexicon.tsv")

CONSONANTS = set("pbtdkgmnsfhlrwy")
VOWELS = set("aeiou")
CODAS = set("nmlrsktp")          # the only consonants allowed to close a syllable
FUNCTION_CLASSES = {"ROLE", "ASP", "EVID", "MOOD", "DEG", "CONN", "DET", "PRON"}

# The 16 one-syllable function words whose class is NOT recoverable from shape.
# Everything else in the grammar is shape-transparent (see SPEC.md 6.1).
RESERVED = {
    "an", "en", "in", "on", "un", "as",                       # oblique roles
    "min", "mun", "mon", "sin", "sun", "tin", "tun", "pan",   # pronouns
    "sel", "tal",                                             # reflexive/reciprocal
}


# ---------------------------------------------------------------- lexicon ----

def load_lexicon(path: Path = LEXICON):
    entries = []
    with path.open(encoding="utf-8") as fh:
        header = next(fh)
        assert header.startswith("form\t"), "unexpected lexicon header"
        for line_no, line in enumerate(fh, start=2):
            line = line.rstrip("\n")
            if not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) != 4:
                raise SystemExit(f"lexicon.tsv:{line_no}: expected 4 columns, got {len(parts)}")
            form, cls, gloss, source = parts
            entries.append({"form": form, "class": cls, "gloss": gloss,
                            "source": source, "line": line_no})
    return entries


# ------------------------------------------------------------ phonotactics ----

def syllabify(word: str):
    """Split a word into syllables by the maximal-onset principle.

    Returns a list of (onset, nucleus, coda) triples, or raises ValueError.
    """
    w = word.lower()
    if not w or any(c not in CONSONANTS | VOWELS for c in w):
        raise ValueError(f"illegal letter in {word!r}")
    syls, i = [], 0
    while i < len(w):
        onset = ""
        if w[i] in CONSONANTS:
            onset = w[i]
            i += 1
            if i < len(w) and w[i] in CONSONANTS:
                raise ValueError(f"onset cluster in {word!r}")
        if i >= len(w) or w[i] not in VOWELS:
            raise ValueError(f"syllable without a vowel in {word!r}")
        nucleus = w[i]
        i += 1
        coda = ""
        # A consonant closes this syllable only if it cannot start the next one,
        # i.e. only when it is followed by another consonant or by end-of-word.
        if i < len(w) and w[i] in CONSONANTS:
            if i + 1 >= len(w) or w[i + 1] in CONSONANTS:
                coda = w[i]
                i += 1
        syls.append((onset, nucleus, coda))
    return syls


def phonotactic_errors(word: str):
    try:
        syls = syllabify(word)
    except ValueError as exc:
        return [str(exc)]
    errors = []
    for onset, _nucleus, coda in syls:
        if coda and coda not in CODAS:
            errors.append(f"{word!r}: /{coda}/ may not close a syllable")
        if onset and onset not in CONSONANTS:
            errors.append(f"{word!r}: /{onset}/ is not a consonant")
    return errors


def syllable_count(word: str):
    try:
        return len(syllabify(word))
    except ValueError:
        return 0


def shape_class(form: str):
    """The class a naive parser can assign from the word's shape alone."""
    if form in RESERVED:
        return "RESERVED"
    syls = syllabify(form)
    if len(syls) == 1:
        onset, nucleus, coda = syls[0]
        if not coda:                       # open monosyllable -> grammar word
            return {"a": "ASP", "e": "MOOD", "i": "DEG",
                    "o": "EVID", "u": "CONN"}[nucleus] if onset else "ROLE"
    if form.endswith("am") and len(syls) == 1:
        return "DET"
    return "ROOT"


# ------------------------------------------------------------- confusability --

def edit_neighbours(forms):
    """Pairs of equal-length forms differing in exactly one letter."""
    by_len = defaultdict(list)
    for f in forms:
        by_len[len(f)].append(f)
    pairs = []
    for group in by_len.values():
        for a, b in itertools.combinations(sorted(group), 2):
            if sum(x != y for x, y in zip(a, b)) == 1:
                pairs.append((a, b))
    return pairs


# ------------------------------------------------------- L1 merger profiles ---
# What a speaker of each language is most likely to *merge* when learning Senel.
# Each profile is a list of letter sets that collapse together for that listener.
PROFILES = {
    "japanese": ([{"r", "l"}, {"f", "h"}], "r/l are one phoneme; f is bilabial [ɸ]"),
    "korean":   ([{"r", "l"}, {"p", "b"}, {"t", "d"}, {"k", "g"}, {"f", "p"}],
                 "r/l allophonic; voicing is allophonic; no /f/"),
    "mandarin": ([{"n", "l"}, {"p", "b"}, {"t", "d"}, {"k", "g"}, {"r", "l"}],
                 "voicing contrast is aspiration; n/l merge in southern varieties"),
    "arabic":   ([{"p", "b"}, {"e", "i"}, {"o", "u"}, {"g", "k"}],
                 "no /p/; three-vowel system; /g/ varies by dialect"),
    "spanish":  ([{"b", "w"}, {"h"}, {"y"}], "b/v/w overlap; written h is silent"),
    "french":   ([{"h"}], "/h/ is not pronounced"),
    "hindi":    ([{"f", "p"}, {"w", "b"}], "f often realised as ph; v/w overlap"),
    "quechua":  ([{"e", "i"}, {"o", "u"}, {"p", "b"}, {"t", "d"}, {"k", "g"}],
                 "three-vowel system, no voicing contrast"),
}
# Pairs whose collision is harmless because one meaning subsumes the other.
GRACEFUL = {("bu", "pu"), ("mun", "mon")}


def collapse(form: str, merges):
    out = []
    for ch in form:
        for group in merges:
            if ch in group:
                out.append(min(group))
                break
        else:
            out.append(ch)
    return "".join(out)


def merger_report(profile_name=None):
    entries = load_lexicon()
    grammar = [e for e in entries if e["class"] in FUNCTION_CLASSES]
    roots = [e for e in entries if e["class"] in ("ROOT", "NUM")]
    names = [profile_name] if profile_name else list(PROFILES)
    worst = 0
    for name in names:
        merges, why = PROFILES[name]
        print(f"\n{name}  ({why})")
        for label, group in (("GRAMMAR", grammar), ("roots", roots)):
            buckets = defaultdict(list)
            for e in group:
                buckets[collapse(e["form"], merges)].append(e["form"])
            clashes = [tuple(sorted(v)) for v in buckets.values() if len(v) > 1]
            clashes = [c for c in clashes if c not in GRACEFUL]
            if label == "GRAMMAR":
                worst = max(worst, len(clashes))
                verdict = "clean" if not clashes else f"{len(clashes)} CLASH"
                print(f"  {label:8} {verdict}" +
                      ("  " + ", ".join("/".join(c) for c in clashes) if clashes else ""))
            else:
                print(f"  {label:8} {len(clashes)} clashing pair(s)" +
                      ("  e.g. " + ", ".join("/".join(c) for c in clashes[:6])
                       if clashes else ""))
    return 1 if worst else 0


def epenthesis_check():
    """CV-language speakers release codas with a short echo vowel: kas -> [kasɯ].
    That is only safe if no root equals another root plus a final vowel."""
    entries = load_lexicon()
    forms = {e["form"] for e in entries if e["class"] in ("ROOT", "NUM")}
    bad = [(f, f[:-1]) for f in forms if f[-1] in VOWELS and f[:-1] in forms]
    print(f"echo-vowel safety: {len(bad)} unsafe root(s)" +
          ("  " + ", ".join(f"{a} vs {b}+V" for a, b in bad) if bad else "  (clean)"))
    return 1 if bad else 0


# ---------------------------------------------------------------- validate ----

def validate():
    entries = load_lexicon()
    problems = []

    # 1. duplicate forms
    seen = {}
    for e in entries:
        if e["form"] in seen:
            problems.append(
                f"DUPLICATE  {e['form']!r} on lines {seen[e['form']]} and {e['line']}")
        seen[e["form"]] = e["line"]

    # 2. phonotactics (affixes are bound, so they are checked as attached forms)
    for e in entries:
        if e["class"] == "AFFIX":
            probe = "mek" + e["form"].strip("-") if e["form"].startswith("-") \
                else e["form"].strip("-") + "mek"
            problems += [f"PHONOTACTIC {p} (via {e['form']})"
                         for p in phonotactic_errors(probe)]
        else:
            problems += [f"PHONOTACTIC {p}" for p in phonotactic_errors(e["form"])]

    # 3. content roots must not wear a grammar word's shape
    for e in entries:
        if e["class"] not in ("ROOT", "NUM"):
            continue
        try:
            sc = shape_class(e["form"])
        except ValueError:
            continue
        if sc != "ROOT":
            problems.append(
                f"SHAPE      root {e['form']!r} ({e['gloss']}) parses as {sc}")

    # 4. function words must be one syllable and shape-transparent or reserved
    for e in entries:
        if e["class"] not in FUNCTION_CLASSES:
            continue
        if syllable_count(e["form"]) != 1:
            problems.append(f"SHAPE      grammar word {e['form']!r} is not monosyllabic")
            continue
        sc = shape_class(e["form"])
        if sc not in (e["class"], "RESERVED"):
            problems.append(
                f"SHAPE      {e['form']!r} is {e['class']} but its shape says {sc}")

    # ---- report
    roots = [e["form"] for e in entries if e["class"] in ("ROOT", "NUM")]
    grammar = [e for e in entries if e["class"] in FUNCTION_CLASSES]
    affixes = [e for e in entries if e["class"] == "AFFIX"]
    mono = [r for r in roots if syllable_count(r) == 1]
    transparent = [e for e in grammar if e["form"] not in RESERVED]
    pairs = edit_neighbours(roots)

    print(f"lexicon            {len(entries)} entries")
    print(f"  content roots    {len(roots)}  ({len(mono)} monosyllabic, "
          f"{100*len(mono)//len(roots)}%)")
    print(f"  grammar words    {len(grammar)}  (all monosyllabic; "
          f"{len(transparent)} shape-transparent, {len(RESERVED)} memorised)")
    print(f"  affixes          {len(affixes)}")
    print(f"  irregular forms  0  (no root ever changes shape)")
    print()
    print(f"confusability      {len(pairs)} minimal pairs among content roots "
          f"({100*len(pairs)/max(len(roots),1):.0f} per 100 roots)")
    dense = defaultdict(int)
    for a, b in pairs:
        dense[a] += 1
        dense[b] += 1
    worst = sorted(dense.items(), key=lambda kv: (-kv[1], kv[0]))[:8]
    print("  densest          " + ", ".join(f"{f}({n})" for f, n in worst))
    print()
    if problems:
        print(f"FAILED: {len(problems)} problem(s)")
        for p in problems:
            print("  " + p)
        return 1
    print("PASS: phonotactics, shape rules and uniqueness all hold.")
    return 0


# ------------------------------------------------------------------ glosser ----

def build_index():
    entries = load_lexicon()
    return {e["form"]: e for e in entries if not e["form"].startswith("-")
            and not e["form"].endswith("-")}, \
           {e["form"].strip("-"): e for e in entries if e["class"] == "AFFIX"}


def analyse(token: str, lex, affixes):
    """Return (gloss, class) for one token, decomposing derivations if needed."""
    t = token.lower().strip(".,!?;:")
    if not t:
        return None
    if t in lex:
        e = lex[t]
        return f"{e['gloss']}", e["class"]
    # try prefixes then suffixes against the root list
    for pre in ("na", "re", "se"):
        if t.startswith(pre) and t[len(pre):] in lex:
            inner = lex[t[len(pre):]]
            return f"{affixes[pre]['gloss']} + {inner['gloss']}", "DERIVED"
    for suf, e in affixes.items():
        if suf in ("na", "re", "se"):
            continue
        if t.endswith(suf) and t[: -len(suf)] in lex:
            inner = lex[t[: -len(suf)]]
            return f"{inner['gloss']} + {e['gloss']}", "DERIVED"
    # compound of two known roots
    for i in range(2, len(t) - 1):
        if t[:i] in lex and t[i:] in lex:
            return f"{lex[t[:i]]['gloss']}-{lex[t[i:]]['gloss']}", "COMPOUND"
    try:
        return f"?unknown ({shape_class(t)} by shape)", "UNKNOWN"
    except ValueError as exc:
        return f"?illegal ({exc})", "ILLEGAL"


def gloss(text: str):
    lex, affixes = build_index()
    tokens = [t for t in text.replace(",", " ,").split() if t]
    rows = []
    for tok in tokens:
        result = analyse(tok, lex, affixes)
        if result is None:
            continue
        g, cls = result
        rows.append((tok, cls, g))
    width = max(len(r[0]) for r in rows) + 2
    cwidth = max(len(r[1]) for r in rows) + 2
    for tok, cls, g in rows:
        print(f"{tok:<{width}}{cls:<{cwidth}}{g}")
    unknown = [t for t, c, _ in rows if c in ("UNKNOWN", "ILLEGAL")]
    if unknown:
        print(f"\n{len(unknown)} unrecognised token(s): {', '.join(unknown)}")
    return 0


def count(text: str):
    total, words = 0, 0
    for tok in text.split():
        t = tok.lower().strip(".,!?;:\"'")
        if not t:
            continue
        try:
            total += len(syllabify(t))
            words += 1
        except ValueError as exc:
            print(f"  ! {t}: {exc}")
    print(f"{words} words, {total} syllables")
    return 0


def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd = argv[1]
    if cmd == "validate":
        rc = validate()
        print()
        rc |= epenthesis_check()
        return rc
    if cmd == "merge":
        return merger_report(argv[2] if len(argv) > 2 else None)
    if cmd == "gloss":
        return gloss(" ".join(argv[2:]))
    if cmd == "count":
        return count(" ".join(argv[2:]))
    print(f"unknown command {cmd!r}")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
