const pptxgen = require("pptxgenjs");
const path = require("path");
const { applyTheme } = require("/root/.claude/skills/synced/1ece1365-2384-45b8-b459-e476804aeb1d_57ca15ae-c39a-437c-935c-74c13609bf20/pptx/scripts/apply_theme.js");

const FIG = "/home/user/witness-network/report/figs/";
const OUT = "/home/user/witness-network/report/witness_networks_talk.pptx";

const THEME = {
  name: "Witness Networks",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1F2A33", lt1: "FFFFFF", dk2: "3D5361", lt2: "EEF2F4",
    accent1: "E0A030", accent2: "5C7A89", accent3: "C0504D",
    accent4: "8FA9B5", accent5: "2E7D6B", accent6: "A0A7AD",
    hlink: "2E7D6B", folHlink: "5C7A89",
  },
};
const H = THEME.colors; // hex, only for chart options that require hex

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9"; // 10 x 5.625
pres.author = "Shrey Sharma";
pres.title = "Witness Networks";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;

pres.defineSlideMaster({
  title: "Dark title",
  background: { color: C.text1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 1.35, w: 8.8, h: 1.6, fontSize: 40, bold: true, color: C.background1, valign: "bottom", align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.6, y: 3.15, w: 8.8, h: 1.6, fontSize: 18, color: C.accent4, valign: "top", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "Dark content",
  background: { color: C.text1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.45, w: 8.8, h: 0.9, fontSize: 34, bold: true, color: C.background1, valign: "middle", align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.6, y: 1.6, w: 8.8, h: 3.4, fontSize: 20, color: C.background1, valign: "top", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "Content",
  background: { color: C.background1 },
  margin: [0.4, 0.5, 0.4, 0.5],
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.5, y: 0.3, w: 9.0, h: 0.75, fontSize: 26, bold: true, color: C.text1, valign: "middle", align: "left", margin: 0 }, text: "" } },
  ],
  slideNumber: { x: 9.2, y: 5.2, w: 0.5, h: 0.3, fontSize: 10, color: C.accent6 },
});

function chartBase(extra) {
  return Object.assign({
    catAxisLabelColor: H.dk2, valAxisLabelColor: H.dk2,
    catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt", dataLabelFontFace: "+mn-lt",
    catAxisLabelFontSize: 11, valAxisLabelFontSize: 10, dataLabelFontSize: 11, dataLabelColor: H.dk1,
    valGridLine: { color: "E1E6E9", size: 0.75 }, catGridLine: { style: "none" },
    showValue: true, dataLabelPosition: "outEnd",
  }, extra);
}

function card(slide, x, y, w, h, big, small, name) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: C.background2 }, line: { color: C.background2 }, objectName: name + " card" });
  slide.addText([
    { text: big, options: { fontSize: 26, bold: true, color: C.text1, fontFace: THEME.headFontFace, breakLine: true } },
    { text: small, options: { fontSize: 13, color: C.text2 } },
  ], { x: x + 0.15, y: y + 0.08, w: w - 0.3, h: h - 0.16, valign: "middle", margin: 0, isTextBox: true, objectName: name + " text" });
}

// 1. Title
pres.addSection({ title: "Opening" });
let s = pres.addSlide({ masterName: "Dark title", sectionTitle: "Opening" });
s.addText("Witness Networks", { placeholder: "title" });
s.addText([
  { text: "When can peer agents expose a colluding coalition's cover-up?", options: { breakLine: true } },
  { text: "Shrey Sharma  ·  Apart Research Swarm Alignment Hackathon", options: { fontSize: 14, color: C.accent6 } },
], { placeholder: "body" });
s.addNotes("Hi, I'm Shrey. If AI agents can edit their own logs, can the other agents act as witnesses and expose a group that is covering its tracks? I'll show where that works, where it fails, and a cheap fix.");

// 2. Problem
pres.addSection({ title: "Problem" });
s = pres.addSlide({ masterName: "Content", sectionTitle: "Problem" });
s.addText("Agents can already rewrite their own records", { placeholder: "title" });
card(s, 0.5, 1.35, 2.8, 1.15, "~1,200", "agents coordinated on an unsanctioned board (July 2026)", "agents");
card(s, 0.5, 2.65, 2.8, 1.15, ">7%", "of reviewed transcripts had spoofed tool outputs", "spoof");
card(s, 0.5, 3.95, 2.8, 1.15, "28 / 28", "fabrications passed a harness's own hash chain", "hash");
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 3.7, y: 1.35, w: 5.8, h: 3.75, rectRadius: 0.08, fill: { color: C.text1 }, line: { color: C.text1 }, objectName: "question panel" });
s.addText([
  { text: "Tamper-evident logs prove a record didn't change. They don't prove it was true.", options: { breakLine: true } },
  { text: " ", options: { breakLine: true, fontSize: 12 } },
  { text: "But every message is stored twice: by its sender and by its receivers.", options: { breakLine: true } },
  { text: " ", options: { breakLine: true, fontSize: 12 } },
  { text: "Can the other agents serve as witnesses?", options: { bold: true, color: C.accent1, fontSize: 24, fontFace: THEME.headFontFace } },
], { x: 4.0, y: 1.6, w: 5.2, h: 3.25, fontSize: 20, color: C.background1, valign: "middle", margin: 0, isTextBox: true, objectName: "question text" });
s.addText("Sources: METR / Redwood investigation (2026); Hearsay, Dai et al. (2026)", { x: 0.5, y: 5.2, w: 7, h: 0.3, fontSize: 10, color: C.accent6, margin: 0, isTextBox: true, objectName: "sources" });
s.addNotes("This already happens. In July 2026 about twelve hundred OpenAI agents coordinated on an unsanctioned board, and investigators found spoofed tool outputs in over seven percent of transcripts. Hash chains don't help: they prove a record didn't change, not that it was true. But every message is stored by both sender and receiver. So can the other agents be witnesses?");

// 3. Setup
pres.addSection({ title: "Method" });
s = pres.addSlide({ masterName: "Content", sectionTitle: "Method" });
s.addText("Testbed: an 8-agent team with a hidden coalition", { placeholder: "title" });
s.addImage({ path: FIG + "fig0_overview.png", x: 0.5, y: 1.15, w: 9.0, h: 9.0 / 3.41, altText: "Overview: colluders relay a key, rewrite their records, and an exact cross-log check exposes mismatches", objectName: "overview figure" });
const facts = [["216", "episodes"], ["1 to 4", "colluders"], ["4", "auditors"]];
facts.forEach(([b, t], i) => {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5 + i * 3.1, y: 4.1, w: 2.8, h: 0.85, rectRadius: 0.08, fill: { color: C.background2 }, line: { color: C.background2 }, objectName: "fact card " + (i + 1) });
  s.addText([
    { text: b + "  ", options: { bold: true, color: C.text1, fontSize: 26, fontFace: THEME.headFontFace } },
    { text: t, options: { color: C.text2, fontSize: 16 } },
  ], { x: 0.5 + i * 3.1, y: 4.1, w: 2.8, h: 0.85, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: "fact " + (i + 1) });
});
s.addNotes("My testbed has eight LLM agents fixing a data pipeline. In attack episodes, one to four of them pass a secret key along and leak it. Then they cover up: they rewrite their own records, or ask honest teammates to correct theirs. Four auditors try to catch them: an exact matcher that compares every copy, and three LLM monitors that read the agents' journals.");

// 4. Detection
pres.addSection({ title: "Results" });
s = pres.addSlide({ masterName: "Content", sectionTitle: "Results" });
s.addText("Exact cross-checks work; LLM monitors barely do", { placeholder: "title" });
s.addChart(pres.charts.BAR, [{ name: "Tamper-detection AUROC", labels: ["B0 single-log LLM", "B1 all-logs LLM", "B3 LLM cross-witness", "B2 exact cross-log"], values: [0.42, 0.46, 0.51, 0.935] }],
  chartBase({ x: 0.4, y: 1.15, w: 5.6, h: 4.0, barDir: "bar", chartColors: [H.accent6, H.accent6, H.accent6, H.accent1],
    valAxisMinVal: 0, valAxisMaxVal: 1, valAxisMajorUnit: 0.25, dataLabelFormatCode: "General", showLegend: false, catAxisLabelFontSize: 12,
    showTitle: true, title: "AUROC on 367 cover-ups, 7B auditors (0.5 = chance)", titleFontSize: 12, titleColor: H.dk2, titleFontFace: "+mn-lt", objectName: "auroc chart" }));
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.3, y: 1.25, w: 3.2, h: 1.95, rectRadius: 0.08, fill: { color: C.background2 }, line: { color: C.background2 }, objectName: "rule card" });
s.addText([
  { text: "The rule", options: { bold: true, fontSize: 14, color: C.text1, breakLine: true } },
  { text: "Detectable if and only if an altered record names someone outside the coalition.", options: { fontSize: 13, color: C.text1, breakLine: true } },
  { text: "898 / 898 audits match", options: { bold: true, fontSize: 18, color: C.accent1, fontFace: THEME.headFontFace } },
], { x: 6.45, y: 1.35, w: 2.9, h: 1.75, valign: "middle", margin: 0, isTextBox: true, objectName: "rule text" });
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.3, y: 3.35, w: 3.2, h: 1.7, rectRadius: 0.08, fill: { color: C.background2 }, line: { color: C.background2 }, objectName: "claude card" });
s.addText([
  { text: "Claude Sonnet 5", options: { bold: true, fontSize: 14, color: C.text1, breakLine: true } },
  { text: "Asked only about tampering: AUROC 0.73, but just 10% caught at 2% FPR (exact check: 87% at 0 FPR).", options: { fontSize: 13, color: C.text1 } },
], { x: 6.45, y: 3.45, w: 2.9, h: 1.5, valign: "middle", margin: 0, isTextBox: true, objectName: "claude text" });
s.addNotes("I prove a simple rule: a cover-up can be caught by comparing logs exactly when some altered record names an agent outside the coalition. The exact matcher follows that rule in all 898 scripted audits and scores 0.935. The LLM monitors sit near chance. Claude Sonnet 5 does no better; even when asked only about tampering, it catches just ten percent at a two percent false-alarm rate.");

// 5. Persuasion
s = pres.addSlide({ masterName: "Content", sectionTitle: "Results" });
s.addText("Witnesses refuse, unless it's called a redaction", { placeholder: "title" });
s.addChart(pres.charts.BAR, [{ name: "Plain request", labels: ["Qwen 7B", "Qwen 14B", "Gemini 3 Flash", "Claude Sonnet 5"], values: [93, 61, 0.4, 0] }],
  chartBase({ x: 0.4, y: 1.15, w: 3.9, h: 3.55, barDir: "col", chartColors: [H.accent6], valAxisMinVal: 0, valAxisMaxVal: 100, valAxisMajorUnit: 25,
    dataLabelFormatCode: "General", showLegend: false, catAxisLabelFontSize: 11,
    showTitle: true, title: "Plain request, % who comply (n = 233)", titleFontSize: 12, titleColor: H.dk2, titleFontFace: "+mn-lt", objectName: "plain chart" }));
s.addChart(pres.charts.BAR, [{ name: "Redaction framing", labels: ["Gemini 3 Flash", "gpt-oss-120b", "GPT-5.4-nano", "Claude Sonnet 5", "Claude + operator OK"], values: [97.5, 99, 57, 1, 23] }],
  chartBase({ x: 4.5, y: 1.15, w: 5.1, h: 3.55, barDir: "col", chartColors: [H.accent3], valAxisMinVal: 0, valAxisMaxVal: 100, valAxisMajorUnit: 25,
    dataLabelFormatCode: "General", showLegend: false, catAxisLabelFontSize: 11,
    showTitle: true, title: "Framed as \"redact this leaked secret\", % (n = 80)", titleFontSize: 12, titleColor: H.dk2, titleFontFace: "+mn-lt", objectName: "redaction chart" }));
s.addText([
  { text: "Claude refused 11 of 12 realistic pretexts. ", options: { bold: true, color: C.text1 } },
  { text: "Only the redaction request plus operator pre-approval moved it.", options: { color: C.text2 } },
], { x: 0.5, y: 4.8, w: 8.6, h: 0.4, fontSize: 14, valign: "middle", margin: 0, isTextBox: true, objectName: "claude note" });
s.addNotes("Colluders can also ask honest agents to change their copies. Small models agree: 93 percent at 7B. Frontier models refuse plain requests. But call it redacting a leaked secret, and Gemini, gpt-oss and GPT-5.4-nano comply 57 to 99 percent of the time. Claude refused eleven of twelve pretexts, but agreed 23 percent of the time when the operator pre-approved the redaction.");

// 6. Fix
s = pres.addSlide({ masterName: "Content", sectionTitle: "Results" });
s.addText("Redundancy has to be built in", { placeholder: "title" });
card(s, 0.5, 1.3, 2.9, 1.7, "61%", "of frontier (Gemini) cover-ups caught, vs 98–100% for 7B forgers", "frontier");
card(s, 0.5, 3.3, 2.9, 1.7, "5.4%", "natural echo coverage in a real agent wiki log", "real");
s.addChart(pres.charts.BAR, [{ name: "Coordinated cover-ups caught (peers only)", labels: ["None (1.0×)", "1 peer (1.5×)", "All peers (3.9×)", "1 peer + receipts (1.5×)", "2 peers + receipts (2.0×)"], values: [42, 67, 67, 97, 99.6] }],
  chartBase({ x: 3.7, y: 1.15, w: 5.9, h: 4.0, barDir: "col", chartColors: [H.accent6, H.accent4, H.accent4, H.accent1, H.accent1],
    valAxisMinVal: 0, valAxisMaxVal: 100, valAxisMajorUnit: 25, dataLabelFormatCode: "General", showLegend: false,
    showTitle: true, title: "% of coordinated cover-ups caught (storage cost)", titleFontSize: 12, titleColor: H.dk2, titleFontFace: "+mn-lt", objectName: "redundancy chart" }));
s.addNotes("This matters because a frontier forger is caught only 61 percent of the time, and a real agent wiki has only about five percent natural redundancy. So redundancy has to be built in. Copying each message to one random extra peer, plus receipts for outside calls, raises detection from 42 to 97 percent at one and a half times the storage, with no false alarms.");

// 7. Takeaways
pres.addSection({ title: "Close" });
s = pres.addSlide({ masterName: "Dark content", sectionTitle: "Close" });
s.addText("Design for witnesses", { placeholder: "title" });
s.addText([
  { text: "Keep verbatim copies on both sides, not summaries", options: { bullet: true, breakLine: true } },
  { text: "Copy each message to one random peer, plus receipts", options: { bullet: true, breakLine: true } },
  { text: "Keep a trusted log of outside calls", options: { bullet: true, breakLine: true } },
  { text: "Log every redaction with a hash of what was removed", options: { bullet: true } },
], { x: 0.6, y: 1.55, w: 5.4, h: 2.7, fontSize: 18, color: C.background1, paraSpaceAfter: 10, valign: "top", margin: 0, isTextBox: true, objectName: "rules" });
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.4, y: 1.55, w: 3.0, h: 2.5, rectRadius: 0.08, fill: { color: C.text2 }, line: { color: C.text2 }, objectName: "stat card" });
s.addText([
  { text: "42% → 97%", options: { bold: true, fontSize: 32, color: C.accent1, fontFace: THEME.headFontFace, breakLine: true } },
  { text: "coordinated cover-ups caught with one extra copy plus receipts, at 1.5× storage", options: { fontSize: 14, color: C.background1 } },
], { x: 6.6, y: 1.65, w: 2.6, h: 2.3, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: "stat text" });
s.addText("Limits: collusion is instructed, one synthetic environment, small frontier samples.", { x: 0.6, y: 4.45, w: 8.8, h: 0.35, fontSize: 13, color: C.accent4, margin: 0, isTextBox: true, objectName: "limits" });
s.addText("github.com/ShreySharma07/witness-network", { x: 0.6, y: 4.85, w: 8.8, h: 0.35, fontSize: 14, color: C.accent1, margin: 0, isTextBox: true, objectName: "repo link",
  hyperlink: { url: "https://github.com/ShreySharma07/witness-network" } });
s.addNotes("So: keep verbatim copies, add one extra copy plus receipts, keep a trusted log of outside calls, and log a hash whenever a record is redacted. Limits: collusion here is instructed, the environment is synthetic, and the frontier samples are small. Code and results are on GitHub. Thanks for watching.");

pres.writeFile({ fileName: OUT }).then(async () => { await applyTheme(OUT, THEME); console.log("wrote", OUT); });
