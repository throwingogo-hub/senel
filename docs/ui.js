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

  setDirection(true);
  input.value = "I am going to your house.";
  translate();
})();
