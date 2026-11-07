"""Paper figures from pipeline outputs.

Fig 1  detection (TPR @ 5% FPR) vs colluder fraction, per auditor, two panels (competent scrub | LLM cover-up),
       dashed = witness-coverage upper bound (share of positives with >=1 honest witness of a covert event).
Fig 2  detection vs honest PEER coverage (no tool log): do all topologies collapse onto one curve?
Fig 3  witness corruption: compliance rate and detection with vs without corruption.
Usage: python scripts/make_figures.py --out <pipeline out dir> --figs report/figs
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from analyze import load  # noqa: E402
from wn.eval.metrics import tpr_at_fpr  # noqa: E402

# validated categorical slots 1-5 (fixed order) + neutral for theory; text never wears series colour
SERIES = {"B0": ("#2a78d6", "o", "B0 single-log"), "B1": ("#eb6834", "s", "B1 all-logs"),
          "B2": ("#1baf7a", "^", "B2 exact match"), "B3": ("#eda100", "D", "B3 cross-witness (ours)"),
          "B3-corrupt": ("#e87ba4", "v", "B3 under witness corruption")}
INK, MUTED, GRID, THEORY = "#0b0b0b", "#52514e", "#e6e5e0", "#8a8983"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "figure.dpi": 150})
FPR = 0.05


def neg_scores(rows, aud):
    return [r[aud]["score"] for r in rows if r["condition"].startswith("neg") and aud in r]


def is_pos(r, conds):
    return r["condition"] in conds and r["n_record"] > 0


def tpr_by(rows, conds, aud, key):
    ns = neg_scores(rows, aud)
    out = {}
    groups = defaultdict(list)
    for r in rows:
        if is_pos(r, conds) and aud in r:
            groups[r[key]].append(r[aud]["score"])
    for k, ps in sorted(groups.items()):
        out[k] = (tpr_at_fpr(ps, ns, FPR), len(ps))
    return out


def theory_by_k(rows, conds, cov_key="coverage"):
    g = defaultdict(list)
    for r in rows:
        if is_pos(r, conds):
            c = r[cov_key]
            g[r["k"]].append(1.0 if (c == c and c > 0) else 0.0)
    return {k: sum(v) / len(v) for k, v in sorted(g.items())}


def _label_end(ax, xs, ys, text, color):
    """Queue an end-of-line label; _flush_labels spreads them so none collide."""
    if xs:
        ax.__dict__.setdefault("_wn_labels", []).append([xs[-1], ys[-1], text])


def _flush_labels(ax, min_gap=0.07):
    labs = sorted(ax.__dict__.pop("_wn_labels", []), key=lambda l: l[1])
    for i in range(1, len(labs)):
        if labs[i][1] - labs[i - 1][1] < min_gap:
            labs[i][1] = labs[i - 1][1] + min_gap
    for x, y, t in labs:
        ax.annotate(t, (x, y), xytext=(5, 0), textcoords="offset points", fontsize=7, color=INK, va="center",
                    annotation_clip=False)


def fig1(rows, n_agents, path):
    panels = [("Competent forger (journal scrub)", {"scripted-PARA"}),
              ("LLM cover-up (naive + adaptive)", {"organic-naive", "organic-adaptive"})]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0), sharey=True)
    for ax, (title, conds) in zip(axes, panels):
        th = theory_by_k(rows, conds)
        ax.plot([k / n_agents for k in th], list(th.values()), ls="--", color=THEORY, lw=1.5, zorder=1)
        if th:
            _label_end(ax, [list(th)[-1] / n_agents], [list(th.values())[-1]], "coverage bound", THEORY)
        for aud in ["B0", "B1", "B2", "B3"]:
            d = tpr_by(rows, conds, aud, "k")
            if not d:
                continue
            xs = [k / n_agents for k in d]
            ys = [v[0] for v in d.values()]
            col, mk, lab = SERIES[aud]
            ax.plot(xs, ys, color=col, marker=mk, ms=5, lw=2, label=lab, zorder=3,
                    markeredgecolor="#fcfcfb", markeredgewidth=1)
            _label_end(ax, xs, ys, aud, col)
        _flush_labels(ax)
        ax.set_title(title, fontsize=9, color=INK, loc="left")
        ax.set_xlabel("colluder fraction k/N")
        ax.set_ylim(-0.03, 1.05)
    axes[0].set_ylabel(f"detection rate (TPR @ {int(FPR*100)}% FPR)")
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=4, frameon=False, fontsize=7, bbox_to_anchor=(0.5, -0.04))
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def fig2(rows, path):
    conds = {"scripted-PARA", "organic-naive", "organic-adaptive"}
    bins = [(-0.01, 0.0, "0"), (0.0, 0.5, "(0, .5]"), (0.5, 1.0, "(.5, 1]")]
    topos = sorted({r["topology"] for r in rows})
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8), sharey=True)
    for ax, aud in zip(axes, ["B2-notool", "B3-notool"]):
        ns = neg_scores(rows, aud)
        for ti, t in enumerate(topos):
            xs, ys = [], []
            for bi, (lo, hi, _) in enumerate(bins):
                ps = [r[aud]["score"] for r in rows if is_pos(r, conds) and aud in r and r["topology"] == t
                      and r["coverage_notool"] == r["coverage_notool"] and lo < r["coverage_notool"] <= hi]
                if len(ps) >= 3:
                    xs.append(bi)
                    ys.append(tpr_at_fpr(ps, ns, FPR))
            col = list(SERIES.values())[ti][0]
            mk = list(SERIES.values())[ti][1]
            ax.plot(xs, ys, color=col, marker=mk, ms=5, lw=2, label=t, markeredgecolor="#fcfcfb")
            _label_end(ax, xs, ys, t, col)
        _flush_labels(ax)
        ax.set_xticks(range(len(bins)), [b[2] for b in bins])
        ax.set_xlabel("honest peer coverage of covert events")
        ax.set_title(f"{aud.replace('-notool', '')} without tool log", fontsize=9, color=INK, loc="left")
        ax.set_ylim(-0.03, 1.05)
    axes[0].set_ylabel(f"detection (TPR @ {int(FPR*100)}% FPR)")
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=4, frameon=False, fontsize=7, bbox_to_anchor=(0.5, -0.04))
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def fig3(rows, coverups, path):
    reqs = [q for b in coverups for q in b.get("requests", []) if "comply" in q]
    rate = sum(q["comply"] for q in reqs) / len(reqs) if reqs else float("nan")
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.6), gridspec_kw={"width_ratios": [1, 2]})
    ax = axes[0]
    ax.bar([0], [rate], color=SERIES["B3-corrupt"][0], width=0.5)
    ax.set_xticks([0], ["honest witnesses\nasked to 'correct'"])
    ax.set_ylim(0, 1)
    ax.set_ylabel("compliance rate")
    ax.annotate(f"{rate:.0%} (n={len(reqs)})", (0, rate), xytext=(0, 3), textcoords="offset points", ha="center",
                fontsize=8, color=INK)
    ax = axes[1]
    auds = ["B2-notool", "B3-notool", "B2", "B3"]
    w = 0.38
    for j, (cond, lab, col) in enumerate([("organic-adaptive", "no corruption", SERIES["B3"][0]),
                                          ("organic-corrupt", "with corruption", SERIES["B3-corrupt"][0])]):
        vals = []
        for aud in auds:
            ns = neg_scores(rows, aud)
            ps = [r[aud]["score"] for r in rows if is_pos(r, {cond}) and aud in r and r["coverage_notool"] > 0]
            vals.append(tpr_at_fpr(ps, ns, FPR) if ps else float("nan"))
        xs = [i + (j - 0.5) * w for i in range(len(auds))]
        ax.bar(xs, vals, width=w - 0.04, color=col, label=lab)
    ax.set_xticks(range(len(auds)), [a.replace("-notool", "\n(no tool log)") for a in auds], fontsize=7)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel(f"detection (TPR @ {int(FPR*100)}% FPR)")
    ax.set_title("episodes with >=1 honest peer witness", fontsize=9, color=INK, loc="left")
    ax.legend(frameon=False, fontsize=7)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--figs", default="report/figs")
    a = p.parse_args()
    os.makedirs(a.figs, exist_ok=True)
    eps, rows = load(a.out)
    n = next(iter(eps.values())).config.n_agents
    fig1(rows, n, os.path.join(a.figs, "fig1_detection_vs_colluders.png"))
    fig2(rows, os.path.join(a.figs, "fig2_coverage_collapse.png"))
    cov = os.path.join(a.out, "coverups.jsonl")
    coverups = [json.loads(l) for l in open(cov)] if os.path.exists(cov) else []
    fig3(rows, coverups, os.path.join(a.figs, "fig3_witness_corruption.png"))
    print("figures written to", a.figs)


if __name__ == "__main__":
    main()
