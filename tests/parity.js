/* Runs the browser translator under Node so CI can compare it with translate.py. */
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const docs = path.join(__dirname, "..", "docs");
const ctx = { console };
ctx.window = ctx;
vm.createContext(ctx);
for (const f of ["data.js", "aliases.js", "app.js"]) {
  vm.runInContext(fs.readFileSync(path.join(docs, f), "utf8"), ctx, { filename: f });
}

const assert = (condition, message) => { if (!condition) throw new Error(message); };
assert(ctx.Senel.englishPhrases.length >= 900, "browser English catalogue regressed");
assert(ctx.Senel.resolveEnglish("black").f === "ninnir", "browser alias lookup failed");
const unknown = ctx.Senel.en2sn("I am gooning for sure.").text;
assert(unknown.includes("«gooning»") && !unknown.includes(" ka "),
  "unknown -ing term triggered a false progressive");
const strictUnknown = ctx.Senel.en2sn("An unknownword remains.", { strict: true }).text;
assert(strictUnknown.includes("[unknownword]"), "strict fallback disappeared");
const overridden = ctx.Senel.en2sn("I am gooning for sure.",
  { overrides: { gooning: "run" } }).text;
assert(overridden.includes("bel ka") && !overridden.includes("gooning"),
  "explicit unknown-term resolution failed");

const cases = JSON.parse(fs.readFileSync(path.join(__dirname, "parity_cases.json"), "utf8"));
const out = { en2sn: {}, en2snStrict: {}, sn2en: {} };
for (const s of cases.en) out.en2sn[s] = ctx.Senel.en2sn(s).text;
for (const s of cases.enStrict || [])
  out.en2snStrict[s] = ctx.Senel.en2sn(s, { strict: true }).text;
for (const s of cases.sn) {
  const r = ctx.Senel.sn2en(s);
  out.sn2en[s] = r.text + (r.evidential ? "  " + r.evidential : "");
}
process.stdout.write(JSON.stringify(out));
