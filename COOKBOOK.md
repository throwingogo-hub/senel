# Senel cookbook

How to build words and say complex things in Senel — the productive patterns, so
vocabulary grows by rule instead of by invention. This is the practical companion to
[`SPEC.md`](SPEC.md).

Senel has **559 roots**. Everything else is composed. When you need a word that isn't a
root, work down this list and stop at the first that fits — **coin a new root only when
nothing above works.**

## 1. Reuse an existing root

Most "missing" words are already there under a synonym. Senel has one root per concept,
not per English word, so map the concept:

| English | Senel | root's own meaning |
|---|---|---|
| accept | `dit` | receive |
| peace | `fep` | calm |
| danger, damage | `rul` | harm |
| goal, purpose, intend | `mor` | intention |
| knowledge, aware, realise | `mal` | know |
| decision, determine | `mes` | decide |

A minimal language merges fine distinctions on purpose. `owl`, `eagle` → `tel` (bird);
`whale`, `mouse` → `tek` (mammal). Say the class; add a modifier only if it matters.

## 2. Derive with a bound affix

Eleven suffixes, three prefixes, all regular (see SPEC §4). The common moves:

| Want | Pattern | Example |
|---|---|---|
| the noun of a verb | verb + `-ko` (product) or `-mu` (quality) | `misko` science (study-product) |
| one who does it | verb + `-ra` | `sirra` author (write-er), `misra` scholar |
| a tool for it | verb + `-te` | `rulte` weapon (harm-tool) |
| a place for it | verb + `-wa` | `henwa` refectory (eat-place) |
| an adjective | noun + `-pi` | `yerpi` annual (year-ly), `hospi` medical |
| the opposite | `na-` + root | `nanim` ugly (not-beautiful), `nayor` rare (not-often) |
| bigger / smaller | measure + `-go` / `-di` | `urgo` big, `wotdi` narrow, `filgo` terrible |
| again / back | `re-` + root | `regan` redo, `rehen` eat again |

## 3. Compound two roots (head first)

`head + modifier`, always in that order — the same as the rest of the grammar. Pick a
category root for the head and a distinguishing root for the modifier:

| Pattern | Reads as | Examples |
|---|---|---|
| container: `X + pel/wun` | "X-container" | `helpel` cup (drink-container), `papwun` bottle |
| colour: `nin + Y` | "colour-of-Y" | `ninkel` red (colour-blood), `ninlis` blue (sky) |
| meal: `time + hem` | "time-meal" | `yenhem` lunch (day-meal), `yelhem` dinner |
| kin/sex: `base + rom/rem` | "base-male/female" | `relrom` son, `resrem` wife, `kemrom` penis |
| place: `X + wal/wan` | "X-area/place" | `tanwal` garden (plant-area), `heppil` kitchen |
| machine: `X + per` | "X-machine" | `lanper` lamp (light-machine), `banper` vehicle |

**Systematic sets** fall out of one rule:

- **indefinites** = base + determiner (determiners follow their noun): `ran kam`
  someone, `um lam` everything, `wan yam` nowhere (`ran` person / `um` thing / `wan`
  place × `kam` some / `lam` all / `wam` any / `yam` none).
- **times of day** = `yen` (day) + sequence: `yenyis` morning, `yenwip` noon,
  `yenyik` evening.

## 4. Coin a root (last resort)

Only when the concept is a genuine primitive with no honest composition — e.g. `tim`
pig, `kem` genitals. Take a free `-em -im -om -um` slot in the right subdomain via
`build_lexicon.py`'s `EXTRA` table; never hand-edit `lexicon.tsv`. See CONTRIBUTING.

---

## How do I say…?

The grammar already covers complex sentences. Worked patterns:

| English | Senel | note |
|---|---|---|
| The man **who** saw you left. | `Ran rom gu nal ta sin bus lo.` | `gu` = relative clause, follows its noun |
| I know **that** you left. | `Min mal ta fu sin bus lo.` | `fu` = statement complement |
| **If** it rains, I stay. | `Hu lol, min bas lo.` | `hu … (du …)` conditional |
| The dog is **bigger than** the cat. | `Til es mi urgo an tir lo.` | `mi …  an` = more … than |
| The cat is **as big as** the dog. | `Tir es si urgo si til lo.` | `si … si` = as … as |
| the **biggest** house | `pin ti urgo` | `ti` = most |
| **Who** saw the dog? | `Ran nam nal ta til he?` | `nam` (which) + root, in place |
| You **must** / **should** go. | `Sin gum / gumdi bal lo.` | `gumdi` = weaker obligation |
| Let's eat. | `Pe mun hen.` | `pe` hortative, `mun` we-incl. |

Time is stated once with a time word, not marked on every verb (SPEC §6.3). Evidence is
obligatory on every statement: `lo` seen, `to` told, `mo` inferred, `yo` known, `so`
internal (SPEC §6.4).

## What Senel deliberately can't do compactly

There is no register or honorific system — politeness is said outright (`fol` respect,
`sal` please-ask). No etymological depth, no built-up idiom. These are deliberate cuts
(SPEC §9); a translator should render them plainly rather than invent tone.
