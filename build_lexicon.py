#!/usr/bin/env python3
"""build_lexicon.py -- generates Senel's entire vocabulary from a semantic map.

No root is borrowed from any existing language. Every root is derived:

    onset consonant  ->  semantic domain      (16 domains)
    vowel            ->  subdomain            (5 per domain)
    coda consonant   ->  item in the subdomain (up to 8)

So `bal` is not an arbitrary noise meaning "go": b = motion, a = basic motion,
l = the second item of that set. A listener who has never met the word still
knows it is about motion. This is the opposite of natural-language vocabulary,
where /dog/ tells you nothing about dogs.

Run:  python3 build_lexicon.py   ->  writes lexicon.tsv
"""

from pathlib import Path

# Forms the grammar has already claimed; the generator must route around them.
RESERVED = {
    # roles
    "an", "en", "in", "on", "un", "as",
    # pronouns
    "min", "mun", "mon", "sin", "sun", "tin", "tun", "pan", "sel", "tal",
}
# Every determiner is C-am, so no root may end in -am.
BLOCKED_SUFFIX = "am"

DOMAINS = {
    "": ("number, quantity and logic", {
        "a": ("digits 1-4", {"l": "1", "k": "2", "t": "3", "p": "4"}),
        "o": ("digits 5-9 and 0", {"s": "5", "l": "6", "k": "7", "t": "8",
                                   "p": "9", "m": "0"}),
        "i": ("powers of ten", {"l": "ten", "k": "hundred", "t": "thousand",
                                "p": "million"}),
        "e": ("logic", {"l": "true", "r": "false", "s": "be, be the same as",
                        "k": "other, different", "t": "cause", "p": "result",
                        "m": "exist, there is"}),
        "u": ("measure", {"l": "amount", "r": "size", "s": "unit", "k": "part",
                          "t": "whole", "p": "degree", "m": "thing, entity"}),
    }),
    "p": ("matter and made things", {
        "a": ("natural substance", {"l": "water", "r": "air", "s": "soil",
                                    "k": "stone", "t": "sand", "p": "liquid"}),
        "e": ("tools", {"n": "tool", "l": "container", "r": "machine",
                        "s": "cloth", "k": "rope", "t": "blade", "p": "wheel"}),
        "i": ("buildings", {"n": "building", "l": "room", "r": "door",
                            "s": "window", "k": "wall", "t": "roof",
                            "p": "floor"}),
        "o": ("worked material", {"n": "metal", "l": "wood", "r": "glass",
                                  "s": "paper", "k": "made material",
                                  "t": "clay", "p": "fibre"}),
        "u": ("states of matter", {"n": "solid", "l": "fluid", "r": "gas",
                                   "s": "dust", "k": "lump", "t": "surface",
                                   "p": "hole"}),
    }),
    "t": ("living kinds", {
        "a": ("plants", {"n": "plant", "r": "tree", "s": "grass", "k": "leaf",
                         "t": "root", "p": "flower"}),
        "e": ("animal classes", {"n": "animal", "l": "bird", "r": "fish",
                                 "s": "insect", "k": "mammal", "t": "reptile",
                                 "p": "worm"}),
        "i": ("familiar animals", {"l": "dog", "r": "cat", "s": "horse",
                                   "k": "fowl", "t": "cattle", "p": "sheep"}),
        "o": ("other life", {"n": "fungus", "l": "seed", "r": "egg",
                             "s": "microbe", "k": "cell", "t": "species",
                             "p": "breed"}),
        "u": ("plant produce", {"l": "fruit", "r": "grain", "s": "vegetable",
                                "k": "timber", "t": "bark", "p": "sap"}),
    }),
    "k": ("parts and structure", {
        "a": ("outer body", {"n": "body", "l": "head", "r": "face", "s": "eye",
                             "k": "ear", "t": "nose", "p": "mouth"}),
        "e": ("inner body", {"n": "heart", "l": "blood", "r": "bone",
                             "s": "brain", "k": "lung", "t": "stomach",
                             "p": "skin"}),
        "i": ("limbs", {"n": "arm", "l": "hand", "r": "finger", "s": "leg",
                        "k": "foot", "t": "back", "p": "shoulder"}),
        "o": ("generic parts", {"n": "part", "l": "piece", "r": "edge",
                                "s": "centre", "k": "layer", "t": "joint",
                                "p": "tip, end"}),
        "u": ("form", {"n": "structure", "l": "frame", "r": "line",
                       "s": "point", "k": "shape", "t": "angle",
                       "p": "surface of"}),
    }),
    "b": ("motion and path", {
        "a": ("basic motion", {"n": "move", "l": "go", "r": "come", "s": "stop",
                               "k": "return", "t": "follow", "p": "lead"}),
        "e": ("manner of motion", {"n": "walk", "l": "run", "r": "fly",
                                   "s": "swim", "k": "climb", "t": "fall",
                                   "p": "jump"}),
        "i": ("caused motion", {"n": "carry", "l": "push", "r": "pull",
                                "s": "throw", "k": "lift", "t": "drop",
                                "p": "drag"}),
        "o": ("direction", {"n": "path", "l": "forward", "r": "backward",
                            "s": "up", "k": "down", "t": "across",
                            "p": "around"}),
        "u": ("arrival and departure", {"n": "enter", "l": "exit", "r": "arrive",
                                        "s": "leave", "k": "pass", "t": "meet",
                                        "p": "cross"}),
    }),
    "d": ("transfer and holding", {
        "a": ("basic transfer", {"n": "give", "l": "take", "r": "have",
                                 "s": "lack", "k": "keep", "t": "lose",
                                 "p": "find"}),
        "e": ("exchange", {"n": "trade", "l": "buy", "r": "sell", "s": "pay",
                           "k": "price", "t": "money", "p": "debt"}),
        "i": ("sharing", {"n": "share", "l": "lend", "r": "borrow", "s": "steal",
                          "k": "gift", "t": "receive", "p": "send"}),
        "o": ("possession", {"n": "owner", "l": "property", "r": "portion",
                             "s": "wealth", "k": "poverty", "t": "value",
                             "p": "cost"}),
        "u": ("flow of goods", {"n": "transfer", "l": "exchange", "r": "supply",
                                "s": "demand", "k": "store", "t": "waste",
                                "p": "save"}),
    }),
    "g": ("force and change", {
        "a": ("causing", {"n": "make, do", "l": "cause", "r": "become",
                          "s": "change", "k": "begin", "t": "end",
                          "p": "continue"}),
        "e": ("build and break", {"n": "build", "l": "break", "r": "repair",
                                  "s": "destroy", "k": "cut", "t": "join",
                                  "p": "open"}),
        "i": ("handling", {"n": "hold", "l": "press", "r": "turn", "s": "bend",
                           "k": "strike", "t": "rub", "p": "tie"}),
        "o": ("physical force", {"n": "force", "l": "power", "r": "weight",
                                 "s": "speed", "k": "pressure",
                                 "t": "resistance", "p": "balance"}),
        "u": ("process", {"n": "work on", "l": "use", "r": "attempt",
                          "s": "succeed", "k": "fail", "t": "prepare",
                          "p": "complete"}),
    }),
    "m": ("mind", {
        "a": ("thinking", {"n": "think", "l": "know", "r": "believe",
                           "s": "doubt", "k": "remember", "t": "forget",
                           "p": "understand"}),
        "e": ("reasoning", {"n": "reason", "l": "judge", "r": "compare",
                            "s": "decide", "k": "plan", "t": "guess",
                            "p": "prove"}),
        "i": ("learning", {"l": "learn", "r": "teach", "s": "study",
                           "k": "skill", "t": "idea", "p": "problem"}),
        "o": ("mental states", {"l": "attention", "r": "intention",
                                "s": "memory", "k": "imagination",
                                "t": "opinion", "p": "mind"}),
        "u": ("truth status", {"l": "fact", "r": "hypothesis", "s": "error",
                               "k": "proof", "t": "meaning", "p": "sense"}),
    }),
    "n": ("perception", {
        "a": ("perceiving", {"n": "perceive", "l": "see", "r": "hear",
                             "s": "smell", "k": "taste", "t": "touch",
                             "p": "feel by body"}),
        "e": ("the senses", {"n": "sight", "l": "sound", "r": "odour",
                             "s": "flavour", "k": "texture", "t": "sensation",
                             "p": "sense faculty"}),
        "i": ("visual quality", {"n": "colour", "l": "bright", "r": "dark",
                                 "s": "clear", "k": "pattern", "t": "visible",
                                 "p": "hidden"}),
        "o": ("auditory quality", {"n": "noise", "l": "loud", "r": "quiet",
                                   "s": "voice", "k": "tone", "t": "silence",
                                   "p": "echo"}),
        "u": ("bodily sensation", {"n": "pain", "l": "pleasure", "r": "hunger",
                                   "s": "thirst", "k": "tiredness",
                                   "t": "feeling warm", "p": "feeling cold"}),
    }),
    "s": ("speech and signs", {
        "a": ("speech acts", {"n": "say", "l": "ask", "r": "answer", "s": "tell",
                              "k": "call, name", "t": "promise", "p": "deny"}),
        "e": ("language units", {"n": "language", "r": "word", "s": "sentence",
                                 "k": "speech sound", "t": "letter",
                                 "p": "text"}),
        "i": ("communicating", {"l": "talk with", "r": "write", "s": "read",
                                "k": "sign", "t": "show", "p": "conceal"}),
        "o": ("discourse", {"n": "story", "l": "news", "r": "question",
                            "s": "claim", "k": "argument", "t": "agreement",
                            "p": "command"}),
        "u": ("naming", {"l": "name", "r": "title", "s": "label", "k": "symbol",
                         "t": "numeral", "p": "mark"}),
    }),
    "f": ("feeling and value", {
        "a": ("wanting", {"n": "feel emotion", "l": "want", "r": "need",
                          "s": "like", "k": "dislike", "t": "love",
                          "p": "hate"}),
        "e": ("emotions", {"n": "joy", "l": "sadness", "r": "fear", "s": "anger",
                           "k": "surprise", "t": "disgust", "p": "calm"}),
        "i": ("evaluation", {"n": "good", "l": "bad", "r": "correct",
                             "s": "wrong", "k": "important", "t": "useful",
                             "p": "beautiful"}),
        "o": ("social feeling", {"n": "trust", "l": "respect", "r": "shame",
                                 "s": "pride", "k": "pity", "t": "envy",
                                 "p": "gratitude"}),
        "u": ("will", {"n": "choose", "l": "resolve", "r": "refuse",
                       "s": "allow", "k": "forbid", "t": "dare",
                       "p": "hesitate"}),
    }),
    "h": ("life and the body's activity", {
        "a": ("life course", {"n": "live", "l": "die", "r": "be born",
                              "s": "grow", "k": "age", "t": "heal",
                              "p": "fall ill"}),
        "e": ("ingestion", {"n": "eat", "l": "drink", "r": "bite",
                            "s": "swallow", "k": "chew", "t": "breathe",
                            "p": "cook"}),
        "i": ("rest and effort", {"n": "sleep", "l": "wake", "r": "rest",
                                  "s": "labour", "k": "play", "t": "exercise",
                                  "p": "dream"}),
        "o": ("health", {"n": "health", "l": "illness", "r": "wound",
                         "s": "medicine", "k": "birth", "t": "death",
                         "p": "strength"}),
        "u": ("care of the body", {"n": "wash", "l": "clean", "r": "dirty",
                                   "s": "body waste", "k": "sweat",
                                   "t": "wear, dress", "p": "bathe"}),
    }),
    "l": ("light, heat and weather", {
        "a": ("light", {"n": "light", "l": "darkness", "r": "shine",
                        "s": "shadow", "k": "colour of light", "t": "reflect",
                        "p": "glow"}),
        "e": ("heat", {"n": "heat", "l": "cold", "r": "burn", "s": "freeze",
                       "k": "melt", "t": "boil", "p": "warm"}),
        "i": ("sky", {"n": "sun", "l": "moon", "r": "star", "s": "sky",
                      "k": "cloud", "t": "world", "p": "outer space"}),
        "o": ("weather", {"n": "weather", "l": "rain", "r": "wind", "s": "snow",
                          "k": "storm", "t": "fog", "p": "drought"}),
        "u": ("energy", {"n": "energy", "l": "fire", "r": "electricity",
                         "s": "wave", "k": "magnetism", "t": "gravity",
                         "p": "radiation"}),
    }),
    "r": ("people and society", {
        "a": ("persons", {"n": "person", "l": "people, group", "r": "family",
                          "s": "friend", "k": "enemy", "t": "stranger",
                          "p": "neighbour"}),
        "e": ("kin", {"n": "parent", "l": "child", "r": "sibling", "s": "spouse",
                      "k": "grandparent", "t": "descendant", "p": "relative",
                      "m": "female"}),
        "i": ("roles", {"n": "leader", "l": "worker", "r": "student",
                        "s": "teacher", "k": "healer", "t": "trader",
                        "p": "guard"}),
        "o": ("institutions", {"n": "society", "l": "law", "r": "government",
                               "s": "school", "k": "market", "t": "court",
                               "p": "army", "m": "male"}),
        "u": ("social action", {"n": "help", "l": "harm", "r": "join with",
                                "s": "cooperate", "k": "compete", "t": "obey",
                                "p": "command"}),
    }),
    "w": ("place and space", {
        "a": ("places", {"n": "place", "l": "area", "r": "position",
                         "s": "region", "k": "land", "t": "sea", "p": "island"}),
        "e": ("relative position", {"n": "inside", "l": "outside", "r": "above",
                                    "s": "below", "k": "in front of",
                                    "t": "behind", "p": "beside"}),
        "i": ("direction", {"n": "north", "l": "south", "r": "east", "s": "west",
                            "k": "left", "t": "right", "p": "middle"}),
        "o": ("extent", {"n": "near", "l": "far", "r": "distance", "s": "height",
                         "k": "depth", "t": "width", "p": "length"}),
        "u": ("bounded space", {"n": "container", "l": "box", "r": "bag",
                                "s": "border", "k": "gate", "t": "way, route",
                                "p": "corner"}),
    }),
    "y": ("time", {
        "a": ("time itself", {"n": "time", "l": "now", "r": "past",
                              "s": "future", "k": "moment", "t": "period",
                              "p": "era"}),
        "e": ("units", {"n": "day", "l": "night", "r": "year", "s": "month",
                        "k": "week", "t": "hour", "p": "minute"}),
        "i": ("sequence", {"n": "before", "l": "after", "r": "during",
                           "s": "start of", "k": "end of", "t": "between",
                           "p": "since"}),
        "o": ("frequency", {"n": "always", "l": "never", "r": "often",
                            "s": "sometimes", "k": "again", "t": "still",
                            "p": "already"}),
        "u": ("pace", {"n": "fast", "l": "slow", "r": "long in time",
                       "s": "brief", "k": "sudden", "t": "gradual",
                       "p": "constant"}),
    }),
}

# Later additions, using the free -m coda slot. Only C-am is blocked (determiners),
# so -em -im -om -um remain available in every domain for filling gaps.
EXTRA = {
    ("f", "o", "m"): "dignity, worth",
    ("f", "u", "m"): "free, at liberty",
    ("r", "u", "m"): "right, entitlement",
    ("m", "o", "m"): "conscience",
    ("s", "e", "m"): "book, document",
    ("h", "e", "m"): "meal",
    ("g", "u", "m"): "must, be obliged to",
    ("w", "u", "m"): "boundary of",
}

GRAMMAR = """a	ROLE	AGENT (subject; omitted in canonical order)	bare vowel = role
e	ROLE	PATIENT (object; omitted in canonical order)	bare vowel = role
o	ROLE	to, toward (recipient, goal)	bare vowel = role
i	ROLE	at, in, on (place and time)	bare vowel = role
u	ROLE	by, with (instrument, means)	bare vowel = role
an	ROLE	from (source, origin)	oblique role series
en	ROLE	of (possession, part, relation)	oblique role series
in	ROLE	for (beneficiary)	oblique role series
on	ROLE	with (accompaniment)	oblique role series
un	ROLE	because of, for the sake of	oblique role series
as	ROLE	TOPIC (as for X)	oblique role series
ta	ASP	PERFECTIVE (completed)	-a class = aspect
ka	ASP	PROGRESSIVE (ongoing)	-a class = aspect
ma	ASP	PERFECT (resulting state)	-a class = aspect
fa	ASP	PROSPECTIVE (about to)	-a class = aspect
sa	ASP	HABITUAL (generic, repeated)	-a class = aspect
ba	ASP	INCEPTIVE (begins to)	-a class = aspect
lo	EVID	I perceived it directly	-o class = evidential
to	EVID	I was told it	-o class = evidential
so	EVID	my own state, intent or opinion	-o class = evidential
mo	EVID	I infer it from evidence	-o class = evidential
yo	EVID	established or common knowledge	-o class = evidential
ne	MOOD	not	-e class = polarity and mood
he	MOOD	POLAR QUESTION	-e class = polarity and mood
we	MOOD	IMPERATIVE, request	-e class = polarity and mood
pe	MOOD	HORTATIVE (let us, may it)	-e class = polarity and mood
ge	MOOD	HYPOTHETICAL, counterfactual	-e class = polarity and mood
de	MOOD	EMPHATIC assertion	-e class = polarity and mood
ye	MOOD	TAG (…right?)	-e class = polarity and mood
mi	DEG	more (comparative)	-i class = degree
li	DEG	less	-i class = degree
ti	DEG	most (superlative)	-i class = degree
si	DEG	as, equally (equative)	-i class = degree
ki	DEG	too, excessively	-i class = degree
fi	DEG	enough, sufficiently	-i class = degree
bi	DEG	very	-i class = degree
nu	CONN	and	-u class = connective
bu	CONN	or (inclusive: one or both)	-u class = connective
pu	CONN	or (exclusive: exactly one)	-u class = connective
wu	CONN	but, however	-u class = connective
hu	CONN	if (marks the condition)	-u class = connective
du	CONN	then, therefore (marks the result)	-u class = connective
ku	CONN	because	-u class = connective
ru	CONN	although	-u class = connective
fu	CONN	that (complementiser)	-u class = connective
gu	CONN	which, who (relativiser)	-u class = connective
sam	DET	this, these (near)	C-am = determiner
tam	DET	that, those (far)	C-am = determiner
nam	DET	which, what (interrogative)	C-am = determiner
kam	DET	some	C-am = determiner
lam	DET	all, every, each	C-am = determiner
pam	DET	many (also general plural)	C-am = determiner
fam	DET	few, a little	C-am = determiner
yam	DET	no, none, zero	C-am = determiner
wam	DET	any	C-am = determiner
min	PRON	I, me	pronoun set
mun	PRON	we (including you)	pronoun set
mon	PRON	we (excluding you)	pronoun set
sin	PRON	you (one)	pronoun set
sun	PRON	you (several)	pronoun set
tin	PRON	he, she, they, it (one)	pronoun set
tun	PRON	they (several)	pronoun set
pan	PRON	one, people (generic)	pronoun set
sel	PRON	self (reflexive)	pronoun set
tal	PRON	each other; together	pronoun set
na-	AFFIX	not, the opposite of	bound CV prefix
re-	AFFIX	again, back	bound CV prefix
se-	AFFIX	self-, auto-	bound CV prefix
-ra	AFFIX	one who does it (agent)	bound CV suffix
-te	AFFIX	tool for doing it	bound CV suffix
-wa	AFFIX	place where it happens	bound CV suffix
-ko	AFFIX	product or result of it	bound CV suffix
-pi	AFFIX	pertaining to it (adjectival)	bound CV suffix
-mu	AFFIX	the quality of it (abstract)	bound CV suffix
-di	AFFIX	small, lesser	bound CV suffix
-go	AFFIX	large, greater	bound CV suffix
-la	AFFIX	cause it to happen (causative)	bound CV suffix
-yi	AFFIX	undergo it (passive)	bound CV suffix
-no	AFFIX	ordinal (Nth)	bound CV suffix"""


def build():
    rows = [line.split("\t") for line in GRAMMAR.split("\n")]
    seen = {r[0] for r in rows}
    skipped = []
    for onset, (dom_name, subs) in DOMAINS.items():
        for vowel, (sub_name, items) in subs.items():
            items = dict(items)
            for (o, v, c), gloss in EXTRA.items():
                if (o, v) == (onset, vowel):
                    items[c] = gloss
            for coda, gloss in items.items():
                form = f"{onset}{vowel}{coda}"
                if form in RESERVED or form.endswith(BLOCKED_SUFFIX):
                    skipped.append((form, gloss))
                    continue
                if form in seen:
                    raise SystemExit(f"generator collision on {form!r} ({gloss})")
                seen.add(form)
                cls = "NUM" if onset == "" and vowel in "aoi" else "ROOT"
                deriv = f"{onset or 'zero'}={dom_name} / {vowel}={sub_name}"
                rows.append([form, cls, gloss, deriv])
    out = "form\tclass\tgloss\tderivation\n" + "\n".join("\t".join(r) for r in rows) + "\n"
    Path(__file__).with_name("lexicon.tsv").write_text(out, encoding="utf-8")
    roots = [r for r in rows if r[1] in ("ROOT", "NUM")]
    print(f"wrote lexicon.tsv: {len(rows)} entries, {len(roots)} generated roots")
    if skipped:
        print(f"{len(skipped)} slot(s) skipped as reserved: " +
              ", ".join(f"{f}({g})" for f, g in skipped))


if __name__ == "__main__":
    build()
