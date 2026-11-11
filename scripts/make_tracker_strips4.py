# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""Four 'you are here' strips (step 1..4 lit) for the corner of each card, matching the 4-step system overview.
Colours follow the user's own System Overview panel: 1 pink-red, 2 peach, 3 green, 4 blue.
  python3 scripts/make_tracker_strips4.py research/figures_v3/trackers4
"""
import sys, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch
for fam in ("TH Sarabun New", "Thonburi"):
    if any(f.name == fam for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = fam; break
COL = ["#E57A7A", "#F0A34A", "#5DBB5D", "#5B7FE0"]
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
for lit in range(4):
    fig = plt.figure(figsize=(2.8, 0.7), dpi=300); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 2.8); ax.set_ylim(0, 0.7); ax.axis("off")
    for i in range(4):
        on = (i == lit)
        ax.add_patch(FancyBboxPatch((0.04 + i * 0.69, 0.08), 0.62, 0.54, boxstyle="round,pad=0,rounding_size=0.08",
                                    fc=COL[i] if on else "#E6E8EC", ec=COL[i] if on else "#E6E8EC", lw=1))
        ax.text(0.35 + i * 0.69, 0.35, str(i + 1), ha="center", va="center", fontsize=16, color="white" if on else "#A7ADB8", fontweight="bold")
    fig.savefig(os.path.join(out, f"tracker4_{lit + 1}.png"), transparent=True); plt.close(fig)
print("saved 4 strips in", out)
