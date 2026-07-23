/* Page wiring: live translation, direction swap, per-word breakdown. */
(function () {
  "use strict";

  const $ = (id) => document.getElementById(id);
  const input = $("input"), output = $("output"), notes = $("notes"),
    cards = $("cards"), breakdown = $("breakdown"), counter = $("counter"),
    syllables = $("syllables");

  let toSenel = true;

  const CLASS_LABEL = {
    ROOT: "root", NUM: "number", ROLE: "role", ASP: "aspect", EVID: "evidence",
    MOOD: "mood", DEG: "degree", CONN: "connective", DET: "determiner",
    PRON: "pronoun", AFFIX: "affix", DERIVED: "derived", COMPOUND: "compound",
  };

  const EXAMPLES = {
    toSenel: ["I am going to your house.", "Where is the toilet?",
      "The dog is bigger than the cat.", "We will eat together.", "I don't know."],
    toEnglish: ["Lol ka mo.", "Til em i pin en sin lo.", "Pe mun hen tal.",
      "Sin nal ta til yen yin he?", "Ran lam har fum nu es i fom nu rum yo."],
  };

  function countSyllables(text) {
    let total = 0;
    for (const w of text.match(/[A-Za-z]+/g) || []) {
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
      syllables.textContent = "";
      return;
    }
    const result = toSenel ? Senel.en2sn(text) : Senel.sn2en(text);
    let shown = result.text;
    if (!toSenel && result.evidential) shown += "  " + result.evidential;
    output.textContent = shown;
    renderNotes(result.notes);
    const senelSide = toSenel ? result.text : text;
    syllables.textContent = `${countSyllables(senelSide)} syllables in Senel`;
    renderBreakdown(senelSide);
  }

  function setDirection(senel) {
    toSenel = senel;
    $("fromLang").textContent = senel ? "English" : "Senel";
    $("toLang").textContent = senel ? "Senel" : "English";
    input.placeholder = senel ? "Type something…" : "Type Senel, e.g. Lol ka mo.";
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

  let timer;
  input.addEventListener("input", () => {
    clearTimeout(timer);
    timer = setTimeout(translate, 120);
  });

  setDirection(true);
  input.value = "I am going to your house.";
  translate();
})();
