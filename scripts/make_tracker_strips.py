# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""Five 'you are here' strips (stage 1..5 lit) for the corner of each method card. Transparent PNG.
Stage colours are eyeballed from the poster's pipeline; replace them in Canva if you pick exact ones.
  python3 scripts/make_tracker_strips.py research/figures_v3/trackers
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
COL = ["#F0953A", "#59C23C", "#4B82E8", "#8E5CE6", "#E86BB5"]
NAME = ["เก็บข้อมูล", "เตรียมข้อมูล", "วิธีที่ทดลอง", "แบ่งและฝึก", "ประเมิน"]
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
for lit in range(5):
    fig = plt.figure(figsize=(3.4, 0.7), dpi=300); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 3.4); ax.set_ylim(0, 0.7); ax.axis("off")
    for i in range(5):
        on = (i == lit)
        ax.add_patch(FancyBboxPatch((0.04 + i * 0.67, 0.08), 0.6, 0.54, boxstyle="round,pad=0,rounding_size=0.08",
                                    fc=COL[i] if on else "#E6E8EC", ec=COL[i] if on else "#E6E8EC", lw=1))
        ax.text(0.34 + i * 0.67, 0.35, str(i + 1), ha="center", va="center", fontsize=16, color="white" if on else "#A7ADB8", fontweight="bold")
    fig.savefig(os.path.join(out, f"tracker_{lit + 1}.png"), transparent=True); plt.close(fig)
print("saved 5 strips in", out)
