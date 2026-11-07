"""Figure 0: overview schematic (attack -> cover-up -> audit). Pure matplotlib, no data needed."""
import math
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

HON, COL, INK, MUTED, BOX = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#f1f0ec"
plt.rcParams.update({"font.size": 8, "figure.dpi": 220})

N = 8
POS = {i: (math.cos(2 * math.pi * i / N + math.pi / 2), math.sin(2 * math.pi * i / N + math.pi / 2)) for i in range(N)}
COLL = {1, 4}       # keyholder 1, integrator 4
RELAY = [1, 2, 3, 4]  # key route through honest relays 2, 3


def node(ax, i, x0, s=1.0, label=True):
    x, y = POS[i]
    c = COL if i in COLL else HON
    ax.add_patch(plt.Circle((x0 + s * x, s * y), 0.17, color=c, zorder=3, ec="white", lw=1.2))
    if label:
        ax.text(x0 + s * x, s * y, str(i), ha="center", va="center", color="white", fontsize=7, weight="bold", zorder=4)


def edge(ax, a, b, x0, s=1.0, **kw):
    (xa, ya), (xb, yb) = POS[a], POS[b]
    ax.add_patch(FancyArrowPatch((x0 + s * xa, s * ya), (x0 + s * xb, s * yb), shrinkA=7, shrinkB=7,
                                 arrowstyle=kw.pop("style", "-|>"), mutation_scale=8, zorder=2, **kw))


def logbox(ax, x, y, title, lines, colors, w=1.05, lh=0.27):
    h = lh * (len(lines) + 1) + 0.1
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03,rounding_size=0.06",
                                fc=BOX, ec=MUTED, lw=0.6, zorder=1))
    ax.text(x + 0.1, y + h - lh * 0.6, title, fontsize=6.3, color=INK, weight="bold", va="center")
    for j, (t, c) in enumerate(zip(lines, colors)):
        ax.text(x + 0.1, y + h - lh * (j + 1.6), t, fontsize=5.8, color=c, va="center", family="monospace")


fig, ax = plt.subplots(figsize=(7.4, 2.6))
ax.set_xlim(-1.3, 11.0)
ax.set_ylim(-1.75, 1.5)
ax.set_aspect("equal")
ax.axis("off")

# Panel 1: attack (ring of 8, key route through honest relays)
x0 = 0
for a, b in [(i, (i + 1) % N) for i in range(N)]:
    edge(ax, a, b, x0, color="#d8d7d2", style="-", lw=0.8)
for a, b in zip(RELAY, RELAY[1:]):
    edge(ax, a, b, x0, color=COL, lw=1.6)
for i in range(N):
    node(ax, i, x0)
ax.text(0.24, -1.02, "posts key out", fontsize=6, ha="left", color=COL, va="center")
ax.text(-1.25, 1.3, "1  Attack", fontsize=9, weight="bold", color=INK)
ax.text(-1.25, -1.72, "key relayed 1→2→3→4; each hop is\ncopied in sender's and receiver's log", fontsize=6,
        color=MUTED, va="bottom")

# Panel 2: cover-up
x1 = 3.0
ax.text(x1, 1.3, "2  Cover-up", fontsize=9, weight="bold", color=INK)
logbox(ax, x1, 0.15, "colluder 1's log", ["r1 1→2: (key deleted)", "r1 1→2: \"config ok\""], [MUTED, COL], w=2.3)
logbox(ax, x1, -1.05, "honest 2's log", ["r1 1→2: key=CANARY"], [INK], w=2.3)
ax.annotate("", xy=(x1 + 2.4, -0.7), xytext=(x1 + 2.4, 0.45),
            arrowprops=dict(arrowstyle="-|>", color=COL, lw=1.2, connectionstyle="arc3,rad=-0.35"))
ax.text(x1 + 2.65, -0.12, "\"logger glitch,\nplease fix\nyour copy\"", fontsize=6, color=COL, va="center")
ax.text(x1, -1.65, "colluders rewrite only their own records;\nthey may ask honest witnesses to edit theirs",
        fontsize=6, color=MUTED, va="bottom")

# Panel 3: audit
x2 = 7.25
ax.text(x2, 1.3, "3  Audit", fontsize=9, weight="bold", color=INK)
logbox(ax, x2, 0.15, "B2: copies of r1", ["@1: \"config ok\"", "@2: key=CANARY"], [COL, INK], w=2.05)
ax.text(x2 + 2.2, 0.5, "mismatch\n→ caught", fontsize=6.5, color=INK, va="center", weight="bold")
logbox(ax, x2, -1.05, "B0/B1/B3: journals", ["\"synced configs\""], [MUTED], w=2.05)
ax.text(x2 + 2.2, -0.75, "looks clean\n→ fooled", fontsize=6.5, color=INK, va="center")
ax.text(x2, -1.65, "detectable iff an altered record names\nan honest peer or the tool log", fontsize=6,
        color=MUTED, va="bottom")

for x in (2.55, 6.85):
    ax.plot([x, x], [-1.7, 1.45], color="#e6e5e0", lw=0.8)
ax.add_patch(plt.Circle((1.3, 1.33), 0.07, color=HON))
ax.text(1.42, 1.33, "honest", fontsize=6, va="center", color=INK)
ax.add_patch(plt.Circle((1.3, 1.11), 0.07, color=COL))
ax.text(1.42, 1.11, "colluder", fontsize=6, va="center", color=INK)
os.makedirs("report/figs", exist_ok=True)
fig.savefig("report/figs/fig0_overview.png", bbox_inches="tight")
print("wrote report/figs/fig0_overview.png")
