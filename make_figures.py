"""
Draws Figures 1 to 6 of the manuscript at their printed size and saves them in figures/.

  Figure 1  Overall procedure flowchart
  Figure 2  Functional model of the method in IDEF0 notation
  Figure 3  Step 1: input processing and translation flowchart
  Figure 4  Step 2: satisficing logic flowchart
  Figure 5  Step 3: decision record and output generation flowchart
  Figure 6  Chain from the published inputs to the measures of each allocation in the example

We draw each figure in inches, so that font sizes in points print as stated, and save it at 400 dots per inch.

Usage:  python make_figures.py      (needs matplotlib; see requirements.txt)
"""
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Polygon, Rectangle  # noqa: E402

plt.rcParams['font.family'] = ['Liberation Sans', 'DejaVu Sans']
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figures')
os.makedirs(OUT, exist_ok=True)
DPI = 400

# Colors of the submitted flowcharts: fill, edge
BLUE = ('#dae8fc', '#6c8ebf')
PURPLE = ('#e1d5e7', '#9673a6')
GREEN = ('#d5e8d4', '#82b366')
YELLOW = ('#fff2cc', '#d6b656')
RED = ('#f8cecc', '#b85450')
ORANGE = ('#ffe6cc', '#d79b00')
GRAY = ('#f5f5f5', '#666666')
INK = '#1a1a1a'
LW = 0.9


def canvas(w, h):
    fig = plt.figure(figsize=(w, h))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis('off')
    return fig, ax


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=DPI, facecolor='white')
    plt.close(fig)


def box(ax, cx, cy, w, h, title=None, lines=(), color=PURPLE, rounded=False, fs_title=8.0, fs=7.2, align='center',
        italic=False, title_caps=False, lw=LW):
    """Box centered at (cx, cy) with an optional bold title and lines of text."""
    x, y = cx - w / 2, cy - h / 2
    if rounded:
        p = FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=0.09', fc=color[0], ec=color[1], lw=lw * 1.4)
    else:
        p = Rectangle((x, y), w, h, fc=color[0], ec=color[1], lw=lw * 1.2)
    ax.add_patch(p)
    rows = []
    if title:
        rows.append((title.upper() if title_caps else title, fs_title, 'bold'))
    rows += [(t, fs, 'normal') for t in lines]
    # vertical layout of the rows
    heights = [r[1] / 72 * 1.32 for r in rows]
    total = sum(heights)
    ty = cy + total / 2
    for (t, f, wt), hh in zip(rows, heights):
        ty -= hh
        if align == 'left':
            ax.text(x + 0.09, ty + hh * 0.42, t, ha='left', va='center', fontsize=f, fontweight=wt, color=INK,
                    style='italic' if italic else 'normal')
        else:
            ax.text(cx, ty + hh * 0.42, t, ha='center', va='center', fontsize=f, fontweight=wt, color=INK,
                    style='italic' if italic else 'normal')
    return (x, y, w, h)


def diamond(ax, cx, cy, w, h, text, color=ORANGE, fs=7.0):
    ax.add_patch(Polygon([(cx - w / 2, cy), (cx, cy + h / 2), (cx + w / 2, cy), (cx, cy - h / 2)], closed=True, fc=color[0],
                         ec=color[1], lw=LW * 1.2))
    ax.text(cx, cy, text, ha='center', va='center', fontsize=fs, fontweight='bold', color=INK, linespacing=1.12)


def parallelogram(ax, cx, cy, w, h, title, lines, color=BLUE, skew=0.35, fs_title=8.0, fs=7.2):
    x, y = cx - w / 2, cy - h / 2
    ax.add_patch(Polygon([(x + skew, y + h), (x + w, y + h), (x + w - skew, y), (x, y)], closed=True, fc=color[0], ec=color[1],
                         lw=LW * 1.2))
    rows = [(title, fs_title, 'bold')] + [(t, fs, 'normal') for t in lines]
    heights = [r[1] / 72 * 1.32 for r in rows]
    ty = cy + sum(heights) / 2
    for (t, f, wt), hh in zip(rows, heights):
        ty -= hh
        ax.text(cx, ty + hh * 0.42, t, ha='center', va='center', fontsize=f, fontweight=wt, color=INK)


def arrow(ax, pts, lw=LW, dashed=False, head=True, color=INK):
    """Polyline through pts with an arrowhead at the last point."""
    xs, ys = zip(*pts)
    ls = (0, (4, 2.5)) if dashed else '-'
    if len(pts) > 2:
        ax.plot(xs[:-1], ys[:-1], color=color, lw=lw, linestyle=ls, solid_capstyle='butt', solid_joinstyle='miter')
    if head:
        ax.annotate('', xy=pts[-1], xytext=pts[-2],
                    arrowprops=dict(arrowstyle='-|>', color=color, lw=lw, shrinkA=0, shrinkB=0, mutation_scale=9,
                                    linestyle=ls))
    else:
        ax.plot(xs[-2:], ys[-2:], color=color, lw=lw, linestyle=ls)


def label(ax, x, y, text, fs=6.8, ha='center', va='center', bold=False, italic=False, color=INK, rot=0):
    ax.text(x, y, text, ha=ha, va=va, fontsize=fs, fontweight='bold' if bold else 'normal', style='italic' if italic else 'normal',
            color=color, rotation=rot, linespacing=1.15)


# ---------------------------------------------------------------- Figure 1: overall procedure flowchart
def figure1():
    W, H = 4.8, 6.15
    fig, ax = canvas(W, H)
    cx, bw = 2.15, 3.75
    steps = [
        (5.55, BLUE, 'STEP 1: INPUT PROCESSING AND TRANSLATION',
         ['• Designer collects forecasts, stakeholder statements and candidates',
          '• Designer translates each forecast into requirement measures',
          '• Designer checks the inputs for format, feasibility and completeness']),
        (3.95, PURPLE, 'STEP 2: SATISFICING LOGIC',
         ['• Designer screens each candidate at the central values',
          '• Designer screens it again at the adverse end of each range',
          '• Designer applies the fallback rules agreed in advance',
          '• Designer accepts, flags or rejects each candidate']),
        (2.30, GREEN, 'STEP 3: DECISION RECORD AND OUTPUT GENERATION',
         ['• Designer records the inputs, checks, rules and verdict',
          '• Designer exports the record in JSON, CSV and NDJSON',
          '• Stakeholders review and approve the decision']),
    ]
    hs = [0.98, 1.12, 0.98]
    for (cy, col, title, lines), h in zip(steps, hs):
        box(ax, cx, cy, bw, h, title, lines, color=col, rounded=True, fs_title=8.4, fs=7.4, align='left')
    # arrows between steps with labels
    arrow(ax, [(cx, 5.55 - 0.49), (cx, 3.95 + 0.56)], lw=1.8)
    label(ax, cx + 0.12, 4.79, 'Validated inputs and translated measures', ha='left', italic=True, fs=7.4)
    arrow(ax, [(cx, 3.95 - 0.56), (cx, 2.30 + 0.49)], lw=1.8)
    label(ax, cx + 0.12, 3.10, 'Accepted, flagged and rejected candidates', ha='left', italic=True, fs=7.4)
    arrow(ax, [(cx, 2.30 - 0.49), (cx, 1.25 + 0.24)], lw=1.8)
    label(ax, cx + 0.12, 1.65, 'Decision records', ha='left', italic=True, fs=7.4)
    box(ax, cx, 1.25, bw, 0.46, 'Ready for stakeholder review and downstream use', [], color=GRAY, rounded=True, fs_title=8.4)
    # feedback loop on the right
    fx = cx + bw / 2 + 0.32
    arrow(ax, [(cx + bw / 2, 1.25), (fx, 1.25), (fx, 5.55), (cx + bw / 2, 5.55)], dashed=True, lw=1.0)
    label(ax, fx + 0.12, 3.40, 'Feedback: realized values and updated forecasts', rot=90, italic=True, fs=7.0)
    label(ax, cx, 0.52, 'Stakeholders decide what matters;\nthe designer applies the same steps to every candidate', italic=True,
          fs=9.0, color='#7f7f7f')
    save(fig, 'fig1_overall_procedure.png')


# ---------------------------------------------------------------- Figure 2: functional model (IDEF0)
def figure2():
    W, H = 6.27, 2.8
    fig, ax = canvas(W, H)
    bw, bh, by = 0.98, 0.86, 1.12
    xs = [1.58, 3.29, 4.89]
    cols = [BLUE, PURPLE, GREEN]
    names = [('A1', 'Input processing', 'and translation'), ('A2', 'Satisficing logic', 'at the central value', 'and the adverse end'),
             ('A3', 'Decision record', 'and output', 'generation')]
    for x, c, n in zip(xs, cols, names):
        box(ax, x, by, bw, bh, n[0], list(n[1:]), color=c, fs_title=8.6, fs=7.0)
    top, bot = by + bh / 2, by - bh / 2
    left = xs[0] - bw / 2
    # inputs to A1, each label above its arrow
    ins = [(by + 0.28, 'Published forecasts\nwith stated ranges'), (by, 'Stakeholder statements'), (by - 0.28, 'Candidate configurations')]
    for yy, t in ins:
        arrow(ax, [(0.04, yy), (left, yy)])
        label(ax, 0.06, yy + 0.03, t, ha='left', va='bottom', fs=6.3)
    # outputs between boxes
    for k, txt in enumerate(['Measures at the\ncentral and the\nadverse values', 'Accepted,\nflagged and\nrejected']):
        x1, x2 = xs[k] + bw / 2, xs[k + 1] - bw / 2
        arrow(ax, [(x1, by), (x2, by)])
        label(ax, (x1 + x2) / 2, by + 0.04, txt, va='bottom', fs=6.2)
    # outputs of A3
    x3 = xs[2] + bw / 2
    arrow(ax, [(x3, by + 0.22), (W - 0.03, by + 0.22)])
    label(ax, x3 + 0.04, by + 0.19, 'Decision records\n(JSON, CSV, NDJSON)', ha='left', va='top', fs=6.0)
    arrow(ax, [(x3, by - 0.22), (W - 0.03, by - 0.22)])
    label(ax, x3 + 0.04, by - 0.25, 'Verdict for each\ncandidate', ha='left', va='top', fs=6.0)
    # controls, labels to the right of each arrow
    ctl = ['Translation relations\nand their sources', 'Thresholds with priority\ntags; adverse-end rule;\nfallback rules agreed\nin advance',
           'Content that others\nneed to recompute\neach verdict']
    for x, t in zip(xs, ctl):
        arrow(ax, [(x, top + 0.62), (x, top)])
        label(ax, x + 0.05, top + 0.31, t, ha='left', va='center', fs=6.2)
    # mechanisms, labels to the right of each arrow
    mech = ['Designer;\nspreadsheet\nor script', 'Designer;\nspreadsheet\nor script', 'Designer;\nstakeholders\nwho approve']
    for x, t in zip(xs, mech):
        arrow(ax, [(x, bot - 0.55), (x, bot)])
        label(ax, x + 0.05, bot - 0.27, t, ha='left', va='center', fs=6.2)
    # feedback from the decision records to the controls of A1
    fy = top + 0.95
    fx = left + 0.14
    arrow(ax, [(W - 0.2, by + 0.22), (W - 0.2, fy), (fx, fy), (fx, top)], dashed=True, lw=1.0)
    label(ax, (fx + W - 0.2) / 2, fy + 0.05, 'Feedback: with realized values and updated forecasts, the designer revises translations, '
          'thresholds and fallback rules', va='bottom', fs=6.3, italic=True)
    save(fig, 'fig2_functional_model.png')


# ---------------------------------------------------------------- Figure 3: Step 1 flowchart
def figure3():
    W, H = 6.27, 7.0
    fig, ax = canvas(W, H)
    cx, bw = 2.45, 3.2
    box(ax, cx, 6.62, 2.3, 0.5, 'START', ['Structured satisficing method'], color=GREEN, rounded=True, fs_title=9, fs=8.4)
    box(ax, cx, 5.95, bw, 0.4, 'STEP 1: INPUT PROCESSING AND TRANSLATION', color=YELLOW, fs_title=8.6)
    parallelogram(ax, cx, 5.08, 3.95, 0.98, 'Designer collects:',
                  ['• Forecasts with central value, stated range, source and timeframe', '• Stakeholder statements with priority tags',
                   '• Fallback rules agreed in advance', '• Candidate configurations'], fs=7.3)
    box(ax, cx, 3.98, bw, 0.82, 'Translate forecasts into requirement measures',
        ['• Write each relation and the source of each coefficient', '• Carry the forecast range through the relation',
         '• Obtain a central and an adverse value'], color=PURPLE, fs=7.3)
    box(ax, cx, 3.02, bw, 0.62, 'Validate input format',
        ['• Consistent units and time periods', '• Source or planning-assumption label for each input'], color=PURPLE, fs=7.3)
    diamond(ax, cx, 2.0, 2.3, 0.92, 'Every quantity\ntranslated with\nenough confidence?', fs=7.6)
    box(ax, cx, 0.98, bw, 0.62, 'Feasibility analysis',
        ['• Check conflicts among thresholds', '• Confirm a candidate can meet every critical requirement'], color=PURPLE, fs=7.3)
    box(ax, cx, 0.3, bw, 0.36, 'STEP 2: SATISFICING LOGIC', color=YELLOW, fs_title=8.6)
    rx = 5.2
    box(ax, rx, 2.0, 1.75, 0.82, 'Flag the quantity', ['• Collect more data', '• Record the decision', '• Translate again'],
        color=RED, fs=7.3)
    arrow(ax, [(cx, 6.37), (cx, 6.15)])
    arrow(ax, [(cx, 5.75), (cx, 5.57)])
    arrow(ax, [(cx, 4.59), (cx, 4.39)])
    arrow(ax, [(cx, 3.57), (cx, 3.33)])
    arrow(ax, [(cx, 2.71), (cx, 2.46)])
    arrow(ax, [(cx, 1.54), (cx, 1.29)])
    arrow(ax, [(cx, 0.67), (cx, 0.48)])
    label(ax, cx + 0.12, 1.42, 'YES', bold=True, ha='left', fs=7)
    arrow(ax, [(cx + 1.15, 2.0), (rx - 0.875, 2.0)])
    label(ax, cx + 1.38, 2.1, 'NO', bold=True, fs=7)
    arrow(ax, [(rx, 2.41), (rx, 3.98), (cx + bw / 2, 3.98)])
    save(fig, 'fig3_step1_input_processing.png')


# ---------------------------------------------------------------- Figure 4: Step 2 flowchart
def figure4():
    W, H = 6.27, 9.1
    fig, ax = canvas(W, H)
    cx, bw = 2.5, 2.9
    rx, rw = 5.08, 1.92
    dw = 2.05
    y = {}
    y['s2'] = 8.85; y['list'] = 8.35; y['each'] = 7.86; y['cen'] = 7.38; y['d1'] = 6.72; y['adv'] = 6.04; y['d2'] = 5.33
    y['d3'] = 4.44; y['d4'] = 3.52; y['rej2'] = 2.78; y['d5'] = 2.08; y['d6'] = 1.28; y['rank'] = 0.66; y['s3'] = 0.2
    box(ax, cx, y['s2'], bw, 0.34, 'STEP 2: SATISFICING LOGIC', color=YELLOW, fs_title=8.4)
    box(ax, cx, y['list'], bw, 0.5, 'Designer lists candidate configurations', ['(in the example, all 35 allocations within the budget)'],
        color=BLUE, fs=7.0)
    box(ax, cx, y['each'], bw, 0.3, None, ['For each configuration'], color=GRAY, fs=7.6, italic=True)
    box(ax, cx, y['cen'], bw, 0.48, 'Compute requirement measures', ['at the central value of each forecast'], color=PURPLE, fs=7.2)
    diamond(ax, cx, y['d1'], dw, 0.6, 'Meets every critical\nrequirement?', fs=7.2)
    box(ax, cx, y['adv'], bw, 0.5, 'Compute the measures again', ['at the adverse end of each forecast range'], color=PURPLE, fs=7.2)
    diamond(ax, cx, y['d2'], dw, 0.68, 'Meets every critical\nand important\nrequirement?', fs=7.2)
    diamond(ax, cx, y['d3'], dw + 0.2, 0.86, 'Fallback rule agreed\nin advance restores\nthem within the\nbudget?', fs=7.0)
    diamond(ax, cx, y['d4'], dw, 0.7, 'Meets every critical\nrequirement at the\nadverse end?', fs=7.0)
    box(ax, cx, y['rej2'], bw, 0.42, 'Reject configuration', ['Record the reason'], color=RED, fs=7.2)
    diamond(ax, cx, y['d5'], dw, 0.56, 'More\nconfigurations?', color=GRAY, fs=7.2)
    diamond(ax, cx, y['d6'], dw, 0.6, 'Any accepted\nconfigurations?', fs=7.2)
    box(ax, cx, y['rank'], bw, 0.42, 'Rank accepted configurations', ['with the desirable requirements'], color=GREEN, fs=7.2)
    box(ax, cx, y['s3'], bw, 0.32, 'STEP 3: DECISION RECORD AND OUTPUT GENERATION', color=YELLOW, fs_title=7.3)
    # right column outcomes
    box(ax, rx, y['d1'], rw, 0.46, 'Reject configuration', ['Record the reason'], color=RED, fs=7.2)
    box(ax, rx, y['d2'], rw, 0.46, 'Accept configuration', ['Add to the satisficing set'], color=GREEN, fs=7.2)
    box(ax, rx, y['d3'], rw, 0.6, 'Accept configuration', ['with the fallback rule', 'recorded'], color=GREEN, fs=7.2)
    box(ax, rx, y['d4'], rw, 0.6, 'Flag configuration', ['Record the shortfall and', 'the cost of removing it'], color=ORANGE, fs=7.2)
    box(ax, rx, y['d6'], rw, 0.78, 'Trigger stakeholder review',
        ['• Revise thresholds or budget?', '• Add a fallback rule?', '• Accept a flagged one?'], color=RED, fs=6.9, fs_title=7.6)
    # main column arrows
    seq = [('s2', 0.17, 'list', 0.25), ('list', 0.25, 'each', 0.15), ('each', 0.15, 'cen', 0.24), ('cen', 0.24, 'd1', 0.30),
           ('d1', 0.30, 'adv', 0.25), ('adv', 0.25, 'd2', 0.34), ('d2', 0.34, 'd3', 0.43), ('d3', 0.43, 'd4', 0.35),
           ('d4', 0.35, 'rej2', 0.21), ('rej2', 0.21, 'd5', 0.28), ('d5', 0.28, 'd6', 0.30), ('d6', 0.30, 'rank', 0.21),
           ('rank', 0.21, 's3', 0.16)]
    for a, ha, b, hb in seq:
        arrow(ax, [(cx, y[a] - ha), (cx, y[b] + hb)])
    for yy in (y['d1'] - 0.30, y['d6'] - 0.30):
        label(ax, cx + 0.1, yy - 0.09, 'YES', bold=True, ha='left', fs=6.6)
    for yy in (y['d2'] - 0.34, y['d3'] - 0.43, y['d4'] - 0.35, y['d5'] - 0.28):
        label(ax, cx + 0.1, yy - 0.09, 'NO', bold=True, ha='left', fs=6.6)
    # right arrows from diamonds
    for k, txt, half in (('d1', 'NO', dw / 2), ('d2', 'YES', dw / 2), ('d3', 'YES', (dw + 0.2) / 2), ('d4', 'YES', dw / 2),
                         ('d6', 'NO', dw / 2)):
        arrow(ax, [(cx + half, y[k]), (rx - rw / 2, y[k])])
        label(ax, cx + half + 0.2, y[k] + 0.09, txt, bold=True, fs=6.6)
    # bus from the right-column outcomes to "More configurations?"
    bx = W - 0.08
    for k in ('d1', 'd2', 'd3', 'd4'):
        ax.plot([rx + rw / 2, bx], [y[k], y[k]], color=INK, lw=LW)
    ax.plot([bx, bx], [y['d1'], y['d5']], color=INK, lw=LW)
    arrow(ax, [(bx, y['d5']), (cx + dw / 2, y['d5'])])
    # loop back for more configurations
    lx = 0.12
    arrow(ax, [(cx - dw / 2, y['d5']), (lx, y['d5']), (lx, y['each']), (cx - bw / 2, y['each'])])
    label(ax, cx - dw / 2 - 0.2, y['d5'] + 0.09, 'YES', bold=True, fs=6.6)
    save(fig, 'fig4_step2_satisficing_logic.png')


# ---------------------------------------------------------------- Figure 5: Step 3 flowchart
def figure5():
    W, H = 6.27, 4.05
    fig, ax = canvas(W, H)
    box(ax, W / 2, 3.83, 4.6, 0.34, 'STEP 3: DECISION RECORD AND OUTPUT GENERATION', color=YELLOW, fs_title=8.4)
    # decision record, two columns of content
    rx, ry, rw, rh = W / 2, 3.02, 5.9, 0.9
    box(ax, rx, ry, rw, rh, None, [], color=PURPLE)
    label(ax, rx, ry + 0.3, 'Generate the decision record for each configuration', fs=8.0, bold=True)
    left = ['• Inputs and their sources', '• Translation relations', '• Forecast bound used in each check']
    right = ['• Result of each check', '• Fallback rules applied and conflicts recorded', '• Classification and approver']
    for k, (a, b) in enumerate(zip(left, right)):
        yy = ry + 0.08 - k * 0.17
        label(ax, rx - rw / 2 + 0.55, yy, a, ha='left', fs=7.4)
        label(ax, rx + 0.25, yy, b, ha='left', fs=7.4)
    # structured outputs and export, side by side
    box(ax, 1.62, 1.83, 2.95, 0.82, 'Generate structured outputs',
        ['• Accepted configurations', '• Flagged configurations with their shortfalls', '• Rejected configurations with their reasons'],
        color=PURPLE, fs=7.4)
    box(ax, 4.82, 1.83, 2.6, 0.82, 'Export the same record',
        ['• JSON for system integration', '• CSV for spreadsheet review', '• NDJSON for streaming and batch processing'],
        color=PURPLE, fs=7.4)
    parallelogram(ax, 2.15, 0.55, 3.9, 0.66, 'Output for stakeholder review and downstream use', ['(audits, dashboards, schedulers)'],
                  fs=7.4, fs_title=7.9)
    box(ax, 5.25, 0.55, 1.75, 0.66, 'END', ['Revisit the record when', 'providers update forecasts'], color=GREEN, rounded=True,
        fs_title=8.4, fs=7.2)
    arrow(ax, [(W / 2, 3.66), (W / 2, ry + rh / 2)])
    arrow(ax, [(1.62, ry - rh / 2), (1.62, 1.83 + 0.41)])
    arrow(ax, [(1.62 + 1.475, 1.83), (4.82 - 1.3, 1.83)])
    arrow(ax, [(4.82, 1.83 - 0.41), (4.82, 1.12), (2.15, 1.12), (2.15, 0.55 + 0.33)])
    arrow(ax, [(2.15 + 1.95 - 0.17, 0.55), (5.25 - 0.875, 0.55)])
    save(fig, 'fig5_step3_output_generation.png')


# ---------------------------------------------------------------- Figure 6: translation chain of the example
def figure6():
    W, H = 6.27, 3.8
    fig, ax = canvas(W, H)
    fs = 6.8
    pop_x, vis_x, mea_x, cy = 1.98, 3.95, 5.6, 1.78
    # published sources (blue)
    box(ax, 0.7, 2.55, 1.3, 0.98, 'United Nations (2024)', ['U.S. population,', '347,275,808 (2025)', 'and 355,649,881', '(2030)'],
        color=BLUE, fs=fs, fs_title=7.2)
    box(ax, 0.7, 1.0, 1.3, 0.98, 'U.S. Census Bureau', ['(2026): town', 'populations,', 'April 1, 2020, and', 'July 1, 2025'],
        color=BLUE, fs=fs, fs_title=7.2)
    box(ax, vis_x, 3.33, 1.55, 0.74, 'Santo and Kang (2023)', ['1.614 primary-care visits', 'per person per year (95%',
                                                               'range 1.428 to 1.800)'], color=BLUE, fs=fs, fs_title=7.2)
    # planning assumptions (yellow)
    box(ax, vis_x, 0.62, 1.55, 0.66, 'Planning assumption', ['stakeholders assign s = 15%', 'of primary-care visits',
                                                             'to the mobile clinics'], color=YELLOW, fs=fs, fs_title=7.2)
    box(ax, mea_x, 3.33, 1.3, 0.74, 'Planning assumptions', ['based on Malone et al.', '(2020): 291 visits and',
                                                              '$81,758 per van', 'per month'], color=YELLOW, fs=fs, fs_title=7.2)
    # calculated (purple) and measures (green)
    box(ax, pop_x, cy, 1.1, 1.12, '2030 population', ['of each town:', 'central (national', 'growth) and local', 'trend, Eq. (3)'],
        color=PURPLE, fs=fs, fs_title=7.2)
    box(ax, vis_x, cy, 1.12, 1.12, 'Monthly visits', ['that residents', 'need from the', 'mobile clinics,', 'Eq. (4)'],
        color=PURPLE, fs=fs, fs_title=7.2)
    box(ax, mea_x, cy, 1.22, 1.12, 'Coverage,', ['unmet visits', 'and cost of each', 'allocation,', 'Eqs. (1) and (2)'], color=GREEN,
        fs=fs, fs_title=7.2)
    jx = 1.39
    arrow(ax, [(0.7 + 0.65, 2.55), (jx, 2.55), (jx, cy + 0.25), (pop_x - 0.55, cy + 0.25)])
    arrow(ax, [(0.7 + 0.65, 1.0), (jx, 1.0), (jx, cy - 0.25), (pop_x - 0.55, cy - 0.25)])
    arrow(ax, [(pop_x + 0.55, cy), (vis_x - 0.56, cy)])
    label(ax, (pop_x + 0.55 + vis_x - 0.56) / 2, cy + 0.05, 'D = P × r × s / 12', va='bottom', fs=6.6, italic=True)
    arrow(ax, [(vis_x, 3.33 - 0.37), (vis_x, cy + 0.56)])
    arrow(ax, [(vis_x, 0.62 + 0.33), (vis_x, cy - 0.56)])
    arrow(ax, [(vis_x + 0.56, cy), (mea_x - 0.61, cy)])
    arrow(ax, [(mea_x, 3.33 - 0.37), (mea_x, cy + 0.56)])
    # legend
    ly = 0.1
    label(ax, 0.08, ly + 0.06, 'Status of each value:', ha='left', fs=6.6, bold=True)
    for x0, col, t in ((1.52, BLUE, 'Published'), (2.30, YELLOW, 'Planning assumption'), (3.50, PURPLE, 'Calculated'),
                       (4.38, GREEN, 'Requirement measures')):
        ax.add_patch(Rectangle((x0, ly - 0.01), 0.16, 0.14, fc=col[0], ec=col[1], lw=LW))
        label(ax, x0 + 0.21, ly + 0.06, t, ha='left', fs=6.6)
    save(fig, 'fig6_translation_chain.png')


if __name__ == '__main__':
    for f in (figure1, figure2, figure3, figure4, figure5, figure6):
        f()
    print('Figures written to', OUT)
