#!/usr/bin/env python3
"""Focused regressions for English normalisation and fallback behaviour."""

from __future__ import annotations

import re
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import translate  # noqa: E402


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"])
        if tag == "script" and values.get("src"):
            self.scripts.append(values["src"])


def sn(text: str, strict=False) -> str:
    return translate.en2sn(text, strict=strict)[0]


def main() -> int:
    # Contractions and their expanded forms must be identical.
    assert sn("I'm going to the office.") == sn("I am going to the office.")
    assert sn("I can't repair the computer.") == sn("I cannot repair the computer.")

    # Candidate-based lemmatisation must recover real lemmas, not truncate blindly.
    hated = sn("I hated the black dog.")
    assert "fap" in hated and "ninnir" in hated and "[" not in hated
    assert "hat" not in hated.lower()

    # -er agent nouns are not comparatives; -ing nouns remain nouns outside verb context.
    assert sn("The runner returned.").startswith("Belra bak ta")
    assert sn("The worker is building a house.").startswith("Ril gen ka")
    assert sn("The building is old.").startswith("Pin es yum")

    # Productive Senel morphology is used rather than inventing roots.
    rebuilt, notes = translate.en2sn("I am rebuilding the classroom.")
    assert "regen ka" in rebuilt
    assert any("productive" in note for note in notes)

    # Longest-match aliases and semantic compounds outrank shorter grammar words.
    assert "de" in sn("I am ready for sure.").split()
    assert sn("The smartphone is black.").startswith("Persil es ninnir")

    # Ability no longer mistranslates as pot 'clay'.
    ability = sn("You can repair the computer.")
    assert " gol " in f" {ability.lower()} " and " pot " not in f" {ability.lower()} "
    assert "can repair the computer" in translate.sn2en(ability)[0].lower()

    # Unknown terms have an honest practical fallback and an inspectable strict mode.
    practical, practical_notes = translate.en2sn("I am gooning for sure.")
    assert "«gooning»" in practical and " ka " not in f" {practical.lower()} "
    assert any("quoted foreign term" in note for note in practical_notes)
    strict = sn("An unknownword remains.", strict=True)
    assert "[unknownword]" in strict
    assert "unknownword" in translate.sn2en(strict)[0].lower()

    # Curated reverse names make common compounds readable again without overriding
    # the semantic map's part of speech for primitive roots.
    assert translate.sn2en("Permen es ninnir lo.")[0].startswith("The computer is black")
    assert translate.sn2en("Min mis lo.")[0].startswith("I study")

    # The browser UI must expose strict mode and deliberate unknown-term resolution,
    # with generated data loaded before the translator rules.
    parser = PageParser()
    parser.feed((ROOT / "docs" / "index.html").read_text(encoding="utf-8"))
    assert {"strictMode", "unknownResolver", "unknownItems", "conceptList"} <= parser.ids
    assert parser.scripts[-4:] == ["data.js", "aliases.js", "app.js", "ui.js"]

    # The browser's embedded alias source must be byte-for-byte synced with the TSV.
    aliases_js = (ROOT / "docs" / "aliases.js").read_text(encoding="utf-8")
    match = re.search(r"raw: `(.*?)`,\n  contractions:", aliases_js, re.S)
    assert match, "aliases.js no longer exposes its generated TSV block"
    assert match.group(1) == (ROOT / "english_aliases.tsv").read_text(encoding="utf-8")

    # The pre-existing large browser data file must remain reproducible.
    with tempfile.TemporaryDirectory() as tmp:
        generated = Path(tmp) / "data.js"
        translate.export_data(generated)
        assert generated.read_bytes() == (ROOT / "docs" / "data.js").read_bytes()

    print("PASS: contractions, morphology, aliases, compounds, foreign fallback and web data.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
