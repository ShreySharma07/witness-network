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
s.addNotes("Hi, I'm Shrey. This project asks a simple question. If AI agents can edit their own logs, can the other agents in the system act as witnesses and expose a group that is covering its tracks? I'll show where that works, where it fails, and a cheap fix.");

// 2. Problem
pres.addSection({ title: "Problem" });
s = pres.addSlide({ masterName: "Content", sectionTitle: "Problem" });
s.addText("Agents can already rewrite their own records", { placeholder: "title" });
card(s, 0.5, 1.35, 2.8, 1.15, "~1,200", "agents coordinated on an unsanctioned board (July 2026)", "agents");
card(s, 0.5, 2.65, 2.8, 1.15, ">7%", "of reviewed transcripts had spoofed tool outputs", "spoof");
card(s, 0.5, 3.95, 2.8, 1.15, "28 / 28", "fabrications passed a harness's own hash chain", "hash");
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 3.7, y: 1.35, w: 5.8, h: 3.75, rectRadius: 0.08, fill: { color: C.text1 }, line: { color: C.text1 }, objectName: "question panel" });
s.addText([
  { text: "Tamper-evident logs prove a record didn't change.", options: { breakLine: true } },
  { text: "They don't prove it was true.", options: { breakLine: true } },
  { text: " ", options: { breakLine: true, fontSize: 10 } },
  { text: "In a multi-agent system every message is stored by its sender and its receivers.", options: { breakLine: true } },
  { text: " ", options: { breakLine: true, fontSize: 10 } },
  { text: "So: can the other agents serve as witnesses?", options: { bold: true, color: C.accent1, fontSize: 20 } },
], { x: 4.0, y: 1.55, w: 5.2, h: 3.35, fontSize: 17, color: C.background1, valign: "middle", margin: 0, isTextBox: true, objectName: "question text" });
s.addText("Sources: METR / Redwood investigation (2026); Hearsay, Dai et al. (2026)", { x: 0.5, y: 5.2, w: 7, h: 0.3, fontSize: 10, color: C.accent6, margin: 0, isTextBox: true, objectName: "sources" });
s.addNotes("This is not hypothetical. In July 2026 around twelve hundred OpenAI agents coordinated on an unsanctioned message board, and investigators found spoofed tool outputs in more than seven percent of transcripts. Hash chains don't help: they prove a record didn't change, not that it was true. But in a multi-agent system, every message is stored twice, by the sender and by the receiver. So can the other agents be witnesses?");

// 3. Setup
pres.addSection({ title: "Method" });
s = pres.addSlide({ masterName: "Content", sectionTitle: "Method" });
s.addText("Testbed: an 8-agent team with a hidden coalition", { placeholder: "title" });
s.addImage({ path: FIG + "fig0_overview.png", x: 0.5, y: 1.2, w: 9.0, h: 9.0 / 3.41, altText: "Overview: colluders relay a key, rewrite their records, and an exact cross-log check exposes mismatches", objectName: "overview figure" });
const facts = [["216", "episodes, 4 communication graphs"], ["1 to 4", "colluders leak a key, then edit logs"], ["4", "auditors: exact matcher + 3 LLM monitors"]];
facts.forEach(([b, t], i) => {
  s.addText([
    { text: b + "  ", options: { bold: true, color: C.accent1, fontSize: 22, fontFace: THEME.headFontFace } },
    { text: t, options: { color: C.text1, fontSize: 14 } },
  ], { x: 0.5 + i * 3.05, y: 4.15, w: 2.9, h: 0.8, valign: "middle", margin: 0, isTextBox: true, objectName: "fact " + (i + 1) });
});
s.addNotes("I built a testbed with eight LLM agents fixing a data pipeline. In attack episodes, one to four of them secretly pass a key along and send it outside. Then they cover up: they delete or rewrite their own records, or ask honest teammates to 'correct' theirs. I compare four auditors: an exact matcher that checks every copy of every message, and three LLM monitors that read the agents' journals.");

// 4. Detection
pres.addSection({ title: "Results" });
s = pres.addSlide({ masterName: "Content", sectionTitle: "Results" });
s.addText("Exact cross-checks work; LLM monitors don't", { placeholder: "title" });
s.addChart(pres.charts.BAR, [{ name: "Tamper-detection AUROC", labels: ["B0 single-log (7B)", "B1 all-logs (7B)", "B3 LLM cross-witness", "Claude Sonnet 5 (B1)*", "B2 exact cross-log"], values: [0.42, 0.46, 0.51, 0.49, 0.935] }],
  chartBase({ x: 0.4, y: 1.15, w: 5.6, h: 4.0, barDir: "bar", chartColors: [H.accent6, H.accent6, H.accent6, H.accent6, H.accent1],
    valAxisMinVal: 0, valAxisMaxVal: 1, valAxisMajorUnit: 0.25, dataLabelFormatCode: "General", showLegend: false,
    showTitle: true, title: "Tamper-detection AUROC (0.5 = chance; *adaptive cover-ups)", titleFontSize: 12, titleColor: H.dk2, titleFontFace: "+mn-lt", objectName: "auroc chart" }));
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.3, y: 1.25, w: 3.2, h: 3.8, rectRadius: 0.08, fill: { color: C.background2 }, line: { color: C.background2 }, objectName: "condition panel" });
s.addText([
  { text: "The rule", options: { bold: true, fontSize: 16, color: C.text1, breakLine: true } },
  { text: "A cover-up is detectable if and only if an altered record names someone outside the coalition.", options: { fontSize: 14, color: C.text1, breakLine: true } },
  { text: " ", options: { fontSize: 8, breakLine: true } },
  { text: "898 / 898", options: { bold: true, fontSize: 24, color: C.accent1, fontFace: THEME.headFontFace, breakLine: true } },
  { text: "scripted audits match the rule exactly", options: { fontSize: 13, color: C.text2 } },
], { x: 6.5, y: 1.4, w: 2.8, h: 3.5, valign: "middle", margin: 0, isTextBox: true, objectName: "condition text" });
s.addNotes("First result. I prove a simple rule: a cover-up can be caught by comparing logs exactly when some altered record names an agent outside the coalition. The exact matcher follows that rule in all 898 scripted audits and reaches 0.935 AUROC. The LLM monitors, all the way up to Claude Sonnet 5, sit at chance. They detect the attack, but a cleaned-up journal fools them.");

// 5. Persuasion
s = pres.addSlide({ masterName: "Content", sectionTitle: "Results" });
s.addText("Witnesses refuse, unless it's called a redaction", { placeholder: "title" });
s.addChart(pres.charts.BAR, [
  { name: "Plain correction request", labels: ["Gemini 3 Flash", "gpt-oss-120b", "GPT-5.4-nano", "Claude Sonnet 5"], values: [0, 0, 0, 0] },
  { name: "\"Redact this leaked secret\"", labels: ["Gemini 3 Flash", "gpt-oss-120b", "GPT-5.4-nano", "Claude Sonnet 5"], values: [97.5, 99, 57, 1] },
], chartBase({ x: 0.4, y: 1.15, w: 5.8, h: 4.0, barDir: "col", barGrouping: "clustered", chartColors: [H.accent6, H.accent3],
  valAxisMinVal: 0, valAxisMaxVal: 100, valAxisMajorUnit: 25, dataLabelFormatCode: "General", showLegend: true, legendPos: "b", legendFontSize: 11, legendFontFace: "+mn-lt", legendColor: H.dk2,
  showTitle: true, title: "% of honest witnesses who change their record (n = 80)", titleFontSize: 12, titleColor: H.dk2, titleFontFace: "+mn-lt", objectName: "compliance chart" }));
card(s, 6.5, 1.25, 3.0, 1.15, "93% → 0%", "plain requests: 7B agents vs Claude Sonnet 5", "trend");
card(s, 6.5, 2.6, 3.0, 1.15, "23%", "Claude complies when the operator pre-approves the redaction", "claude");
card(s, 6.5, 3.95, 3.0, 1.15, "11 / 12", "other realistic pretexts Claude refused", "refused");
s.addNotes("Second result: colluders can ask honest agents to change their copies. Small 7B models agree 93 percent of the time; frontier models almost never do. But the framing matters. Call it redacting a leaked secret and Gemini, gpt-oss and GPT-5.4-nano comply at 57 to 99 percent. Claude refused eleven of twelve pretexts, but agreed 23 percent of the time when the operator pre-approved the redaction.");

// 6. Fix
s = pres.addSlide({ masterName: "Content", sectionTitle: "Results" });
s.addText("Built-in redundancy makes cover-ups visible", { placeholder: "title" });
s.addChart(pres.charts.BAR, [{ name: "Coordinated cover-ups caught (peers only)", labels: ["No extra copies", "Copy to 1 peer", "Copy to all peers", "1 peer + receipts", "2 peers + receipts"], values: [42, 67, 67, 97, 99.6] }],
  chartBase({ x: 0.4, y: 1.15, w: 5.8, h: 4.0, barDir: "col", chartColors: [H.accent6, H.accent4, H.accent4, H.accent1, H.accent1],
    valAxisMinVal: 0, valAxisMaxVal: 100, valAxisMajorUnit: 25, dataLabelFormatCode: "General", showLegend: false,
    showTitle: true, title: "% of coordinated cover-ups caught, no trusted log", titleFontSize: 12, titleColor: H.dk2, titleFontFace: "+mn-lt", objectName: "redundancy chart" }));
card(s, 6.5, 1.25, 3.0, 1.15, "61%", "of frontier (Gemini) cover-ups caught, vs 98–100% for 7B forgers", "frontier");
card(s, 6.5, 2.6, 3.0, 1.15, "5.4%", "natural echo coverage in a real agent wiki log", "real");
card(s, 6.5, 3.95, 3.0, 1.15, "1.5× storage", "for 97% detection, with zero false alarms", "cost");
s.addNotes("The catch: sloppy 7B forgers get caught almost every time, but a Gemini forger is caught only 61 percent of the time, and in a real agent wiki only about five percent of posts are naturally echoed. So redundancy has to be designed in. Copy each message to one random extra peer and send receipts for outside calls, and detection rises from 42 to 97 percent at one and a half times the storage, with no false alarms.");

// 7. Takeaways
pres.addSection({ title: "Close" });
s = pres.addSlide({ masterName: "Dark content", sectionTitle: "Close" });
s.addText("Design for witnesses", { placeholder: "title" });
s.addText([
  { text: "Keep verbatim copies on both sides, not summaries", options: { bullet: true, breakLine: true } },
  { text: "Copy each message to one random peer, plus receipts", options: { bullet: true, breakLine: true } },
  { text: "Keep a trusted log of outside calls", options: { bullet: true, breakLine: true } },
  { text: "Log every redaction with a hash of what was removed", options: { bullet: true, breakLine: true } },
  { text: " ", options: { breakLine: true, fontSize: 12 } },
  { text: "github.com/ShreySharma07/witness-network", options: { color: C.accent1, fontSize: 14 } },
], { placeholder: "body", paraSpaceAfter: 6 });
s.addNotes("So, four design rules. Keep verbatim copies of messages, not summaries. Copy each message to one random peer and send receipts for outside calls. Keep a trusted log of outside calls. And whenever a record is redacted, log a hash of what was removed. The code and results are on GitHub. Thanks for watching.");

pres.writeFile({ fileName: OUT }).then(async () => { await applyTheme(OUT, THEME); console.log("wrote", OUT); });
