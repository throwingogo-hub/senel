# Senel — a constructed language

**`sen`** (language) + **`el`** (true) — a name built from its own roots, like everything
else here. No word in Senel is taken from any existing language. The vocabulary is
generated from a semantic map (`build_lexicon.py`), and every structural claim in this
document that can be checked mechanically is checked by `senel.py validate`.

---

## 0. What "efficient" means here, and what it cannot mean

No language can be more efficient than every other language in every sense. Measured
speech carries roughly the same information rate in every language studied — languages
with simple syllables talk faster, languages with dense syllables talk slower, and the
bits per second come out close to equal. So "the most efficient language" is not a
target anyone can hit.

What *can* be optimised, and what Senel optimises:

| Dimension | Optimised how | Measured result |
|---|---|---|
| **Learning load** | Vocabulary derived from meaning, not memorised | 16 domains replace ~550 arbitrary words |
| **Irregularity** | No root ever changes shape | **0** irregular forms |
| **Grammar size** | Whole grammar is a closed list | **65** one-syllable words |
| **Spelling** | One letter, one sound, both directions | **20** letters, 0 exceptions |
| **Parse cost** | Word class is readable from word shape | grammar identified with no dictionary |
| **Length** | No articles, agreement, gender or tense marking | **‑43%** syllables vs English on test text |
| **Ambiguity** | Contested distinctions are grammaticalised | see §7 |

What Senel gives up is stated in §9. It is a real cost, not a rhetorical one.

---

## 1. Sounds

### 1.1 Inventory

**Consonants (15)** — `p b t d k g` `m n` `s f h` `l r` `w y`

| Letter | IPA | Letter | IPA | Letter | IPA |
|---|---|---|---|---|---|
| p | /p/ | m | /m/ | l | /l/ |
| b | /b/ | n | /n/ | r | /r/ any rhotic |
| t | /t/ | s | /s/ | w | /w/ |
| d | /d/ | f | /f/ | y | /j/ |
| k | /k/ | h | /h/ | | |
| g | /g/ | | | | |

**Vowels (5)** — `a e i o u` = /a e i o u/. The five-vowel system is the most common
vowel system in the world's languages, and it is the largest system that almost every
speaker can hear reliably.

**Not used, deliberately:** tone, vowel length, stress-based meaning, consonant
clusters, geminates, nasalised vowels, the /θ ð ʃ ʒ tʃ dʒ ŋ ʁ/ series, and every
sound that a large fraction of the world cannot produce without training.

### 1.2 Permitted variation

A sound may be pronounced any way inside its range without changing the word. This is
written into the language, not left to chance:

- `r` — trill, tap, approximant or uvular. All correct.
- `p b` / `t d` / `k g` — may be distinguished **either** by voicing **or** by
  aspiration. A speaker whose language uses aspiration says `p` as [pʰ] and `b` as [p].
- `h` — [h], [x] or [ħ]. It must be *audible*; it may never be silent.
- `a` [a~ɑ], `e` [e~ɛ], `i` [i~ɪ], `o` [o~ɔ], `u` [u~ʊ].
- A final consonant may be released with a very short echo vowel — `pin` as [pinɯ] —
  by speakers whose language has no closed syllables. This is safe: the lexicon is
  checked so that no root equals another root plus a final vowel (`validate` reports
  `echo-vowel safety: 0 unsafe`).

### 1.3 Syllables and stress

Every syllable is **(C)V(C)**. Onset: any consonant, or none. Coda: only
`n m l r s k t p`, or none. No clusters anywhere.

**Stress falls on content words; grammar words are never stressed.** In a word of more
than one syllable, stress is on the second-to-last. This is not decoration: it means
the rhythm of a sentence tells the listener where the meaning is before they have
parsed anything.

Unstressed does **not** mean reduced. Every vowel keeps its full quality in every
position. Speakers of languages that reduce unstressed vowels to a schwa (English,
Russian, Portuguese) must suppress that habit — the vowel of a grammar word carries its
grammatical category, so reducing it destroys the sentence.

### 1.4 Writing

Twenty letters: `a b d e f g h i k l m n o p r s t u w y`. No `c j q v x z`. One letter
is one sound in every word, and one sound is one letter — reading aloud and writing
from dictation are both mechanical. Capitals mark proper names only. Digits 0–9 are
written as digits.

---

## 2. Word shape tells you word class

Before knowing a single word, a listener can classify it:

| Shape | Class |
|---|---|
| open one-syllable word (`ta`, `nu`, `lo`) | grammar word — the vowel says which kind |
| `C‑am` (`sam`, `lam`, `nam`) | determiner |
| closed one-syllable word (`kas`, `bal`, `til`) | **content root** |
| two or more syllables | derived or compound — never a primitive root |
| 16 listed exceptions | pronouns and oblique role markers |

Every primitive root in Senel is exactly one closed syllable. Everything longer is
transparently built from parts. This makes tokenising and parsing deterministic, and it
is why an unknown word can still be placed by a listener.

---

## 3. The vocabulary is derived, not memorised

This is the core of the language.

```
    t      i      l     →  til   "dog"
    │      │      │
    │      │      └──── item within the subdomain
    │      └─────────── subdomain: familiar animals
    └────────────────── domain: living kinds
```

### 3.1 The 16 domains (first consonant)

| | Domain | | Domain |
|---|---|---|---|
| *(none)* | number, quantity, logic | `f` | feeling and value |
| `p` | matter and made things | `h` | life and the body's activity |
| `t` | living kinds | `l` | light, heat and weather |
| `k` | parts and structure | `r` | people and society |
| `b` | motion and path | `w` | place and space |
| `d` | transfer and holding | `y` | time |
| `g` | force and change | | |
| `m` | mind | | |
| `n` | perception | | |
| `s` | speech and signs | | |

### 3.2 The five subdomains (vowel)

Each domain divides five ways. For `k` (parts and structure):

| | Subdomain | Members |
|---|---|---|
| `ka‑` | outer body | `kan` body, `kal` head, `kar` face, `kas` eye, `kak` ear, `kat` nose, `kap` mouth |
| `ke‑` | inner body | `ken` heart, `kel` blood, `ker` bone, `kes` brain, `kek` lung, `ket` stomach, `kep` skin |
| `ki‑` | limbs | `kin` arm, `kil` hand, `kir` finger, `kis` leg, `kik` foot, `kit` back, `kip` shoulder |
| `ko‑` | generic parts | `kon` part, `kol` piece, `kor` edge, `kos` centre, `kok` layer, `kot` joint, `kop` tip |
| `ku‑` | form | `kun` structure, `kul` frame, `kur` line, `kus` point, `kuk` shape, `kut` angle |

The full 553-root map is in `lexicon.tsv`, one line per root, with its derivation.

### 3.3 Why the item goes in the weakest position

Word-initial consonants are the most reliably heard; final consonants are the least.
Senel therefore puts the **most important** information (the domain) where hearing is
strongest, and the **most recoverable** information (which member of a small semantic
set) where hearing is weakest. A final-consonant error yields a near-miss inside the
same subdomain — `kas` eye heard as `kak` ear — which context usually repairs. Compare
English, where *cat / cap / cab* are three unrelated concepts.

### 3.4 Growth

New concepts are added by (a) taking a free slot in the right subdomain — `-em -im -om
-um` are free in every domain, since only `C-am` is reserved — or (b) compounding, or
(c) derivation. New *arbitrary* roots are never coined.

---

## 4. Derivation and compounding

Eleven suffixes and three prefixes, all bound, all productive, no exceptions. They are
open `CV` syllables, so they can never be confused with a root (which is always closed).

| | Meaning | From `hen` "eat" |
|---|---|---|
| `-ra` | one who does it | `henra` eater |
| `-te` | tool for it | `hente` fork |
| `-wa` | place of it | `henwa` refectory |
| `-ko` | product of it | `henko` food |
| `-pi` | pertaining to it | `henpi` dietary |
| `-mu` | the quality of it | `henmu` nourishment |
| `-di` | small | `hendi` snack |
| `-go` | large | `hengo` feast |
| `-la` | cause it (causative) | `henla` feed |
| `-yi` | undergo it (passive) | `henyi` be eaten |
| `-no` | ordinal | `atno` third |
| `na-` | opposite / not | `nahen` fast, abstain |
| `re-` | again, back | `rehen` eat again |
| `se-` | self- | `sehen` feed oneself |

**Compounds are head-first, modifier-second**, matching the rest of the language:
`pal‑pel` water-container = bottle; `sem‑wa` book-place = library; `lin‑lan` sun-light.

---

## 5. Numbers, dates and measures

**Digits.** `al` 1, `ak` 2, `at` 3, `ap` 4, `os` 5, `ol` 6, `ok` 7, `ot` 8, `op` 9,
`om` 0. The `a`→`o` vowel change means **+5**: `ak` 2 → `ok` 7, `at` 3 → `ot` 8. Digits
deliberately break the semantic scheme, because a misheard number is expensive; they
are the most acoustically separated words in the language.

**Powers.** `il` 10, `ik` 100, `it` 1000, `ip` 10⁶. Higher powers are explicit:
`il` + ordinal — `il opno` = 10⁹. There is no long-scale/short-scale ambiguity, ever.

**Building numbers.** Multiplier before the power, units after: `ak il at` = 23,
`at ik ap il os` = 345. Fully regular, no teens, no irregular tens.

**Ordinals** `-no`. **Fractions**: N + `uk` (part) — `at uk` = ⅓; `ak en at uk` = ⅔.

**Dates are always year-month-day**, largest to smallest, digits only. There is no
format in which 03‑04 is ambiguous.

**Times are always 24-hour.** **Measures are decimal and SI-only**; the language has no
customary units to convert.

---

## 6. Grammar — the whole of it

Sixty-five one-syllable words. There is nothing else. No conjugation, no declension, no
agreement, no gender, no articles, no irregular anything.

### 6.1 The vowel of a grammar word gives its category

| Vowel | Category | Members |
|---|---|---|
| bare | **role** | `a` agent · `e` patient · `o` to · `i` at · `u` by |
| `‑a` | **aspect** | `ta` completed · `ka` ongoing · `ma` resulting state · `fa` about to · `sa` habitual · `ba` beginning |
| `‑e` | **polarity & mood** | `ne` not · `he` question · `we` command · `pe` let-us · `ge` hypothetical · `de` emphatic · `ye` tag |
| `‑i` | **degree** | `mi` more · `li` less · `ti` most · `si` equally · `ki` too · `fi` enough · `bi` very |
| `‑o` | **evidence** | `lo` seen · `to` told · `so` internal · `mo` inferred · `yo` established |
| `‑u` | **connective** | `nu` and · `bu` or(±both) · `pu` or(exactly one) · `wu` but · `hu` if · `du` then · `ku` because · `ru` although · `fu` that · `gu` which |
| `C‑am` | **determiner** | `sam` this · `tam` that · `nam` which · `kam` some · `lam` all · `pam` many · `fam` few · `yam` none · `wam` any |

Sixteen further forms must simply be learned: the oblique roles `an` from, `en` of,
`in` for, `on` with, `un` because-of, `as` as-for; and the pronouns.

### 6.2 Word order and roles

Canonical order is **Subject – Verb – Object**, and in that order the role markers `a`
and `e` are omitted. Any other order is legal provided the roles are marked. You pay
for word-order freedom only when you use it.

```
Til   nal  sin  lo.            The dog sees you.
dog   see  you  [I saw it]

E sin,  til  nal  lo.          It's you the dog sees.
PAT you dog  see  [I saw it]
```

Obliques are prepositions and may go anywhere: `i pin` in the building, `an pol` from
the city, `u pet` with a blade, `in sin` for you, `un lol` because of rain.

### 6.3 Aspect, not tense

Senel does not mark tense. Time is stated once, with a time word, and not repeated on
every verb — English marks it on every verb whether or not it adds anything.

```
Min bal ta.     I went / have gone.        (completed)
Min bal ka.     I am going.                (ongoing)
Min bal ma.     I am gone.                 (resulting state)
Min bal fa.     I am about to go.          (imminent)
Min bal sa.     I go (regularly).          (habitual)
Yer yar, min bal ta lo.    Last year I went.
```

### 6.4 Evidence is obligatory

Every plain statement ends with one syllable saying how the speaker knows it.

```
Lol ka lo.    It is raining — I can see it.
Lol ka to.    It is raining — I was told.
Lol ka mo.    It is raining — I infer it.
Lol ka yo.    It rains here — established fact.
Fen so.       I am happy — internal state, only I have access.
```

This costs one syllable per sentence. It saves more than it costs: English needs
*"apparently"*, *"I heard that"*, *"it seems"*, *"I saw"* — three to five syllables —
and usually omits them, leaving the hearer to guess. In Senel the omission is
ungrammatical.

Questions, commands and hypotheticals take a mood particle instead: `he` `we` `pe` `ge`.

### 6.5 Negation, questions, comparison

- **Negation** — `ne` before the verb. `na-` on a root gives its opposite. There is no
  double negation and no negative concord: `yam` (none) is already negative.
- **Polar question** — `he` at the end: `Sin nal ta til he?`
- **Content question** — `nam` (which) plus the right root, in place, no movement, no
  new words: `nam ran` who · `nam wan` where · `nam yan` when · `nam ul` how many ·
  `un nam` why · `u nam` how. Eight English interrogatives replaced by one rule.
- **Comparison** — degree particle plus `an` (from) for the standard:
  `Til es mi ur an tir lo.` the dog is more size-from the cat = the dog is bigger.
- **Answers** — `el` true / `er` false, or repeat the verb.

### 6.6 Subordination

`fu` introduces a statement complement, `gu` a relative clause, `hu … du …` a
conditional. Clauses are head-initial, so relative clauses follow their noun and never
nest inward:

```
Min mal fu  sin  bal ta   lo.       I know that you left.
Ran gu  sir   ta  sem tam  es min ren    en min yo.
person who write PFV book that is  parent of me [established]
```

### 6.7 Reference

Pronouns: `min` I · `sin` you · `tin` he/she/it · `sun` you-plural · `tun` they ·
`pan` one/people · `sel` self · `tal` each other.

- **`mun` = we including you. `mon` = we excluding you.** The distinction is
  obligatory, so "we" is never a trap.
- **Indexed third persons.** When two third parties are in play, number them:
  `tinal` (that one, #1), `tinak` (#2). Reference is then explicit rather than guessed.
- **No gender anywhere in the grammar.** `rem` female and `rom` male exist as ordinary
  roots, used only when the fact matters.
- **Number is optional.** `til` is dog-or-dogs; `til pam` many dogs; `til ak` two dogs.
  Plurality is marked when it is news, not every time.

### 6.8 No adjective class

Property words are verbs. `Til fin lo` = the dog is good (no copula). The same root
placed after a noun modifies it: `til fin` = a good dog. One construction, two jobs.

`es` is the identity copula (*be the same as*); `em` is existence (*there is*).

---

## 7. Ambiguities Senel removes by design

Each of these is a documented, real source of failure in natural language:

1. **Source of knowledge** — obligatory evidential.
2. **"We"** — inclusive `mun` vs exclusive `mon`.
3. **"Or"** — `bu` (one or both) vs `pu` (exactly one).
4. **Dates** — always year-month-day, digits only.
5. **"Billion"** — powers of ten are explicit.
6. **"Next Friday"** — relative time requires a stated reference point or a date.
7. **Quantifier scope** — surface order *is* scope order; to change the reading,
   reorder, which is free because roles are marked.
8. **Pronoun reference** — indexed third persons.
9. **Relative-clause attachment** — clauses are head-initial and follow their head, so
   "the servant of the actress who…" cannot arise.
10. **Word class** — recoverable from the shape of the word.

---

## 8. Measured efficiency

Universal Declaration of Human Rights, Article 1:

```
Lam ran har fum nu es i fom nu rum yo.
all person be-born free and be-same at dignity and right [established]

Tun dar men nu mom, du gum gan o tal on rusmu yo.
they have reason and conscience, so must act to each-other with cooperation-ness
```

| | Syllables |
|---|---|
| English original | 44 |
| **Senel** | **25** |

A 43% reduction, with the evidential included and nothing left implicit that English
states. Senel wins on dense expository text. On very short conversational clauses it is
roughly level with English, because the obligatory evidential costs a syllable that a
short sentence cannot amortise. Both facts are reported here because both are true.

Learning load, which is the larger win:

| | Senel | English |
|---|---|---|
| Irregular verb forms | 0 | ~200 |
| Irregular plurals | 0 | ~100 |
| Grammatical genders | 0 | 0 |
| Grammar words to learn | 65 | ~150 |
| Spelling–sound rules | 20 | several hundred |
| Arbitrary root meanings | 0 | all of them |

---

## 9. What Senel is worse at

Stated plainly, because a design document that only lists wins is advertising.

1. **Noise.** A systematic lexicon puts related meanings in adjacent sound-space.
   `validate` counts 6,202 one-phoneme-apart root pairs. 42% of those errors land
   inside the same domain (a recoverable near-miss), but 58% change the initial
   consonant and therefore the topic. English is more redundant and survives a bad
   phone line better. This is the direct cost of the compression, and it cannot be
   removed without lengthening words.
2. **Speech rate.** Denser syllables are pronounced more slowly. The 43% syllable
   saving will not translate into 43% less time.
3. **Poetry, idiom, register.** Senel has no honorific system, no register variation,
   no etymological depth and no accumulated idiom. Politeness must be said outright
   with words like `fol` (respect). This is a deliberate cut, and it makes the language
   flatter than any natural one.
4. **Vocabulary depth.** 553 roots plus derivation covers ordinary life. Medicine, law
   and engineering would each need their subdomains filled out.
5. **Adoption.** Design quality has never been what determines whether a constructed
   language is used. Nothing here changes that.

---

## 10. Tooling

```bash
python3 build_lexicon.py          # regenerate every root from the semantic map
python3 senel.py validate         # phonotactics, collisions, confusability, echo-vowel
python3 senel.py gloss "<text>"   # interlinear gloss, decomposes derivations
python3 senel.py count "<text>"   # syllable count
python3 senel.py merge            # which words collapse for a given L1's ear
```

`validate` currently reports: 553 roots, 100% one syllable, 65 grammar words,
**0 irregular forms**, 0 phonotactic violations, 0 shape-rule violations, 0 duplicate
forms, 0 echo-vowel hazards.
