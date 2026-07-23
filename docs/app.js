/* Senel translator — browser port of translate.py.
   All lookup tables come from data.js, which translate.py generates, so the two
   implementations cannot drift on vocabulary. Only the rules live here. */
(function (global) {
  "use strict";

  const D = global.SENEL_DATA;
  const T = D.tables;
  const LEX = new Map(D.lexicon.map((e) => [e.f, e]));
  const AFFIX = new Map(
    D.lexicon.filter((e) => e.c === "AFFIX").map((e) => [e.f.replace(/-/g, ""), e])
  );
  const PREFIXES = ["na", "re", "se"];
  const VOWELS = new Set(["a", "e", "i", "o", "u"]);
  const set = (a) => new Set(a);
  const COPULA = set(T.copula), HAVE = set(T.have), DO = set(T.doSupport),
    NEG = set(T.negators), DROP = set(T.drop), PAST_CUES = set(T.pastCues),
    HEARSAY = set(T.hearsayCues), INFER = set(T.inferCues),
    OPINION = set(T.opinionVerbs),
    VERBAL = set(T.verbal), PROPERTY = set(T.property);

  const clean = (g) => g.replace(/\s*\(.*?\)/g, "").split(/[,;]/)[0].trim();

  function posOf(form, cls) {
    if (cls === "NUM") return "num";
    if (cls !== "ROOT") return "gram";
    const key = form.length === 2 ? "0" + form[0] : form[0] + form[1];
    const k = form.length === 2 ? form[0] : form[0] + form[1];
    if (VERBAL.has(key) || VERBAL.has(k)) return "verb";
    if (PROPERTY.has(key) || PROPERTY.has(k)) return "property";
    return "noun";
  }

  /* ---- morphology of a single Senel word: root, derivation or compound ---- */
  function analyse(token) {
    const t = token.toLowerCase().replace(/[.,!?;:]/g, "");
    if (!t) return null;
    if (LEX.has(t)) return { gloss: LEX.get(t).g, kind: LEX.get(t).c, form: t };
    for (const p of PREFIXES) {
      if (t.startsWith(p) && LEX.has(t.slice(p.length)))
        return {
          gloss: clean(AFFIX.get(p).g) + " + " + LEX.get(t.slice(p.length)).g,
          kind: "DERIVED", form: t,
        };
    }
    for (const [suf, entry] of AFFIX) {
      if (PREFIXES.includes(suf)) continue;
      if (t.endsWith(suf) && LEX.has(t.slice(0, -suf.length)))
        return {
          gloss: LEX.get(t.slice(0, -suf.length)).g + " + " + clean(entry.g),
          kind: "DERIVED", form: t,
        };
    }
    for (let i = 2; i < t.length - 1; i++)
      if (LEX.has(t.slice(0, i)) && LEX.has(t.slice(i)))
        return {
          gloss: LEX.get(t.slice(0, i)).g + "-" + LEX.get(t.slice(i)).g,
          kind: "COMPOUND", form: t,
        };
    return { gloss: null, kind: "UNKNOWN", form: t };
  }

  /* --------------------------- English -> Senel --------------------------- */

  function lemma(w) {
    if (T.irregular[w]) return T.irregular[w];
    for (const [suf, repl] of [["ies", "y"], ["ing", ""], ["ed", ""], ["es", ""], ["s", ""]])
      if (w.endsWith(suf) && w.length - suf.length >= 3)
        return w.slice(0, w.length - suf.length) + repl;
    return w;
  }

  function comparative(word) {
    if (T.irregularComparative[word]) return T.irregularComparative[word].slice();
    for (const [suf, particle] of [["est", "ti"], ["er", "mi"]]) {
      if (!word.endsWith(suf) || word.length - suf.length < 3) continue;
      const stem = word.slice(0, word.length - suf.length);
      const tries = [stem, stem + "e"];
      if (stem.length > 3 && stem[stem.length - 1] === stem[stem.length - 2])
        tries.push(stem.slice(0, -1));
      for (const c of tries)
        if (D.english[c]) {
          let form = D.english[c];
          if ((form.endsWith("go") || form.endsWith("di")) && form.length > 4)
            form = form.slice(0, -2);
          return [particle].concat(form.split(" "));
        }
    }
    return null;
  }

  function verbSlot(tokens) {
    for (let i = 0; i < tokens.length; i++) {
      const e = LEX.get(tokens[i]);
      if (e && e.c === "ROOT") return i;
    }
    return tokens.length;
  }

  function en2sn(text) {
    const notes = [], out = [];
    const raw = text.trim();
    const isQuestion = raw.endsWith("?");
    let words = (raw.toLowerCase().replace(/n't/g, " not").match(/[a-z']+/g) || []);
    if (!words.length) return { text: "", notes };

    let aspect = null, negate = false, modal = null, evidential = null,
      leadWh = null, firstPerson = false, opinion = false;
    const joined = words.join(" ");

    for (const c of HEARSAY) if (words.includes(c)) evidential = "to";
    for (const c of INFER) if (words.includes(c)) evidential = "mo";
    if (words.some((w) => PAST_CUES.has(w))) aspect = "ta";
    words.forEach((w, i) => {
      const nxt = words[i + 1];
      if (["is", "am", "are", "was", "were"].includes(w) && nxt && nxt.endsWith("ing"))
        aspect = "ka";
      if (HAVE.has(w) && nxt && !COPULA.has(nxt) && (nxt.endsWith("ed") || T.irregular[nxt]))
        aspect = "ma";
      if (w === "was" || w === "were" || (w.endsWith("ed") && lemma(w) !== w))
        aspect = aspect || "ta";
      if (T.aspectWords[w]) aspect = T.aspectWords[w];
      if (NEG.has(w)) negate = true;
      if (T.modals[w]) modal = T.modals[w];
      if (OPINION.has(lemma(w))) opinion = true;
    });
    if (words[0] === "i" || words[0] === "we") firstPerson = true;

    for (const wh of Object.keys(T.wh).sort((a, b) => b.length - a.length))
      if (joined.startsWith(wh)) {
        leadWh = T.wh[wh];
        words = words.slice(wh.split(" ").length);
        break;
      }

    let i = 0, possessor = null;
    while (i < words.length) {
      const w = words[i];
      if (DROP.has(w) || DO.has(w) || HAVE.has(w) || NEG.has(w) ||
          T.aspectWords[w] || COPULA.has(w)) {
        if (COPULA.has(w) && !words.slice(i + 1).some((x) => x.endsWith("ing")))
          out.push("es");
        i++; continue;
      }
      if (w === "than") { out.push("an"); i++; continue; }
      const cmp = comparative(w);
      if (cmp) { out.push(...cmp); i++; continue; }

      let matched = false;
      for (const span of [3, 2, 1]) {
        const phrase = words.slice(i, i + span).join(" ");
        if (!phrase) continue;
        const tables = [
          ["prep", T.prepositions], ["conn", T.connectives], ["deg", T.degree],
          ["det", T.determiners], ["pron", T.pronouns], ["we", T.we],
          ["modal", T.modals],
        ];
        for (const [name, table] of tables) {
          if (!(phrase in table)) continue;
          const val = table[phrase];
          if (name === "we")
            notes.push("English 'we' is ambiguous; Senel requires a choice. " +
              "Used mon (we, NOT including you) — swap to mun to include them.");
          if (name === "modal") { matched = true; i += span; break; }
          if ((name === "pron" || name === "we") &&
              ["my", "your", "his", "her", "its", "their", "our", "ours"].includes(phrase)) {
            possessor = val; matched = true; i += span; break;
          }
          out.push(val); matched = true; i += span; break;
        }
        if (matched) break;
        const key = phrase in D.english ? phrase :
          (lemma(phrase) in D.english ? lemma(phrase) : null);
        if (key) {
          out.push(...D.english[key].split(" "));
          if (possessor) { out.push("en", possessor); possessor = null; }
          matched = true; i += span; break;
        }
      }
      if (matched) continue;
      notes.push(`no Senel word for '${w}' yet — left as [${w}]`);
      out.push(`[${w}]`);
      i++;
    }
    if (possessor) out.push("en", possessor);

    let tokens = out;
    if (leadWh) {
      if (tokens[0] === "es") tokens.shift();
      tokens = tokens.concat(leadWh === "wan nam" ? ["em", "i", "wan", "nam"]
        : leadWh.split(" "));
    }
    if (modal) tokens.splice(Math.max(0, verbSlot(tokens)), 0, modal);
    if (negate) tokens.splice(Math.max(0, verbSlot(tokens)), 0, "ne");
    if (aspect)
      tokens.splice(Math.min(tokens.length, verbSlot(tokens) + 1 + (negate ? 1 : 0)),
        0, aspect);

    if (isQuestion || leadWh) tokens.push("he");
    else {
      if (!evidential) {
        if (firstPerson && opinion) evidential = "so";
        else if (aspect === "sa") evidential = "yo";
        else {
          evidential = "lo";
          notes.push("Senel requires an evidential; guessed lo (you witnessed it). " +
            "Use to if told, mo if inferred, yo if general knowledge, so if internal.");
        }
      }
      tokens.push(evidential);
    }
    const s = tokens.join(" ");
    return {
      text: s.charAt(0).toUpperCase() + s.slice(1) + (isQuestion || leadWh ? "?" : "."),
      notes: [...new Set(notes)],
    };
  }

  /* --------------------------- Senel -> English --------------------------- */

  const head = (fn) => (v) => {
    const idx = v.indexOf(" ");
    return idx < 0 ? fn(v) : fn(v.slice(0, idx)) + v.slice(idx);
  };
  const ing = head((v) => {
    if (v.endsWith("e") && !v.endsWith("ee")) return v.slice(0, -1) + "ing";
    if (v.length > 2 && !"aeiouwxy".includes(v.slice(-1)) &&
        "aeiou".includes(v.slice(-2, -1)) && !"aeiou".includes(v.slice(-3, -2)))
      return v + v.slice(-1) + "ing";
    return v + "ing";
  });
  const past = head((v) => {
    if (v === "be") return "was";
    if (T.irregularPast[v]) return T.irregularPast[v];
    return v.endsWith("e") ? v + "d" : v + "ed";
  });
  const third = head((v) => {
    if (v === "is" || v === "there is") return v;
    if (v === "be") return "is";
    return /(?:s|sh|ch|x|o)$/.test(v) ? v + "es" : v + "s";
  });

  function sn2en(text) {
    const notes = [], recs = [];
    let evidential = "", question = false, imperative = false, tag = "";

    for (const tok of text.match(/[A-Za-z]+/g) || []) {
      const low = tok.toLowerCase();
      const entry = LEX.get(low);
      const cls = entry ? entry.c : null;
      if (cls === "EVID") { evidential = T.evidEn[low]; continue; }
      if (cls === "MOOD") {
        if (low === "he") question = true;
        else if (low === "we") imperative = true;
        else if (low === "ne") recs.push({ kind: "neg" });
        else if (low === "pe") { recs.unshift({ kind: "word", text: "let" }); tag = "hortative"; }
        else if (low === "ge") tag = "hypothetically";
        else if (low === "de") tag = "indeed";
        else if (low === "ye") tag = "right?";
        continue;
      }
      if (cls === "ASP") { recs.push({ kind: "asp", asp: low }); continue; }
      if (cls === "ROLE") {
        const r = T.roleEn[low];
        if (r) recs.push({ kind: "word", text: r });
        continue;
      }
      if (cls === "CONN" || cls === "DEG" || cls === "DET") {
        recs.push({ kind: cls.toLowerCase(), text: clean(entry.g), form: low });
        continue;
      }
      if (cls === "PRON") { recs.push({ kind: "pron", form: low }); continue; }
      const a = analyse(low);
      if (!a || a.kind === "UNKNOWN") {
        notes.push(`'${tok}' is not a Senel word`);
        recs.push({ kind: "word", text: `[${tok}]` });
        continue;
      }
      if (a.kind === "DERIVED") {
        const [base, mod] = a.gloss.split(" + ");
        recs.push({ kind: "derived", text: `${clean(base)} (${clean(mod)})`, pos: "noun" });
        continue;
      }
      if (a.kind === "COMPOUND") {
        recs.push({ kind: "derived", text: clean(a.gloss).replace(/-/g, " "), pos: "noun" });
        continue;
      }
      recs.push({ kind: "root", form: low, pos: posOf(low, cls),
        text: T.rootEn[low] || clean(entry.g) });
    }

    let verbIdx = recs.findIndex((r) => r.kind === "root" && r.pos === "verb");
    if (verbIdx < 0) verbIdx = recs.findIndex((r) => r.kind === "root" && r.pos === "property");

    const grouped = [];
    for (let n = 0; n < recs.length; ) {
      const r = recs[n];
      if (r.kind === "root" && r.pos === "noun") {
        const mods = [];
        let m = n + 1;
        while (m < recs.length && (recs[m].kind === "det" ||
          (recs[m].kind === "root" && recs[m].pos === "property" && m !== verbIdx))) {
          mods.push(recs[m].text); m++;
        }
        let headWord = r.text;
        if (r.form[0] === "y" || mods.some((x) => ["before", "after", "during"].includes(x))) {
          headWord = [headWord].concat(mods).join(" ");
          mods.length = 0;
        }
        const determined = mods.some((mod) => mod.split(" ").some((w) =>
          ["this", "that", "these", "those", "all", "every", "some", "many",
            "few", "no", "any", "which", "what"].includes(w)));
        if (!determined) mods.unshift("the");
        if (mods.some((x) => ["all", "many", "few", "some"].includes(x)))
          headWord = T.irregularPlural[headWord] ||
            (headWord.endsWith("s") ? headWord : headWord + "s");
        grouped.push(mods.concat([headWord]).join(" "));
        n = m;
        continue;
      }
      grouped.push(r);
      n++;
    }

    const words = [];
    let subject = null, predicateDone = false;
    const negated = recs.some((r) => r.kind === "neg");
    const aspect = (recs.find((r) => r.kind === "asp") || {}).asp || null;

    for (const item of grouped) {
      if (typeof item === "string") {
        if (subject === null) subject = item;
        words.push(item);
        continue;
      }
      const k = item.kind;
      if (k === "asp" || k === "neg") continue;
      if (k === "pron") {
        const form = T.pronEn[item.form];
        const afterLet = words.length && words[words.length - 1] === "let";
        words.push(subject !== null || afterLet ? form[1] : form[0]);
        if (subject === null) subject = item.form;
        continue;
      }
      if (k === "root" && (item.pos === "verb" || item.pos === "property")) {
        let verb = item.text;
        if (subject === null) { words.push("it"); subject = "tin"; }
        if (predicateDone) { words.push(verb); continue; }
        predicateDone = true;
        const plural = ["tun", "sun", "mun", "mon"].includes(subject) ||
          (typeof subject === "string" && (subject.endsWith("s") ||
            ["all", "many", "few", "some"].includes(subject.split(" ")[0]) ||
            Object.values(T.irregularPlural).includes(subject.split(" ").pop())));
        const thirdSg = subject === "tin" ||
          (typeof subject === "string" && !(subject in T.pronEn) && !plural);
        const be = subject === "min" ? "am"
          : plural || subject === "sin" || subject === "sun" ? "are" : "is";
        if (item.pos === "property" && !Object.values(T.rootEn).includes(verb)) {
          words.push(negated ? `${be} not ${verb}` : `${be} ${verb}`);
          continue;
        }
        const doAux = thirdSg ? "does" : "do";
        if (negated) words.push(aspect === null ? `${doAux} not ${verb}` : `not ${verb}`);
        else if (aspect === "ka") words.push(`${be} ${ing(verb)}`);
        else if (aspect === "ta") words.push(past(verb));
        else if (aspect === "ma") words.push((thirdSg ? "has " : "have ") + past(verb));
        else if (aspect === "fa") words.push(`${be} about to ${verb}`);
        else if (aspect === "sa") words.push("usually " + (thirdSg ? third(verb) : verb));
        else if (aspect === "ba") words.push(`${thirdSg ? "begins" : "begin"} to ${verb}`);
        else if (imperative) words.push(verb);
        else if (verb.split(" ")[0] === "be") words.push(be + verb.slice(2));
        else words.push(thirdSg ? third(verb) : verb);
        continue;
      }
      if (subject === null && k === "derived") subject = item.text;
      words.push(item.text);
    }

    let s = words.filter(Boolean).join(" ").trim();
    if (imperative) s = "please " + s;
    s = s ? s.charAt(0).toUpperCase() + s.slice(1) : "";
    s += question ? "?" : ".";
    if (tag) s += ` (${tag})`;
    return { text: s, notes: [...new Set(notes)], evidential };
  }

  /* ---- per-word breakdown, so the page can show why a word means what it does ---- */
  const DOMAIN_NAMES = {};
  for (const e of D.lexicon)
    if (e.c === "ROOT" || e.c === "NUM") {
      const m = /^(\w*)=(.+?) \/ (\w)=(.+)$/.exec(e.d || "");
      if (m) DOMAIN_NAMES[e.f] = { domain: m[2], sub: m[4] };
    }

  function breakdown(sentence) {
    return (sentence.match(/[A-Za-z]+/g) || []).map((tok) => {
      const low = tok.toLowerCase();
      const entry = LEX.get(low);
      const a = analyse(low);
      return {
        token: tok,
        cls: entry ? entry.c : a && a.kind !== "UNKNOWN" ? a.kind : "?",
        gloss: entry ? entry.g : a && a.gloss ? a.gloss : "not a Senel word",
      };
    });
  }

  global.Senel = { en2sn, sn2en, breakdown, analyse, LEX, data: D };
})(window);
