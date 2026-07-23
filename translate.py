#!/usr/bin/env python3
"""translate.py -- bidirectional English <-> Senel translation.

    python3 translate.py en2sn "I am going to your house."
    python3 translate.py sn2en "Til em i pin en sin lo."
    python3 translate.py data                # emit docs/data.js for the web UI

This is rule-based, not statistical. Senel was designed to be unambiguous, so
Senel -> English is close to exact. English -> Senel is the hard direction:
English leaves things out that Senel requires (how you know a claim, whether
"we" includes the listener), so the translator makes a choice and *tells you*
it made one. Every guess appears as a note rather than being hidden.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import senel  # noqa: E402

# --------------------------------------------------------------- English side --

# English words with no single gloss in the lexicon, or where the natural English
# word maps onto a derived Senel form. Value is the Senel output.
SUPPLEMENT = {
    # derived properties
    "big": "urgo", "large": "urgo", "huge": "urgo", "small": "urdi",
    "little": "urdi", "tiny": "urdi", "long": "wopgo", "short": "wopdi",
    "tall": "wosgo", "heavy": "gorgo", "deep": "wokgo",
    "easy": "nagom", "simple": "nagom", "quick": "yun", "quickly": "yun",
    "hot": "len", "warm": "lep", "cool": "lel",
    # common nouns that live under a broader gloss
    "house": "pin", "home": "pin", "building": "pin", "room": "pil",
    "food": "henko", "meal": "hem", "drink": "helko", "book": "sem",
    "toilet": "huswa", "school": "ros", "shop": "rok", "market": "rok",
    "man": "ran rom", "woman": "ran rem", "boy": "rel rom", "girl": "rel rem",
    "teacher": "ris", "student": "rir", "doctor": "rik", "worker": "ril",
    "restaurant": "henwa", "library": "semwa", "sunlight": "linlan",
    # verbs
    "walk": "ben", "run": "bel", "speak": "sil", "talk": "sil", "get": "dat",
    "look": "nal", "watch": "nal", "listen": "nar", "understand": "map",
    "work": "gun", "study": "mis", "become": "gar", "seem": "par",
    "want": "fal", "need": "far", "like": "fas", "love": "fat", "hate": "fap",
    "begin": "gak", "start": "gak", "finish": "gup", "stay": "bas",
    "put": "bin", "wear": "hut", "cook": "hep", "wash": "hun", "buy": "del",
    "sell": "der", "pay": "des", "help": "run", "wait": "bas",
    # bare adjectives that are stative verbs in Senel
    "happy": "fen", "sad": "fel", "angry": "fes", "afraid": "fer",
    "tired": "nuk", "hungry": "nur", "thirsty": "nus", "sick": "hol",
    "ill": "hol", "well": "hon", "healthy": "hon", "beautiful": "nim",
    "important": "fik", "useful": "fit", "correct": "fir", "wrong": "fis",
    "good": "fin", "bad": "fil", "new": "yim", "old": "yum",
    "difficult": "gom", "hard": "gom", "free": "fum", "clean": "hul",
    "dirty": "hur", "loud": "nol", "quiet": "nor", "bright": "nil",
    "dark": "nir", "far": "wol", "near": "won", "same": "es",
    "different": "ek", "true": "el", "false": "er",
    # deictic time and place
    "yesterday": "yen yin", "today": "yen sam", "tomorrow": "yen yil",
    "now": "yal", "here": "sam wan", "there": "tam wan", "again": "yok",
    "always": "yon", "never": "yol", "often": "yor", "sometimes": "yos",
}

# Part of speech by (domain, subdomain). Used to decide where articles go and
# which token is the verb. Derived from the semantic map, not guessed per word.
VERBAL = {
    ("b", "a"), ("b", "e"), ("b", "i"), ("b", "u"),
    ("d", "a"), ("d", "i"), ("d", "u"), ("d", "e"),
    ("g", "a"), ("g", "e"), ("g", "i"), ("g", "u"),
    ("m", "a"), ("m", "e"), ("m", "i"),
    ("n", "a"), ("s", "a"), ("s", "i"),
    ("f", "a"), ("f", "u"),
    ("h", "a"), ("h", "e"), ("h", "i"), ("h", "u"),
    ("l", "a"), ("l", "e"), ("l", "o"), ("r", "u"), ("", "e"),
}
PROPERTY = {
    ("f", "e"), ("f", "i"), ("f", "o"), ("n", "i"), ("n", "o"), ("n", "u"),
    ("y", "u"), ("w", "o"), ("w", "e"), ("b", "o"), ("y", "o"), ("p", "u"),
    ("y", "i"),
}


def pos_of(form: str, cls: str) -> str:
    """noun / verb / property, from where the root sits in the semantic map."""
    if cls in ("NUM",):
        return "num"
    if cls != "ROOT":
        return "gram"
    if len(form) == 2:
        onset, vowel = "", form[0]
    else:
        onset, vowel = form[0], form[1]
    if (onset, vowel) in VERBAL:
        return "verb"
    if (onset, vowel) in PROPERTY:
        return "property"
    return "noun"

PRONOUNS = {
    "i": "min", "me": "min", "my": "min", "mine": "min", "myself": "sel",
    "you": "sin", "your": "sin", "yours": "sin", "yourself": "sel",
    "he": "tin", "him": "tin", "his": "tin", "she": "tin", "her": "tin",
    "hers": "tin", "it": "tin", "its": "tin", "himself": "sel",
    "herself": "sel", "itself": "sel",
    "they": "tun", "them": "tun", "their": "tun", "theirs": "tun",
    "themselves": "sel", "one": "pan", "each other": "tal",
    "one another": "tal", "together": "tal",
}
# "we" needs a decision Senel forces and English does not.
WE = {"we": "mon", "us": "mon", "our": "mon", "ours": "mon", "ourselves": "sel"}

DETERMINERS = {
    "this": "sam", "these": "sam", "that": "tam", "those": "tam",
    "some": "kam", "all": "lam", "every": "lam", "each": "lam",
    "many": "pam", "much": "pam", "few": "fam", "several": "fam",
    "no": "yam", "none": "yam", "any": "wam", "which": "nam", "what": "nam",
}

PREPOSITIONS = {
    "to": "o", "toward": "o", "towards": "o", "at": "i", "in": "i", "on": "i",
    "inside": "i", "during": "i", "by": "u", "with": "on", "using": "u",
    "from": "an", "of": "en", "for": "in", "because of": "un",
    "about": "en", "into": "o", "onto": "o", "out of": "an",
}

CONNECTIVES = {
    "and": "nu", "or": "bu", "but": "wu", "however": "wu", "if": "hu",
    "then": "du", "so": "du", "therefore": "du", "because": "ku",
    "although": "ru", "though": "ru", "that": "fu", "who": "gu",
    "which": "gu", "whom": "gu",
}

DEGREE = {
    "more": "mi", "less": "li", "most": "ti", "least": "li", "as": "si",
    "equally": "si", "too": "ki", "enough": "fi", "very": "bi",
    "really": "bi", "extremely": "bi", "quite": "bi",
}

# Auxiliaries and how they set aspect / mood.
ASPECT_WORDS = {
    "will": "fa", "shall": "fa", "gonna": "fa",
    "usually": "sa", "always": "sa", "often": "sa", "sometimes": "sa",
    "already": "ma",
}
MODALS = {"can": "pot", "could": "pot", "must": "gum", "should": "gum",
          "have to": "gum", "has to": "gum", "need to": "far",
          "may": "fus", "might": "fus", "would": None}

COPULA = {"is", "am", "are", "was", "were", "be", "been", "being"}
HAVE = {"have", "has", "had", "having"}
DO_SUPPORT = {"do", "does", "did"}
NEGATORS = {"not", "n't", "never", "no"}
DROP = {"the", "a", "an", "there", "please", "just", "actually"}

IRREGULAR_VERBS = {
    "went": "go", "gone": "go", "goes": "go", "going": "go",
    "came": "come", "coming": "come", "saw": "see", "seen": "see",
    "seeing": "see", "said": "say", "saying": "say", "told": "tell",
    "telling": "tell", "made": "make", "making": "make", "took": "take",
    "taken": "take", "taking": "take", "gave": "give", "given": "give",
    "giving": "give", "got": "get", "gotten": "get", "getting": "get",
    "ate": "eat", "eaten": "eat", "eating": "eat", "drank": "drink",
    "drunk": "drink", "drinking": "drink", "slept": "sleep",
    "sleeping": "sleep", "knew": "know", "known": "know", "knowing": "know",
    "thought": "think", "thinking": "think", "felt": "feel",
    "feeling": "feel", "heard": "hear", "hearing": "hear", "ran": "run",
    "running": "run", "wrote": "write", "written": "write",
    "writing": "write", "read": "read", "bought": "buy", "buying": "buy",
    "sold": "sell", "selling": "sell", "paid": "pay", "paying": "pay",
    "built": "build", "building": "build", "broke": "break",
    "broken": "break", "left": "leave", "leaving": "leave", "met": "meet",
    "meeting": "meet", "found": "find", "finding": "find", "lost": "lose",
    "losing": "lose", "began": "begin", "begun": "begin",
    "understood": "understand", "children": "child", "people": "person",
    "men": "man", "women": "woman", "feet": "foot", "teeth": "tooth",
    "wanted": "want", "needed": "need", "helped": "help", "worked": "work",
    "lived": "live", "died": "die", "loved": "love", "liked": "like",
}

WH = {"who": "ran nam", "where": "wan nam", "when": "yan nam",
      "what": "um nam", "why": "un nam", "how": "u nam",
      "how many": "ul nam", "how much": "ul nam", "whose": "en ran nam"}

PAST_CUES = {"yesterday", "ago", "last", "earlier", "previously", "before"}
HEARSAY_CUES = {"apparently", "reportedly", "supposedly", "allegedly"}
INFER_CUES = {"probably", "presumably", "evidently", "must", "seems", "seem"}
OPINION_VERBS = {"think", "believe", "feel", "want", "need", "like", "love",
                 "hate", "hope", "intend", "prefer", "doubt", "guess"}


def lemma(word: str) -> str:
    if word in IRREGULAR_VERBS:
        return IRREGULAR_VERBS[word]
    for suf, repl in (("ies", "y"), ("ing", ""), ("ed", ""), ("es", ""), ("s", "")):
        if word.endswith(suf) and len(word) - len(suf) >= 3:
            stem = word[: len(word) - len(suf)] + repl
            return stem
    return word


def build_english_index():
    """English phrase -> Senel form, taken from the lexicon's own glosses."""
    index = {}
    for entry in senel.load_lexicon():
        if entry["class"] not in ("ROOT", "NUM"):
            continue
        for phrase in entry["gloss"].split(", "):
            phrase = re.sub(r"\s*\(.*?\)", "", phrase).strip().lower()
            if phrase and phrase not in index:
                index[phrase] = entry["form"]
    index.update(SUPPLEMENT)
    return index


# ------------------------------------------------------------ English -> Senel --

def en2sn(text: str):
    index = build_english_index()
    notes, out = [], []
    raw = text.strip()
    is_question = raw.endswith("?")
    words = re.findall(r"[a-z']+", raw.lower().replace("n't", " not"))
    if not words:
        return "", notes

    aspect = None
    negate = False
    modal = None
    evidential = None
    lead_wh = None
    subject_first_person = False
    has_opinion_verb = False

    # ---- scan for grammatical signals before translating anything
    joined = " ".join(words)
    for cue in HEARSAY_CUES:
        if cue in words:
            evidential = "to"
    for cue in INFER_CUES:
        if cue in words:
            evidential = "mo"
    if any(w in PAST_CUES for w in words):
        aspect = "ta"
    for i, w in enumerate(words):
        if w in ("is", "am", "are", "was", "were") and i + 1 < len(words) \
                and words[i + 1].endswith("ing"):
            aspect = "ka"
        if w in HAVE and i + 1 < len(words) and words[i + 1] not in COPULA:
            nxt = words[i + 1]
            if nxt.endswith("ed") or nxt in IRREGULAR_VERBS:
                aspect = "ma"
        if w in ("was", "were") or (w.endswith("ed") and lemma(w) != w):
            aspect = aspect or "ta"
        if w in ASPECT_WORDS:
            aspect = ASPECT_WORDS[w]
        if w in NEGATORS:
            negate = True
        if w in MODALS and MODALS[w]:
            modal = MODALS[w]
        if lemma(w) in OPINION_VERBS:
            has_opinion_verb = True

    if words[0] in ("i", "we"):
        subject_first_person = True
    for wh, sn in sorted(WH.items(), key=lambda kv: -len(kv[0])):
        if joined.startswith(wh):
            lead_wh = sn
            words = words[len(wh.split()):]
            break

    # ---- word-by-word, longest phrase first
    i = 0
    pending_possessor = None
    while i < len(words):
        w = words[i]
        # Auxiliaries, articles and negators are consumed by the grammar above and
        # must never reach the dictionary — English "do" is not Senel gan.
        if w in DROP or w in DO_SUPPORT or w in HAVE or w in NEGATORS \
                or w in ASPECT_WORDS or w in COPULA:
            if w in COPULA and not any(x.endswith("ing") for x in words[i + 1:]):
                out.append("es")
            i += 1
            continue
        if w == "than":
            out.append("an")
            i += 1
            continue
        cmp_form = _comparative(w, index)
        if cmp_form:
            out += cmp_form
            i += 1
            continue
        matched = False
        for span in (3, 2, 1):
            phrase = " ".join(words[i: i + span])
            if not phrase:
                continue
            for table in (PREPOSITIONS, CONNECTIVES, DEGREE, DETERMINERS,
                          PRONOUNS, WE, MODALS):
                if phrase in table:
                    val = table[phrase]
                    if table is WE:
                        notes.append(
                            "English 'we' is ambiguous; Senel requires a choice. "
                            "Used mon (we, NOT including you) — swap to mun to include them.")
                    if table is MODALS and val is None:
                        matched = True
                        i += span
                        break
                    if table is PRONOUNS and phrase in ("my", "your", "his",
                                                        "her", "its", "their"):
                        pending_possessor = val
                        matched = True
                        i += span
                        break
                    if table is WE and phrase in ("our", "ours"):
                        pending_possessor = val
                        matched = True
                        i += span
                        break
                    if table is MODALS:
                        matched = True
                        i += span
                        break
                    out.append(val)
                    matched = True
                    i += span
                    break
            if matched:
                break
            if phrase in index:
                out.append(index[phrase])
                if pending_possessor:
                    out += ["en", pending_possessor]
                    pending_possessor = None
                matched = True
                i += span
                break
            base = lemma(phrase)
            if base in index:
                out.append(index[base])
                if pending_possessor:
                    out += ["en", pending_possessor]
                    pending_possessor = None
                matched = True
                i += span
                break
        if matched:
            continue
        notes.append(f"no Senel word for '{w}' yet — left as [{w}]")
        out.append(f"[{w}]")
        i += 1

    if pending_possessor:
        out += ["en", pending_possessor]

    # ---- assemble
    if lead_wh:
        if out and out[0] == "es":
            out.pop(0)
        out = out + (["em", "i", "wan", "nam"] if lead_wh == "wan nam"
                     else lead_wh.split())
    if modal:
        out.insert(max(0, _verb_slot(out)), modal)
    if negate:
        out.insert(max(0, _verb_slot(out)), "ne")
    if aspect:
        out.insert(min(len(out), _verb_slot(out) + 1 + (1 if negate else 0)), aspect)

    if is_question or lead_wh:
        out.append("he")
    else:
        if evidential is None:
            if subject_first_person and has_opinion_verb:
                evidential = "so"
            elif aspect == "sa":
                evidential = "yo"
            else:
                evidential = "lo"
                notes.append(
                    "Senel requires an evidential; guessed lo (you witnessed it). "
                    "Use to if told, mo if inferred, yo if general knowledge, so if internal.")
        out.append(evidential)

    sentence = " ".join(out)
    return sentence[:1].upper() + sentence[1:] + ("?" if is_question or lead_wh else "."), notes


IRREGULAR_COMPARATIVE = {
    "better": ["mi", "fin"], "best": ["ti", "fin"],
    "worse": ["mi", "fil"], "worst": ["ti", "fil"],
    "further": ["mi", "wol"], "furthest": ["ti", "wol"],
    "elder": ["mi", "yum"], "eldest": ["ti", "yum"],
}


def _comparative(word: str, index):
    """bigger -> ['mi','ur'] ; biggest -> ['ti','ur']. Returns None if not one."""
    if word in IRREGULAR_COMPARATIVE:
        return list(IRREGULAR_COMPARATIVE[word])
    for suffix, particle in (("est", "ti"), ("er", "mi")):
        if not word.endswith(suffix) or len(word) - len(suffix) < 3:
            continue
        stem = word[: len(word) - len(suffix)]
        for candidate in (stem, stem + "e", stem[:-1] if len(stem) > 3
                          and stem[-1] == stem[-2] else stem):
            if candidate in index:
                form = index[candidate]
                # big -> urgo, but "bigger" is better said "more size" than
                # "more large-size", so peel a size suffix back off.
                if form.endswith(("go", "di")) and len(form) > 4:
                    form = form[:-2]
                return [particle] + form.split()
    return None


def _verb_slot(tokens):
    """Index of the first token that behaves like the main verb."""
    lex, _ = senel.build_index()
    for idx, tok in enumerate(tokens):
        entry = lex.get(tok)
        if entry and entry["class"] == "ROOT":
            return idx
    return len(tokens)


# ------------------------------------------------------------ Senel -> English --

EVID_EN = {"lo": "[I saw it]", "to": "[I was told]", "so": "[my own state]",
           "mo": "[I infer it]", "yo": "[established knowledge]"}
ROLE_EN = {"o": "to", "i": "at", "u": "by", "an": "from", "en": "of",
           "on": "with", "in": "for", "un": "because of", "as": "as for",
           "a": None, "e": None}
PRON_EN = {"min": ("I", "me"), "sin": ("you", "you"), "tin": ("it", "it"),
           "sun": ("you", "you"), "tun": ("they", "them"),
           "mun": ("we (including you)", "us (including you)"),
           "mon": ("we (not including you)", "us (not including you)"),
           "pan": ("one", "one"), "sel": ("oneself", "oneself"),
           "tal": ("each other", "each other")}
ROOT_EN = {"em": "exist", "es": "is", "gan": "do"}
IRREGULAR_PAST = {"go": "went", "come": "came", "see": "saw", "say": "said",
                  "tell": "told", "make": "made", "do": "did", "take": "took",
                  "give": "gave", "get": "got", "eat": "ate", "drink": "drank",
                  "sleep": "slept", "know": "knew", "think": "thought",
                  "feel": "felt", "hear": "heard", "run": "ran",
                  "write": "wrote", "buy": "bought", "sell": "sold",
                  "pay": "paid", "build": "built", "break": "broke",
                  "leave": "left", "meet": "met", "find": "found",
                  "lose": "lost", "begin": "began", "is": "was",
                  "there is": "there was", "be born": "was born",
                  "understand": "understood", "hold": "held"}


def _clean(gloss: str) -> str:
    gloss = re.sub(r"\s*\(.*?\)", "", gloss)
    return re.split(r"[,;]", gloss)[0].strip()


def _head(fn):
    """Apply an inflection to the first word of a multi-word gloss."""
    def wrapper(verb: str) -> str:
        head, sep, rest = verb.partition(" ")
        return fn(head) + sep + rest
    return wrapper


def _ing(verb: str) -> str:
    if verb.endswith("e") and not verb.endswith("ee"):
        return verb[:-1] + "ing"
    if len(verb) > 2 and verb[-1] not in "aeiouwxy" and verb[-2] in "aeiou" \
            and verb[-3] not in "aeiou":
        return verb + verb[-1] + "ing"
    return verb + "ing"


def _past(verb: str) -> str:
    if verb in IRREGULAR_PAST:
        return IRREGULAR_PAST[verb]
    if verb == "be":
        return "was"
    if verb.endswith("e"):
        return verb + "d"
    return verb + "ed"


IRREGULAR_PLURAL = {"person": "people", "child": "children", "man": "men",
                    "woman": "women", "foot": "feet", "tooth": "teeth"}


def _third(verb: str) -> str:
    if verb in ("is", "there is"):
        return verb
    if verb == "be":
        return "is"
    if verb.endswith(("s", "sh", "ch", "x", "o")):
        return verb + "es"
    return verb + "s"


_ing, _past, _third = _head(_ing), _head(_past), _head(_third)


def sn2en(text: str):
    lex, affixes = senel.build_index()
    notes = []
    recs = []
    evidential, question, imperative, tag = "", False, False, ""

    for tok in re.findall(r"[A-Za-z]+", text):
        low = tok.lower()
        entry = lex.get(low)
        cls = entry["class"] if entry else None
        if cls == "EVID":
            evidential = EVID_EN[low]
            continue
        if cls == "MOOD":
            if low == "he":
                question = True
            elif low == "we":
                imperative = True
            elif low == "ne":
                recs.append({"kind": "neg"})
            elif low == "pe":
                recs.insert(0, {"kind": "word", "text": "let"})
                tag = "hortative"
            elif low == "ge":
                tag = "hypothetically"
            elif low == "de":
                tag = "indeed"
            elif low == "ye":
                tag = "right?"
            continue
        if cls == "ASP":
            recs.append({"kind": "asp", "asp": low})
            continue
        if cls == "ROLE":
            role = ROLE_EN.get(low)
            if role:
                recs.append({"kind": "word", "text": role})
            continue
        if cls in ("CONN", "DEG", "DET"):
            recs.append({"kind": cls.lower(), "text": _clean(entry["gloss"]),
                         "form": low})
            continue
        if cls == "PRON":
            recs.append({"kind": "pron", "form": low})
            continue
        gloss, kind = senel.analyse(low, lex, affixes)
        if kind in ("UNKNOWN", "ILLEGAL"):
            notes.append(f"'{tok}' is not a Senel word")
            recs.append({"kind": "word", "text": f"[{tok}]"})
            continue
        if kind == "DERIVED":
            base, _, mod = gloss.partition(" + ")
            recs.append({"kind": "derived", "text": f"{_clean(base)} ({_clean(mod)})",
                         "pos": "noun"})
            continue
        if kind == "COMPOUND":
            recs.append({"kind": "derived", "text": _clean(gloss).replace("-", " "),
                         "pos": "noun"})
            continue
        recs.append({"kind": "root", "form": low, "pos": pos_of(low, cls),
                     "text": ROOT_EN.get(low, _clean(entry["gloss"]))})

    # a determiner or property that follows its noun moves in front of it, as English
    # requires; the first verb-like root is the predicate and stays put
    verb_idx = next((n for n, r in enumerate(recs)
                     if r["kind"] == "root" and r.get("pos") == "verb"), None)
    if verb_idx is None:
        verb_idx = next((n for n, r in enumerate(recs)
                         if r["kind"] == "root" and r.get("pos") == "property"), None)
    out, n = [], 0
    while n < len(recs):
        r = recs[n]
        if r["kind"] == "root" and r.get("pos") == "noun":
            mods = []
            m = n + 1
            while m < len(recs) and (recs[m]["kind"] == "det" or
                                     (recs[m]["kind"] == "root"
                                      and recs[m].get("pos") == "property"
                                      and m != verb_idx)):
                mods.append(recs[m]["text"])
                m += 1
            head = r["text"]
            if r["form"][0] == "y" or any(m in ("before", "after", "during")
                                          for m in mods):
                head = " ".join([head] + mods)
                mods = []
            determined = any(
                w in ("this", "that", "these", "those", "all", "every", "some",
                      "many", "few", "no", "any", "which", "what")
                for mod in mods for w in mod.split())
            if not determined:
                mods.insert(0, "the")
            if any(m in ("all", "many", "few", "some") for m in mods):
                head = IRREGULAR_PLURAL.get(head, head + ("" if head.endswith("s")
                                                          else "s"))
            out.append(" ".join(mods + [head]))
            n = m
            continue
        out.append(r)
        n += 1

    # realise
    words, i, subject, predicate_done = [], 0, None, False
    negated = any(r["kind"] == "neg" for r in recs if isinstance(r, dict))
    aspect = next((r["asp"] for r in recs if isinstance(r, dict)
                   and r["kind"] == "asp"), None)
    for item in out:
        if isinstance(item, str):
            if subject is None:
                subject = item
            words.append(item)
            continue
        k = item["kind"]
        if k in ("asp", "neg"):
            continue
        if k == "pron":
            form = PRON_EN[item["form"]]
            after_let = bool(words) and words[-1] == "let"
            words.append(form[1] if (subject is not None or after_let) else form[0])
            if subject is None:
                subject = item["form"]
            continue
        if k == "root" and item.get("pos") in ("verb", "property"):
            verb = item["text"]
            if predicate_done:                # complement of an earlier predicate
                words.append(verb)
                continue
            predicate_done = True
            if subject is None:          # weather and existentials need a subject
                words.append("it")
                subject = "tin"
            plural = subject in ("tun", "sun", "mun", "mon") or (
                isinstance(subject, str) and (
                    subject.endswith("s")
                    or subject.split()[0].lower() in ("all", "many", "few", "some")
                    or subject.split()[-1] in IRREGULAR_PLURAL.values()))
            third_sg = subject == "tin" or (isinstance(subject, str)
                                            and subject not in PRON_EN
                                            and not plural)
            be = "am" if subject == "min" else "are" if plural or subject == "sin" \
                else "is"
            if item["pos"] == "property" and verb not in ROOT_EN.values():
                words.append(f"{be} {verb}" if not negated else f"{be} not {verb}")
                continue
            do = "does" if third_sg else "do"
            if negated:
                words.append(f"{do} not {verb}" if aspect is None else f"not {verb}")
            elif aspect == "ka":
                words.append(f"{be} {_ing(verb)}")
            elif aspect == "ta":
                words.append(_past(verb))
            elif aspect == "ma":
                words.append(("has " if third_sg else "have ") + _past(verb))
            elif aspect == "fa":
                words.append(f"{be} about to {verb}")
            elif aspect == "sa":
                words.append("usually " + (_third(verb) if third_sg else verb))
            elif aspect == "ba":
                words.append(f"{be_start(subject)} to {verb}".replace(
                    "BEGIN", "begin"))
            elif imperative:
                words.append(verb)
            elif verb.split()[0] == "be":
                words.append(be + verb[2:])
            else:
                words.append(_third(verb) if third_sg else verb)
            continue
        if subject is None and k == "derived":
            subject = item["text"]
        words.append(item["text"])

    sentence = " ".join(w for w in words if w).strip()
    if imperative:
        sentence = "please " + sentence
    sentence = sentence[:1].upper() + sentence[1:] if sentence else ""
    sentence += "?" if question else "."
    if tag:
        sentence += f" ({tag})"
    if evidential:
        sentence += f"  {evidential}"
    return sentence, notes


def be_start(subject):
    return "begins" if subject == "tin" else "begin"


# ------------------------------------------------------------------ web export --

def export_data(target: Path):
    entries = [{"f": e["form"], "c": e["class"], "g": e["gloss"],
                "d": e["source"]} for e in senel.load_lexicon()]
    payload = {
        "lexicon": entries,
        "english": build_english_index(),
        "tables": {
            "pronouns": PRONOUNS, "we": WE, "determiners": DETERMINERS,
            "prepositions": PREPOSITIONS, "connectives": CONNECTIVES,
            "degree": DEGREE, "aspectWords": ASPECT_WORDS,
            "modals": {k: v for k, v in MODALS.items() if v},
            "irregular": IRREGULAR_VERBS, "wh": WH,
            "copula": sorted(COPULA), "have": sorted(HAVE),
            "doSupport": sorted(DO_SUPPORT), "negators": sorted(NEGATORS),
            "drop": sorted(DROP), "pastCues": sorted(PAST_CUES),
            "hearsayCues": sorted(HEARSAY_CUES), "inferCues": sorted(INFER_CUES),
            "opinionVerbs": sorted(OPINION_VERBS),
            "evidEn": EVID_EN, "roleEn": ROLE_EN, "pronEn": PRON_EN,
            "rootEn": ROOT_EN, "irregularPast": IRREGULAR_PAST,
            "irregularPlural": IRREGULAR_PLURAL,
            "verbal": sorted("".join(k) or "0" for k in VERBAL),
            "property": sorted("".join(k) or "0" for k in PROPERTY),
            "supplement": SUPPLEMENT,
            "irregularComparative": IRREGULAR_COMPARATIVE,
        },
    }
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("window.SENEL_DATA = " + json.dumps(payload, ensure_ascii=False)
                      + ";\n", encoding="utf-8")
    print(f"wrote {target} ({target.stat().st_size // 1024} KB, "
          f"{len(entries)} entries, {len(payload['english'])} English keys)")


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 0
    cmd = argv[1]
    if cmd == "data":
        export_data(HERE / "docs" / "data.js")
        return 0
    text = " ".join(argv[2:])
    fn = {"en2sn": en2sn, "sn2en": sn2en}.get(cmd)
    if not fn:
        print(f"unknown command {cmd!r}")
        return 1
    result, notes = fn(text)
    print(result)
    for n in dict.fromkeys(notes):
        print(f"  note: {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
