#!/usr/bin/env python3
"""The web translator and translate.py must produce identical output.

There are two implementations because the browser cannot run Python. All the
vocabulary tables are generated into docs/data.js by `translate.py data`, so
only the rules are written twice — and this test is what stops those from
drifting apart.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import translate  # noqa: E402


def main():
    cases = json.loads((ROOT / "tests" / "parity_cases.json").read_text())
    try:
        js = json.loads(subprocess.run(
            ["node", str(ROOT / "tests" / "parity.js")],
            capture_output=True, text=True, check=True).stdout)
    except FileNotFoundError:
        print("SKIP: node is not installed, cannot check parity")
        return 0
    except subprocess.CalledProcessError as exc:
        print("FAILED: the browser translator did not run\n" + exc.stderr)
        return 1

    mismatches = []
    for sentence in cases["en"]:
        expected, _ = translate.en2sn(sentence)
        if js["en2sn"][sentence] != expected:
            mismatches.append((sentence, expected, js["en2sn"][sentence]))
    for sentence in cases.get("enStrict", []):
        expected, _ = translate.en2sn(sentence, strict=True)
        if js["en2snStrict"][sentence] != expected:
            mismatches.append((sentence + " [strict]", expected,
                               js["en2snStrict"][sentence]))
    for sentence in cases["sn"]:
        expected, _ = translate.sn2en(sentence)
        if js["sn2en"][sentence] != expected:
            mismatches.append((sentence, expected, js["sn2en"][sentence]))

    if mismatches:
        print(f"FAILED: {len(mismatches)} disagreement(s) between Python and JS")
        for src, py, node in mismatches:
            print(f"  {src!r}\n    python: {py!r}\n    js:     {node!r}")
        return 1
    total = len(cases["en"]) + len(cases.get("enStrict", [])) + len(cases["sn"])
    print(f"PASS: {total} sentences translate identically in Python and JavaScript.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
