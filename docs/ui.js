/* Page wiring: live translation, direction swap, per-word breakdown. */
(function () {
  "use strict";

  const $ = (id) => document.getElementById(id);
  const input = $("input"), output = $("output"), notes = $("notes"),
    cards = $("cards"), breakdown = $("breakdown"), counter = $("counter"),
    syllables = $("syllables"), strictMode = $("strictMode"),
    translationOptions = $("translationOptions"), unknownResolver = $("unknownResolver"),
    unknownItems = $("unknownItems"), conceptList = $("conceptList");

  let toSenel = true;
  let overrides = {};

  const CLASS_LABEL = {
    ROOT: "root", NUM: "number", ROLE: "role", ASP: "aspect", EVID: "evidence",
    MOOD: "mood", DEG: "degree", CONN: "connective", DET: "determiner",
    PRON: "pronoun", AFFIX: "affix", DERIVED: "derived", COMPOUND: "compound",
    FOREIGN: "foreign term",
  };

  const EXAMPLES = {
    toSenel: ["I am going to your house.", "Where is the toilet?",
      "The dog is bigger than the cat.", "We will eat together.", "I don't know."],
    toEnglish: ["Lol ka mo.", "Til em i pin en sin lo.", "Pe mun hen tal.",
      "Sin nal ta til yen yin he?", "Ran lam har fum nu es i fom nu rum yo."],
  };

  function countSyllables(text) {
    let total = 0;
    const senelOnly = text.replace(/«[^»]*»|\[[^\]]*\]/g, "");
    for (const w of senelOnly.match(/[A-Za-z]+/g) || []) {
      const m = w.toLowerCase().match(/[aeiou]/g);
      total += m ? m.length : 0;
    }
    return total;
  }

  function renderNotes(list) {
    if (!list.length) { notes.hidden = true; return; }
    notes.hidden = false;
    notes.innerHTML = "<ul>" +
      list.map((n) => `<li>${n.replace(/&/g, "&amp;").replace(/</g, "&lt;")}</li>`)
        .join("") + "</ul>";
  }

  function renderUnknownResolver(senelText) {
    const found = [];
    const pattern = /«([^»]+)»|\[([^\]]+)\]/g;
    for (const match of senelText.matchAll(pattern)) {
      const term = match[1] || match[2];
      if (!found.includes(term)) found.push(term);
    }
    if (!toSenel || !found.length) {
      unknownResolver.hidden = true;
      unknownItems.replaceChildren();
      return;
    }

    unknownResolver.hidden = false;
    unknownItems.replaceChildren();
    for (const term of found) {
      const row = document.createElement("div");
      row.className = "unknownItem";

      const word = document.createElement("code");
      word.textContent = term;

      const field = document.createElement("input");
      field.type = "text";
      field.setAttribute("list", "conceptList");
      field.placeholder = "e.g. run, joke, dark colour";
      field.value = overrides[term] || "";
      field.setAttribute("aria-label", `Map ${term} to an existing concept`);

      const apply = document.createElement("button");
      apply.type = "button";
      apply.textContent = "Use meaning";
      const submit = () => {
        const record = Senel.resolveEnglish(field.value);
        if (!record) {
          field.classList.add("invalid");
          field.setAttribute("aria-invalid", "true");
          field.focus();
          return;
        }
        field.classList.remove("invalid");
        field.removeAttribute("aria-invalid");
        overrides[term] = field.value;
        translate();
      };
      apply.addEventListener("click", submit);
      field.addEventListener("keydown", (event) => {
        if (event.key === "Enter") { event.preventDefault(); submit(); }
      });
      field.addEventListener("input", () => {
        field.classList.remove("invalid");
        field.removeAttribute("aria-invalid");
      });

      row.append(word, field, apply);
      unknownItems.append(row);
    }
  }

  function renderBreakdown(senelText) {
    const rows = Senel.breakdown(senelText).filter((r) => r.cls !== "?" || r.token);
    if (!rows.length) { breakdown.hidden = true; return; }
    breakdown.hidden = false;
    cards.innerHTML = rows.map((r) => {
      const entry = Senel.LEX.get(r.token.toLowerCase());
      let derivation = "";
      if (entry && entry.d && entry.d.includes("=")) {
        const m = /^(\w*)=(.+?) \/ (\w)=(.+)$/.exec(entry.d);
        if (m) {
          const onset = m[1] === "zero" ? "—" : m[1];
          derivation = `<div class="d"><b>${onset}</b> ${m[2]}<br><b>${m[3]}</b> ${m[4]}</div>`;
        } else {
          derivation = `<div class="d">${entry.d}</div>`;
        }
      }
      const label = CLASS_LABEL[r.cls] || r.cls.toLowerCase();
      return `<div class="card"><div class="w">${r.token}</div>` +
        `<div class="g">${r.gloss}</div>${derivation}` +
        `<span class="tag">${label}</span></div>`;
    }).join("");
  }

  function translate() {
    const text = input.value;
    counter.textContent = `${text.length} character${text.length === 1 ? "" : "s"}`;
    if (!text.trim()) {
      output.textContent = "";
      renderNotes([]);
      breakdown.hidden = true;
      unknownResolver.hidden = true;
      syllables.textContent = "";
      return;
    }
    const result = toSenel ? Senel.en2sn(text, {
      strict: strictMode.checked, overrides,
    })
      : Senel.sn2en(text);
    let shown = result.text;
    if (!toSenel && result.evidential) shown += "  " + result.evidential;
    output.textContent = shown;
    renderNotes(result.notes);
    renderUnknownResolver(toSenel ? result.text : "");
    const senelSide = toSenel ? result.text : text;
    syllables.textContent = `${countSyllables(senelSide)} syllables in Senel`;
    renderBreakdown(senelSide);
  }

  function setDirection(senel) {
    toSenel = senel;
    overrides = {};
    $("fromLang").textContent = senel ? "English" : "Senel";
    $("toLang").textContent = senel ? "Senel" : "English";
    input.placeholder = senel ? "Type something…" : "Type Senel, e.g. Lol ka mo.";
    translationOptions.hidden = !senel;
    document.querySelectorAll(".examples button").forEach((b, i) => {
      const list = senel ? EXAMPLES.toSenel : EXAMPLES.toEnglish;
      b.textContent = list[i];
      b.dataset.ex = list[i];
    });
  }

  $("swap").addEventListener("click", () => {
    const previous = output.textContent.replace(/\s*\[[^\]]*\]\s*$/, "").trim();
    setDirection(!toSenel);
    if (previous) input.value = previous;
    translate();
    input.focus();
  });

  document.querySelectorAll(".examples button").forEach((b) => {
    b.addEventListener("click", () => {
      overrides = {};
      input.value = b.dataset.ex;
      translate();
      input.focus();
    });
  });

  $("copy").addEventListener("click", async () => {
    if (!output.textContent) return;
    try {
      await navigator.clipboard.writeText(output.textContent);
      const btn = $("copy");
      btn.textContent = "Copied";
      setTimeout(() => (btn.textContent = "Copy"), 1200);
    } catch (_) { /* clipboard unavailable */ }
  });

  strictMode.addEventListener("change", translate);

  let timer;
  input.addEventListener("input", () => {
    overrides = {};
    clearTimeout(timer);
    timer = setTimeout(translate, 120);
  });

  for (const phrase of Senel.englishPhrases) {
    const option = document.createElement("option");
    option.value = phrase;
    conceptList.append(option);
  }

  /* ---- Learn mode: the 16 domains, a decode drill, and the honesty lesson ---- */
  const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;");
  const rand = (arr) => arr[Math.floor(Math.random() * arr.length)];
  const parseDeriv = (d) => /^(\w*)=(.+?) \/ (\w)=(.+)$/.exec(d || "");

  const DOMAINS = {}, DOMAIN_ORDER = [];
  for (const e of Senel.data.lexicon) {
    if (e.c !== "ROOT" && e.c !== "NUM") continue;
    const m = parseDeriv(e.d);
    if (!m) continue;
    const onset = m[1] === "zero" ? "" : m[1];
    if (!DOMAINS[onset]) { DOMAINS[onset] = { name: m[2], subs: {} }; DOMAIN_ORDER.push(onset); }
    (DOMAINS[onset].subs[m[3]] = DOMAINS[onset].subs[m[3]] || { name: m[4], roots: [] })
      .roots.push({ f: e.f, g: e.g });
  }

  const domainGrid = $("domainGrid"), domainDetail = $("domainDetail");
  let openDomain = null;
  function renderDomainGrid() {
    domainGrid.innerHTML = DOMAIN_ORDER.map((onset) => {
      const d = DOMAINS[onset];
      return `<button class="domainTile${onset === openDomain ? " active" : ""}" ` +
        `data-onset="${onset}" role="listitem"><span class="dLetter">${onset || "∅"}</span>` +
        `<span class="dName">${esc(d.name)}</span></button>`;
    }).join("");
  }
  domainGrid.addEventListener("click", (ev) => {
    const tile = ev.target.closest(".domainTile");
    if (!tile) return;
    openDomain = tile.dataset.onset === openDomain ? null : tile.dataset.onset;
    renderDomainGrid();
    if (openDomain === null) { domainDetail.hidden = true; return; }
    const d = DOMAINS[openDomain];
    domainDetail.hidden = false;
    domainDetail.innerHTML = `<h4><span class="dLetter big">${openDomain || "∅"}</span> ` +
      `${esc(d.name)}</h4>` + Object.entries(d.subs).map(([v, sub]) =>
        `<div class="subRow"><span class="subVowel">${openDomain}${v}-</span>` +
        `<span class="subName">${esc(sub.name)}</span><span class="subRoots">` +
        sub.roots.map((r) => `<code title="${esc(r.g)}">${r.f}</code>`).join(" ") +
        `</span></div>`).join("");
    domainDetail.scrollIntoView({ behavior: "smooth", block: "nearest" });
  });

  const CONTENT = Senel.data.lexicon.filter((e) =>
    e.c === "ROOT" && e.f.length === 3 && DOMAINS[e.f[0]]);
  const drillWord = $("drillWord"), drillChoices = $("drillChoices"),
    drillReveal = $("drillReveal"), drillScore = $("drillScore");
  let streak = 0, best = 0, current = null, answered = false;
  function newDrill() {
    answered = false;
    current = rand(CONTENT);
    drillWord.textContent = current.f;
    drillReveal.hidden = true;
    const options = new Set([current.f[0]]);
    while (options.size < 4) options.add(rand(DOMAIN_ORDER));
    drillChoices.innerHTML = [...options].sort(() => Math.random() - 0.5).map((onset) =>
      `<button class="choice" data-onset="${onset}">${onset || "∅"} · ${esc(DOMAINS[onset].name)}</button>`)
      .join("");
  }
  drillChoices.addEventListener("click", (ev) => {
    const btn = ev.target.closest(".choice");
    if (!btn || answered) return;
    answered = true;
    const correct = current.f[0];
    drillChoices.querySelectorAll(".choice").forEach((b) => {
      if (b.dataset.onset === correct) b.classList.add("right");
      else if (b === btn) b.classList.add("wrong");
      b.disabled = true;
    });
    if (btn.dataset.onset === correct) { streak++; best = Math.max(best, streak); }
    else streak = 0;
    drillScore.textContent = `streak ${streak} · best ${best}`;
    const m = parseDeriv(current.d);
    drillReveal.hidden = false;
    drillReveal.innerHTML = `<b>${current.f}</b> = “${esc(current.g)}”` +
      (m ? ` — <span class="muted">${esc(m[2])} / ${esc(m[4])}</span>` : "");
  });
  $("drillNext").addEventListener("click", newDrill);

  const families = {};
  for (const e of CONTENT) (families[e.f.slice(1)] = families[e.f.slice(1)] || []).push(e);
  const denseFamilies = Object.entries(families).filter(([, v]) => v.length >= 8)
    .sort((a, b) => b[1].length - a[1].length).map(([k]) => k);
  const familyDemo = $("familyDemo");
  let famIdx = 0;
  function renderFamily() {
    const key = denseFamilies[famIdx % denseFamilies.length];
    familyDemo.innerHTML = `<p class="famHead">Every word here ends <code>-${key}</code>; ` +
      `only the first sound differs:</p><div class="famRow">` +
      families[key].slice().sort((a, b) => a.f.localeCompare(b.f)).map((r) =>
        `<span class="famWord"><b>${r.f}</b><span>${esc(r.g)}</span></span>`).join("") + `</div>`;
  }
  $("familyNext").addEventListener("click", () => { famIdx++; renderFamily(); });

  let learnBuilt = false;
  function showTab(learn) {
    $("translateView").hidden = learn;
    $("learnView").hidden = !learn;
    $("tabTranslate").classList.toggle("active", !learn);
    $("tabLearn").classList.toggle("active", learn);
    $("tabTranslate").setAttribute("aria-selected", String(!learn));
    $("tabLearn").setAttribute("aria-selected", String(learn));
    if (learn && !learnBuilt) {
      learnBuilt = true;
      renderDomainGrid();
      newDrill();
      renderFamily();
    }
  }
  $("tabTranslate").addEventListener("click", () => showTab(false));
  $("tabLearn").addEventListener("click", () => showTab(true));

  setDirection(true);
  input.value = "I am going to your house.";
  translate();
})();
