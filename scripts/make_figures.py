"""Paper figures (revised after review). Thresholds are set on the SAME episodes' attack-only controls.

Fig 1  tamper detection (TPR @ 5% FPR) vs colluder fraction; left = coordinated scrub, right = LLM cover-ups.
       Dashed = consistency bound for B2: share of positives with a non-coalition witness of a touched record.
Fig 2  B2 (no tool log) detection vs tamper coverage, per topology.
Fig 3  witness corruption: compliance, and detection with vs without corruption.
Fig 4  real data: share of scrubbed posts still witnessed vs coalition size (collusion.wiki).
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
from analyze import load, threshold_tpr  # noqa: E402

SERIES = {"B0": ("#2a78d6", "o", "B0 single-log"), "B1": ("#eb6834", "s", "B1 all-logs"),
          "B2": ("#1baf7a", "^", "B2 exact match"), "B3": ("#eda100", "D", "B3 cross-witness (ours)"),
          "X": ("#e87ba4", "v", "")}
INK, MUTED, GRID, THEORY = "#0b0b0b", "#52514e", "#e6e5e0", "#8a8983"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "figure.dpi": 200})
FPR = 0.05


def _label(ax, x, y, t):
    ax.__dict__.setdefault("_wn", []).append([x, y, t])


def _flush(ax, gap=0.07):
    labs = sorted(ax.__dict__.pop("_wn", []), key=lambda l: l[1])
    for i in range(1, len(labs)):
        if labs[i][1] - labs[i - 1][1] < gap:
            labs[i][1] = labs[i - 1][1] + gap
    for x, y, t in labs:
        ax.annotate(t, (x, y), xytext=(5, 0), textcoords="offset points", fontsize=7, color=INK, va="center",
                    annotation_clip=False)


def thr(ctrl, aud):
    ns = [r[aud]["score"] for r in ctrl if aud in r]
    if not ns:
        return None
    for t in sorted(set(ns)) + [max(ns) + 1e-9]:
        if sum(n > t for n in ns) / len(ns) <= FPR:
            return t


def fig1(rows, n, path):
    ctrl = [r for r in rows if r["condition"] == "ctrl-attack-untampered"]
    panels = [("Coordinated forger (scripted scrub)", {"scripted-PARA"}),
              ("LLM cover-ups (naive + adaptive)", {"organic-naive", "organic-adaptive"})]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0), sharey=True)
    for ax, (title, conds) in zip(axes, panels):
        pos = [r for r in rows if r["condition"] in conds and r["n_record"] > 0]
        ks = sorted({r["k"] for r in pos})
        bound = [sum(r.get("detectable") is True for r in pos if r["k"] == k) / max(1, sum(r["k"] == k for r in pos))
                 for k in ks]
        bound = [b + (1 - b) * FPR for b in bound]
        ax.plot([k / n for k in ks], bound, ls="--", color=THEORY, lw=1.5, zorder=1)
        if ks:
            _label(ax, ks[-1] / n, bound[-1], "B2 bound")
        for aud in ["B0", "B1", "B2", "B3"]:
            t = thr(ctrl, aud)
            if t is None:
                continue
            xs, ys = [], []
            for k in ks:
                g = [r for r in pos if r["k"] == k and aud in r]
                if g:
                    xs.append(k / n)
                    ys.append(sum(r[aud]["score"] > t for r in g) / len(g))
            col, mk, lab = SERIES[aud]
            ax.plot(xs, ys, color=col, marker=mk, ms=5, lw=2, label=lab, zorder=3, markeredgecolor="#fcfcfb")
            if xs:
                _label(ax, xs[-1], ys[-1], aud)
        _flush(ax)
        ax.set_title(title, fontsize=9, color=INK, loc="left")
        ax.set_xlabel("colluder fraction k/N")
        ax.set_ylim(-0.03, 1.08)
    axes[0].set_ylabel(f"tamper detection (TPR @ {int(FPR*100)}% FPR)")
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=4, frameon=False, fontsize=7, bbox_to_anchor=(0.5, -0.04))
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def fig2(rows, path):
    ctrl = [r for r in rows if r["condition"] == "ctrl-attack-untampered"]
    pos = [r for r in rows if r["k"] > 0 and r["n_record"] > 0 and not r["condition"].startswith("ctrl")
           and r.get("tcov_notool") == r.get("tcov_notool") and r.get("tcov_notool") is not None]
    bins = [(-0.01, 0.0, "0"), (0.0, 0.34, "(0, 1/3]"), (0.34, 0.67, "(1/3, 2/3]"), (0.67, 1.0, "(2/3, 1]")]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8), sharey=True)
    for ax, (title, conds) in zip(axes, [("scripted (coordinated)", lambda c: c.startswith("scripted")),
                                          ("LLM-organic", lambda c: c.startswith("organic"))]):
        t = thr(ctrl, "B2-notool")
        for ti, topo in enumerate(sorted({r["topology"] for r in rows})):
            xs, ys = [], []
            for bi, (lo, hi, _) in enumerate(bins):
                g = [r for r in pos if conds(r["condition"]) and r["topology"] == topo and lo < r["tcov_notool"] <= hi]
                if len(g) >= 3:
                    xs.append(bi)
                    ys.append(sum(r["B2-notool"]["score"] > t for r in g) / len(g))
            col, mk, _ = list(SERIES.values())[ti]
            ax.plot(xs, ys, color=col, marker=mk, ms=5, lw=2, label=topo, markeredgecolor="#fcfcfb")
            if xs:
                _label(ax, xs[-1], ys[-1], topo)
        _flush(ax)
        ax.set_xticks(range(len(bins)), [b[2] for b in bins], fontsize=7)
        ax.set_xlabel("share of touched records with an honest witness")
        ax.set_title(f"B2 without tool log: {title}", fontsize=9, color=INK, loc="left")
        ax.set_ylim(-0.03, 1.08)
    axes[0].set_ylabel(f"detection (TPR @ {int(FPR*100)}% FPR)")
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=4, frameon=False, fontsize=7, bbox_to_anchor=(0.5, -0.05))
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def fig3(rows, coverups, path):
    reqs = [q for b in coverups for q in b.get("requests", []) if "comply" in q]
    if not reqs:
        print("fig3 skipped: no corruption requests")
        return
    rate = sum(q["comply"] for q in reqs) / len(reqs)
    ctrl = [r for r in rows if r["condition"] == "ctrl-attack-untampered"]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.6), gridspec_kw={"width_ratios": [1, 2.2]})
    ax = axes[0]
    ax.bar([0], [rate], color=SERIES["X"][0], width=0.5)
    ax.set_xticks([0], ["honest witnesses\nasked to 'correct'"], fontsize=7)
    ax.set_ylim(0, 1)
    ax.set_ylabel("compliance rate")
    ax.annotate(f"{rate:.0%} (n={len(reqs)})", (0, rate), xytext=(0, 3), textcoords="offset points", ha="center",
                fontsize=8, color=INK)
    ax = axes[1]
    auds = ["B2-notool", "B3-notool", "B2", "B3"]
    corrupted_ids = {(b["episode_id"]) for b in coverups if any(q.get("comply") is not None for q in b.get("requests", []))}
    w = 0.38
    for j, (cond, lab, col) in enumerate([("organic-adaptive", "adaptive, no corruption", SERIES["B3"][0]),
                                          ("organic-corrupt", "adaptive + corruption", SERIES["X"][0])]):
        vals = []
        for aud in auds:
            t = thr(ctrl, aud)
            g = [r for r in rows if r["condition"] == cond and aud in r and r["episode_id"] in corrupted_ids]
            vals.append(sum(r[aud]["score"] > t for r in g) / len(g) if g and t is not None else float("nan"))
        ax.bar([i + (j - 0.5) * w for i in range(len(auds))], vals, width=w - 0.04, color=col, label=lab)
    ax.set_xticks(range(len(auds)), [a.replace("-notool", "\n(no tool log)") for a in auds], fontsize=7)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel(f"tamper detection (TPR @ {int(FPR*100)}% FPR)")
    ax.set_title(f"episodes where corruption was attempted (n={len(corrupted_ids)})", fontsize=9, color=INK,
                 loc="left")
    ax.legend(frameon=False, fontsize=7)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def fig4(real_path, path):
    if not os.path.exists(real_path):
        return
    res = json.load(open(real_path))
    fig, ax = plt.subplots(figsize=(3.6, 2.6))
    for key, (col, mk, lab) in [("curve_weighted", (SERIES["B0"][0], "o", "activity-weighted coalition")),
                                ("curve_uniform", (SERIES["B1"][0], "s", "uniform coalition"))]:
        c = res[key]
        xs = [p["frac"] * 100 for p in c]
        ys = [p["witnessed"] * 100 for p in c]
        ax.plot(xs, ys, color=col, marker=mk, ms=5, lw=2, label=lab, markeredgecolor="#fcfcfb")
        ax.fill_between(xs, [p["spread_lo"] * 100 for p in c], [p["spread_hi"] * 100 for p in c], color=col,
                        alpha=0.12, lw=0)
    ax.set_xscale("log")
    ax.set_xlabel("coalition size (% of identities, log)")
    ax.set_ylabel("scrubbed posts still witnessed (%)")
    ax.set_ylim(0, max(10, ax.get_ylim()[1]))
    ax.set_title("collusion.wiki: cross-page echoes", fontsize=9, color=INK, loc="left")
    ax.legend(frameon=False, fontsize=7)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--figs", default="report/figs")
    p.add_argument("--real", default="results/realdata/collusion_wiki_coverage.json")
    a = p.parse_args()
    os.makedirs(a.figs, exist_ok=True)
    eps, rows = load(a.out)
    n = next(iter(eps.values())).config.n_agents
    fig1(rows, n, os.path.join(a.figs, "fig1_tamper_detection.png"))
    fig2(rows, os.path.join(a.figs, "fig2_coverage.png"))
    cov = os.path.join(a.out, "coverups.jsonl")
    coverups = [json.loads(l) for l in open(cov)] if os.path.exists(cov) else []
    fig3(rows, coverups, os.path.join(a.figs, "fig3_witness_corruption.png"))
    fig4(a.real, os.path.join(a.figs, "fig4_realdata.png"))
    print("figures written to", a.figs)


if __name__ == "__main__":
    main()
