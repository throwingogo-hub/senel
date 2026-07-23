/* Runs the browser translator under Node so CI can compare it with translate.py. */
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const docs = path.join(__dirname, "..", "docs");
const ctx = { console };
ctx.window = ctx;
vm.createContext(ctx);
for (const f of ["data.js", "app.js"]) {
  vm.runInContext(fs.readFileSync(path.join(docs, f), "utf8"), ctx, { filename: f });
}

const cases = JSON.parse(fs.readFileSync(path.join(__dirname, "parity_cases.json"), "utf8"));
const out = { en2sn: {}, sn2en: {} };
for (const s of cases.en) out.en2sn[s] = ctx.Senel.en2sn(s).text;
for (const s of cases.sn) {
  const r = ctx.Senel.sn2en(s);
  out.sn2en[s] = r.text + (r.evidential ? "  " + r.evidential : "");
}
process.stdout.write(JSON.stringify(out));
