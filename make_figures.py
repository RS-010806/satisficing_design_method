"""
Draws Figs. 1 to 3 of the manuscript at their printed size and saves them in figures/.

  Fig. 1  Functional model of the method in IDEF0 notation
  Fig. 2  Screening logic of Step 2
  Fig. 3  Chain from the published inputs to the measures of each allocation in the example

Usage:  python make_figures.py      (needs matplotlib; see requirements.txt)
"""
import os
# We draw each figure at its printed size (data units = inches), so that font sizes in points print as stated.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon
plt.rcParams['font.family'] = 'DejaVu Sans'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figures')
os.makedirs(OUT, exist_ok=True)
K = 'black'
FS = 7.2      # labels
FB = 7.8      # box text

def canvas(w, h):
    fig = plt.figure(figsize=(w, h))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, w); ax.set_ylim(0, h); ax.axis('off')
    return fig, ax

def box(ax, x, y, w, h, text, fs=FB, bold=False, rounded=False, lw=0.9):
    p = (FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=0.08', fc='white', ec=K, lw=lw) if rounded
         else Rectangle((x, y), w, h, fc='white', ec=K, lw=lw))
    ax.add_patch(p)
    ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=fs, fontweight='bold' if bold else 'normal',
            linespacing=1.15)

def arrow(ax, x1, y1, x2, y2, lw=0.9):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='-|>', color=K, lw=lw, shrinkA=0, shrinkB=0, mutation_scale=8))

def line(ax, xs, ys, lw=0.9):
    ax.plot(xs, ys, color=K, lw=lw, solid_capstyle='butt')

def txt(ax, x, y, s, ha='center', va='center', fs=FS, **kw):
    ax.text(x, y, s, ha=ha, va=va, fontsize=fs, linespacing=1.12, **kw)

# ---------------- Figure 1: functional model in IDEF0 notation (6.3 in x 3.05 in) ----------------
fig, ax = canvas(6.3, 3.23); ax.set_ylim(-0.08, 3.15)
BY, BH = 0.60, 1.00                       # box bottom and height
boxes = [(0.98, 1.05, 'A1\nTranslate and\ncheck the inputs'),
         (2.78, 1.12, 'A2\nScreen every\ncandidate at the\ncentral value and\nat the adverse end'),
         (4.50, 0.90, 'A3\nRecord each\ndecision')]
for x, w, t in boxes:
    box(ax, x, BY, w, BH, t)
# inputs to A1
for yy, t in [(1.42, 'Published\nforecasts with\nstated ranges'), (1.08, 'Stakeholder\nrequirements'), (0.76, 'Candidate\nconfigurations')]:
    txt(ax, 0.0, yy, t, ha='left')
    arrow(ax, 0.78, yy, 0.98, yy)
# A1 -> A2, A2 -> A3
ym = BY + BH/2
arrow(ax, 2.03, ym, 2.78, ym); txt(ax, 2.405, ym + 0.05, 'Measures at\nthe central\nand adverse\nvalues', va='bottom')
arrow(ax, 3.90, ym, 4.50, ym); txt(ax, 4.20, ym + 0.05, 'Accepted,\nflagged or\nrejected', va='bottom')
# outputs of A3
arrow(ax, 5.40, 1.34, 6.28, 1.34); txt(ax, 5.45, 1.38, 'Decision\nrecord', ha='left', va='bottom')
arrow(ax, 5.40, 0.86, 6.28, 0.86); txt(ax, 5.45, 0.82, 'Verdict for each\ncandidate', ha='left', va='top')
# controls (top)
TOP = BY + BH
ctrl = [(1.70, 'Translation\nrelations and\ntheir sources'),
        (3.34, 'Thresholds with\npriority tags;\nadverse-end rule;\nfallback rules\nagreed in advance'),
        (4.95, 'Content that\nothers need to\nrecompute each\nverdict')]
for xc, t in ctrl:
    arrow(ax, xc, TOP + 0.30, xc, TOP)
    txt(ax, xc, TOP + 0.33, t, va='bottom')
# mechanisms (bottom)
mech = [(1.505, 'Designer;\nspreadsheet\nor script'), (3.34, 'Designer;\nspreadsheet\nor script'), (4.95, 'Designer;\nstakeholders\nwho approve')]
for xc, t in mech:
    arrow(ax, xc, BY - 0.25, xc, BY)
    txt(ax, xc, BY - 0.28, t, va='top')
# feedback: from the decision record, over the top, into A1 as a control
FY = 2.74
line(ax, [6.12, 6.12], [1.34, FY]); line(ax, [6.12, 1.22], [FY, FY]); arrow(ax, 1.22, FY, 1.22, TOP)
txt(ax, 3.67, FY + 0.05, 'Feedback: with realized values and updated forecasts, the designer revises\ntranslations, thresholds and fallback rules', va='bottom')
fig.savefig(os.path.join(OUT, 'fig1_functional_model.png'), dpi=300); plt.close(fig)

# ---------------- Figure 2: screening logic of Step 2 (5.6 in x 7.15 in) ----------------
fig, ax = canvas(5.6, 7.15)
CX, DW = 1.85, 2.9
RX, RW = 3.78, 1.8
def diamond(cy, h, text):
    ax.add_patch(Polygon([(CX, cy + h/2), (CX + DW/2, cy), (CX, cy - h/2), (CX - DW/2, cy)], closed=True, fc='white', ec=K, lw=0.9))
    txt(ax, CX, cy, text, fs=FB)
box(ax, CX - 1.25, 6.78, 2.5, 0.32, 'For each candidate configuration', rounded=True)
arrow(ax, CX, 6.78, CX, 6.56)
box(ax, CX - 1.45, 6.06, 2.9, 0.50, 'Compute every requirement measure\nat the central value of each forecast')
arrow(ax, CX, 6.06, CX, 5.86)
d1 = 5.42; diamond(d1, 0.88, 'Are all critical\nrequirements met?')
arrow(ax, CX + DW/2, d1, RX, d1); txt(ax, CX + DW/2 + 0.05, d1 + 0.04, 'No', ha='left', va='bottom')
box(ax, RX, d1 - 0.27, RW, 0.54, 'Rejected at the central\nvalue; record the reason')
arrow(ax, CX, d1 - 0.44, CX, 4.70); txt(ax, CX + 0.06, d1 - 0.56, 'Yes', ha='left')
box(ax, CX - 1.45, 4.06, 2.9, 0.64, 'Compute every measure again at the\nadverse end of each forecast range (the\nend at which the designer finds the\nrequirement harder to meet)', fs=7.4)
arrow(ax, CX, 4.06, CX, 3.86)
d2 = 3.40; diamond(d2, 0.92, 'Are all critical and\nimportant requirements\nmet at the adverse end?')
arrow(ax, CX + DW/2, d2, RX, d2); txt(ax, CX + DW/2 + 0.05, d2 + 0.04, 'Yes', ha='left', va='bottom')
box(ax, RX, d2 - 0.22, RW, 0.44, 'Accepted', bold=True)
arrow(ax, CX, d2 - 0.46, CX, 2.70); txt(ax, CX + 0.06, d2 - 0.58, 'No', ha='left')
d3 = 2.18; diamond(d3, 1.04, 'Can the designer restore them\nwith a fallback rule agreed in\nadvance, within the budget?')
arrow(ax, CX + DW/2, d3, RX, d3); txt(ax, CX + DW/2 + 0.05, d3 + 0.04, 'Yes', ha='left', va='bottom')
box(ax, RX, d3 - 0.27, RW, 0.54, 'Accepted, with the\nfallback rule recorded', bold=True)
arrow(ax, CX, d3 - 0.52, CX, 1.42); txt(ax, CX + 0.06, d3 - 0.64, 'No', ha='left')
d4 = 0.98; diamond(d4, 0.88, 'Are all critical requirements\nmet at the adverse end?')
arrow(ax, CX + DW/2, d4, RX, d4); txt(ax, CX + DW/2 + 0.05, d4 + 0.04, 'Yes', ha='left', va='bottom')
box(ax, RX, d4 - 0.33, RW, 0.66, 'Flagged; record the\nshortfall and the cost\nof removing it')
arrow(ax, CX, d4 - 0.44, CX, 0.34); txt(ax, CX + 0.06, d4 - 0.56, 'No', ha='left')
box(ax, CX - 1.15, 0.04, 2.3, 0.30, 'Rejected; record the reason')
fig.savefig(os.path.join(OUT, 'fig2_screening_logic.png'), dpi=300); plt.close(fig)

# ---------------- Figure 3: chain from published inputs to the measures (6.3 in x 3.2 in) ----------------
F3 = 6.9
fig, ax = canvas(6.36, 3.44)
BW, BHh = 1.2, 0.80
c1, c2, c3, c4, c5 = 0.03, 1.40, 2.80, 4.20, 5.60
top, mid, bot = 2.50, 1.30, 0.06
box(ax, c1, top, BW, BHh, 'United Nations\n(2024): U.S.\npopulation, 347.28\nmillion (2025) and\n355.65 million (2030)', fs=F3)
box(ax, c1, bot, BW, BHh, 'U.S. Census Bureau\n(2026): town\npopulations, April\n2020 and July 2025', fs=F3)
box(ax, c2, mid, BW, BHh, '2030 population of\neach town: central\nvalue (national\ngrowth) and local-\ntrend value', fs=F3)
box(ax, c3, top, BW, BHh, 'Santo and Kang\n(2023): 1.614 primary-\ncare visits per person\nper year (95% range\n1.428 to 1.800)', fs=F3)
box(ax, c3, bot, BW, BHh, 'Planning assumption:\nstakeholders assign\n15 percent of primary-\ncare visits to the\nmobile clinics', fs=F3)
box(ax, c4, mid, BW, BHh, 'Monthly visits that\nthe residents of each\ntown need from the\nmobile clinics, central\nand adverse', fs=F3)
box(ax, c4, top + 0.08, BW, BHh, 'Planning assumptions\nbased on Malone et al.\n(2020): 291 visits\nand $81,758 per van\nper month', fs=F3)
box(ax, c5, 1.08, 0.72, 1.24, 'Coverage,\nunmet\nvisits and\ncost of each\nallocation', fs=F3)
ym = mid + BHh/2
arrow(ax, c1 + BW, top + 0.2, c2 + 0.25, mid + BHh)          # UN -> town population
arrow(ax, c1 + BW, bot + BHh - 0.2, c2 + 0.25, mid)          # Census -> town population
arrow(ax, c2 + BW, ym, c4, ym)                                # town population -> monthly visits
txt(ax, (c2 + BW + c4)/2, ym + 0.05, 'D = P × r × s / 12', va='bottom', fs=7.6, style='italic')
arrow(ax, c3 + BW/2, top, c4 + 0.25, mid + BHh)               # visit rate -> monthly visits
arrow(ax, c3 + BW/2, bot + BHh, c4 + 0.25, mid)               # share -> monthly visits
arrow(ax, c4 + BW, ym, c5, ym)                                # monthly visits -> measures
line(ax, [c4 + BW, c5 + 0.36], [top + 0.08 + BHh/2, top + 0.08 + BHh/2]); arrow(ax, c5 + 0.36, top + 0.08 + BHh/2, c5 + 0.36, 1.08 + 1.24)
fig.savefig(os.path.join(OUT, 'fig3_translation_chain.png'), dpi=300); plt.close(fig)
print('Figures written to', OUT)
