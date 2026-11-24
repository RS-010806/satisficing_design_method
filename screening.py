"""
Structured satisficing screening: worked example of Section 3.4 of the manuscript
"A Structured Satisficing Design Method for Configuring Decisions Under Uncertainty Using
Future-Representative Data" (Shah, Hajihashemi, Allen and Mistree).

A regional health planner allocates mobile primary-care clinics (vans) to three Oklahoma towns
for 2030. We follow the three steps of the method:

  Step 1  Translate the published forecasts into the requirement measures (Eqs. (3) and (4)).
  Step 2  Screen every allocation at the central values and at the adverse end of each range,
          and apply the fallback rule that the stakeholders agreed in advance (Eqs. (1), (2)).
  Step 3  Write a decision record for every allocation and export the same records in JSON, CSV
          and NDJSON.

In this script, we use only the Python standard library, read every input from inputs.json and
write the results to results/. With every run, you obtain the same results.

Usage:  python screening.py
"""

import csv
import itertools
import json
import math
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "results")
TOWNS = ["Anadarko", "Pauls Valley", "Chickasha"]


def load_inputs(path=os.path.join(HERE, "inputs.json")):
    with open(path) as f:
        d = json.load(f)
    p = {
        "us_2025": d["us_population"]["2025"],
        "us_2030": d["us_population"]["2030"],
        "years": d["years_from_base_to_2025"]["value"],
        "r": d["visit_rate"]["value"],
        "se": d["visit_rate"]["standard_error"],
        "z": d["z_95"]["value"],
        "s": d["mobile_share"]["value"],
        "visits_year": d["median_annual_visits_per_clinic"]["value"],
        "cost_year": d["mean_annual_cost_primary_care_clinic"]["value"],
        "days": d["service_days_per_week"]["value"],
        "budget": d["budget_per_month"]["value"],
        "crit": d["critical_coverage"]["value"],
        "imp": d["important_coverage"]["value"],
        "max_town": d["vans_per_town"]["max"],
        "max_total": d["vans_per_town"]["max_total"],
        "shares": d["planning_share_sensitivity"],
        "towns": {t: d["towns"][t] for t in TOWNS},
    }
    p["g"] = p["us_2030"] / p["us_2025"]                 # national growth factor, 2025 to 2030
    p["r_adv"] = p["r"] + p["z"] * p["se"]               # upper end of the 95 percent range
    p["cap"] = round(p["visits_year"] / 12)              # visits per van per month (planning assumption)
    p["cost"] = round(p["cost_year"] / 12)               # dollars per van per month (planning assumption)
    p["shift"] = p["cap"] / p["days"]                    # capacity of one service day per month
    return p


# ------------------------------------------------------------------ Step 1: translation
def translate(p, s=None):
    """2030 population (central and local trend) and monthly visits for each town, Eqs. (3) and (4)."""
    s = p["s"] if s is None else s
    rows = {}
    for t in TOWNS:
        p25 = p["towns"][t]["population_2025"]
        base = p["towns"][t]["estimates_base_2020"]
        p_central = p25 * p["g"]                                  # national growth
        trend = (p25 / base) ** (5 / p["years"])                  # five more years of the local trend
        p_trend = p25 * trend
        p_adverse = max(p_central, p_trend)                       # more people: coverage harder to meet
        rows[t] = {
            "population_2025": p25,
            "estimates_base_2020": base,
            "change_2020_2025": p25 / base - 1,
            "population_2030_central": p_central,
            "local_trend_factor": trend,
            "population_2030_local_trend": p_trend,
            "population_2030_adverse": p_adverse,
            "adverse_population_source": "local trend" if p_trend > p_central else "national growth",
            "visits_month_central": p_central * p["r"] * s / 12,
            "visits_month_adverse": p_adverse * p["r_adv"] * s / 12,
            "visits_month_adverse_population_only": p_adverse * p["r"] * s / 12,
            "visits_month_adverse_rate_only": p_central * p["r_adv"] * s / 12,
        }
    return rows


# ------------------------------------------------------------------ Step 2: screening
def classify(cost, coverage, p):
    if cost > p["budget"] or min(coverage.values()) < p["crit"]:
        return "Rejected"
    if min(coverage.values()) < p["imp"]:
        return "Flagged"
    return "Accepted"


def evaluate(alloc, demand, p, fallback=False):
    """Coverage, unmet visits, cost and classification of one allocation, Eqs. (1) and (2)."""
    capacity = {t: n * p["cap"] for t, n in zip(TOWNS, alloc)}
    applied = False
    if fallback:
        n_a, n_c = alloc[0], alloc[2]
        # Trigger: Chickasha requests exceed what its vans can serve at the important threshold.
        if demand["Chickasha"] > n_c * p["cap"] / p["imp"] and n_a >= 1:
            capacity["Anadarko"] -= p["shift"]            # Anadarko team serves Chickasha one day per week
            capacity["Chickasha"] += p["shift"]
            applied = True
    coverage = {t: min(1.0, capacity[t] / demand[t]) for t in TOWNS}
    unmet = {t: max(0.0, demand[t] - capacity[t]) for t in TOWNS}
    cost = p["cost"] * sum(alloc)
    return {"capacity": capacity, "coverage": coverage, "unmet": unmet, "unmet_total": sum(unmet.values()),
            "cost": cost, "fallback_applied": applied, "class": classify(cost, coverage, p)}


def allocations(p):
    return [a for a in itertools.product(range(p["max_town"] + 1), repeat=3) if sum(a) <= p["max_total"]]


def screen(p, tr):
    d_cen = {t: tr[t]["visits_month_central"] for t in TOWNS}
    d_adv = {t: tr[t]["visits_month_adverse"] for t in TOWNS}
    return [{"allocation": a,
             "central": evaluate(a, d_cen, p),
             "adverse": evaluate(a, d_adv, p),
             "adverse_fallback": evaluate(a, d_adv, p, fallback=True)} for a in allocations(p)]


# ------------------------------------------------------------------ Step 3: decision records
def reason(e, p):
    if e["class"] == "Rejected":
        low = [t for t in TOWNS if e["coverage"][t] < p["crit"]]
        parts = []
        if e["cost"] > p["budget"]:
            parts.append("cost above the budget")
        if low:
            parts.append("coverage below 50 percent in " + ", ".join(low))
        return "; ".join(parts)
    if e["class"] == "Flagged":
        return "coverage below 80 percent in " + ", ".join(t for t in TOWNS if e["coverage"][t] < p["imp"])
    return "every requirement met"


def failed_checks(e, p):
    """The threshold checks that an allocation fails: cost, then critical and important coverage in each town."""
    out = []
    if e["cost"] > p["budget"]:
        out.append("cost above the budget")
    out += [f"critical coverage in {t}" for t in TOWNS if e["coverage"][t] < p["crit"]]
    out += [f"important coverage in {t}" for t in TOWNS if e["coverage"][t] < p["imp"]]
    return out


def fallback_rule_text(p):
    days = {5: "five"}.get(p["days"], str(p["days"]))
    return (f"trigger: {math.ceil(p['cap'] / p['imp'])} or more visit requests in a month in Chickasha; action: the Anadarko "
            f"clinic team serves Chickasha one of its {days} service days each week ({p['shift']:.1f} visits per month)")


def compact_json(obj):
    """JSON with an indent of two spaces, in which we keep each innermost object or list on one line."""
    text = json.dumps(obj, indent=2)
    inner = re.compile(r"([\{\[])\n([^\{\}\[\]]*?)\n\s*([\}\]])")
    return inner.sub(lambda m: m.group(1) + " ".join(x.strip() for x in m.group(2).split("\n")) + m.group(3), text)


def records(p, rows):
    out = []
    for r in rows:
        a, c, ad, f = r["allocation"], r["central"], r["adverse"], r["adverse_fallback"]
        final = f["class"] + (", with the fallback rule recorded" if f["class"] == "Accepted" and f["fallback_applied"] else "")
        out.append({
            "allocation": "({}, {}, {})".format(*a),
            "vans_anadarko": a[0], "vans_pauls_valley": a[1], "vans_chickasha": a[2],
            "monthly_cost": c["cost"],
            "inputs_and_sources": "inputs.json",
            "translation": "Eq. (4) with the 2030 population from the national growth factor or from Eq. (3)",
            "forecast_bounds_used": "adverse: higher 2030 population of each town and upper end of the visit rate",
            **{f"central_coverage_{t.lower().replace(' ', '_')}": round(c["coverage"][t], 6) for t in TOWNS},
            "central_failed_checks": "; ".join(failed_checks(c, p)) or "none",
            "central_class": c["class"],
            **{f"adverse_coverage_{t.lower().replace(' ', '_')}": round(ad["coverage"][t], 6) for t in TOWNS},
            "adverse_unmet_total": round(ad["unmet_total"], 6),
            "adverse_failed_checks": "; ".join(failed_checks(ad, p)) or "none",
            "adverse_class": ad["class"],
            "fallback_applied": "yes" if f["fallback_applied"] else "no",
            "fallback_rule": fallback_rule_text(p) if f["fallback_applied"] else "none",
            **{f"fallback_coverage_{t.lower().replace(' ', '_')}": round(f["coverage"][t], 6) for t in TOWNS},
            "fallback_unmet_total": round(f["unmet_total"], 6),
            "fallback_failed_checks": "; ".join(failed_checks(f, p)) or "none",
            "classification": final,
            "reason": reason(f, p),
            "approved_by": "stakeholders' planning committee (illustrative)",
        })
    return out


def sensitivity(p):
    out = []
    for s in p["shares"]:
        tr = translate(p, s)
        d_cen = {t: tr[t]["visits_month_central"] for t in TOWNS}
        d_adv = {t: tr[t]["visits_month_adverse"] for t in TOWNS}
        for a in [(1, 1, 1), (2, 1, 1), (1, 2, 1), (1, 1, 2)]:
            c, ad, f = evaluate(a, d_cen, p), evaluate(a, d_adv, p), evaluate(a, d_adv, p, True)
            out.append({"share": s, "allocation": "({}, {}, {})".format(*a),
                        "central_coverage_chickasha": round(c["coverage"]["Chickasha"], 6), "central_class": c["class"],
                        "adverse_coverage_chickasha": round(ad["coverage"]["Chickasha"], 6), "adverse_class": ad["class"],
                        "fallback_applied": "yes" if f["fallback_applied"] else "no",
                        "fallback_coverage_chickasha": round(f["coverage"]["Chickasha"], 6), "fallback_class": f["class"]})
    return out


def nested(rec):
    """The same decision record, nested for JSON and NDJSON."""
    key = {"Anadarko": "anadarko", "Pauls Valley": "pauls_valley", "Chickasha": "chickasha"}
    checks = lambda v: [] if v == "none" else v.split("; ")  # noqa: E731
    return {
        "allocation": rec["allocation"],
        "vans": {t: rec[f"vans_{key[t]}"] for t in TOWNS},
        "monthly_cost": rec["monthly_cost"],
        "inputs_and_sources": rec["inputs_and_sources"],
        "translation": rec["translation"],
        "forecast_bounds_used": rec["forecast_bounds_used"],
        "central": {"coverage": {t: rec[f"central_coverage_{key[t]}"] for t in TOWNS},
                    "failed_checks": checks(rec["central_failed_checks"]), "class": rec["central_class"]},
        "adverse": {"coverage": {t: rec[f"adverse_coverage_{key[t]}"] for t in TOWNS}, "unmet_total": rec["adverse_unmet_total"],
                    "failed_checks": checks(rec["adverse_failed_checks"]), "class": rec["adverse_class"]},
        "adverse_with_fallback": {"fallback_applied": rec["fallback_applied"] == "yes", "fallback_rule": rec["fallback_rule"],
                                  "coverage": {t: rec[f"fallback_coverage_{key[t]}"] for t in TOWNS},
                                  "unmet_total": rec["fallback_unmet_total"],
                                  "failed_checks": checks(rec["fallback_failed_checks"])},
        "classification": rec["classification"],
        "reason": rec["reason"],
        "approved_by": rec["approved_by"],
    }


def write_json_and_ndjson(recs):
    docs = [nested(r) for r in recs]
    with open(os.path.join(OUT, "decision_records.json"), "w") as f:
        f.write(compact_json({"schema_version": "1.0",
                              "description": "Decision records of the worked example in Section 3.4 of the manuscript, one for each "
                                             "of the 35 allocations; we provide the same records in decision_records.csv and "
                                             "decision_records.ndjson.",
                              "records": docs}) + "\n")
    with open(os.path.join(OUT, "decision_records.ndjson"), "w") as f:
        for d in docs:
            f.write(json.dumps(d, separators=(",", ":")) + "\n")


def write_csv(name, rows):
    with open(os.path.join(OUT, name), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main():
    os.makedirs(OUT, exist_ok=True)
    p = load_inputs()
    tr = translate(p)
    rows = screen(p, tr)

    write_csv("translation.csv", [{"town": t, **{k: (round(v, 6) if isinstance(v, float) else v) for k, v in tr[t].items()}}
                                  for t in TOWNS])
    flat = []
    for r in rows:
        for case in ("central", "adverse", "adverse_fallback"):
            e = r[case]
            flat.append({"allocation": "({}, {}, {})".format(*r["allocation"]), "case": case, "monthly_cost": e["cost"],
                         **{f"capacity_{t.lower().replace(' ', '_')}": round(e["capacity"][t], 6) for t in TOWNS},
                         **{f"coverage_{t.lower().replace(' ', '_')}": round(e["coverage"][t], 6) for t in TOWNS},
                         **{f"unmet_{t.lower().replace(' ', '_')}": round(e["unmet"][t], 6) for t in TOWNS},
                         "unmet_total": round(e["unmet_total"], 6),
                         "fallback_applied": "yes" if e["fallback_applied"] else "no", "class": e["class"]})
    write_csv("screening.csv", flat)
    recs = records(p, rows)
    write_csv("decision_records.csv", recs)
    write_json_and_ndjson(recs)
    write_csv("sensitivity.csv", sensitivity(p))

    counts = {case: {k: sum(1 for r in rows if r[case]["class"] == k) for k in ("Accepted", "Flagged", "Rejected")}
              for case in ("central", "adverse", "adverse_fallback")}
    pick = {r["allocation"]: r for r in rows}
    c111, c112 = pick[(1, 1, 1)], pick[(1, 1, 2)]
    pc = p["towns"]["Chickasha"]["population_2025"] * p["g"]
    summary = {
        "national_growth_factor": p["g"], "visit_rate_adverse": p["r_adv"], "van_capacity_per_month": p["cap"],
        "van_cost_per_month": p["cost"], "allocations": len(rows), "counts": counts,
        "threshold_checks": len(rows) * 7 * 2,
        "chickasha_central_chain": {"population_2030": pc, "visits_year": pc * p["r"], "visits_year_mobile": pc * p["r"] * p["s"],
                                    "visits_month": pc * p["r"] * p["s"] / 12},
        "allocation_111": {case: {"class": c111[case]["class"], "coverage_chickasha": c111[case]["coverage"]["Chickasha"],
                                  "unmet_total": c111[case]["unmet_total"]} for case in ("central", "adverse", "adverse_fallback")},
        "added_cost_fourth_van": c112["central"]["cost"] - c111["central"]["cost"],
        "added_cost_share": (c112["central"]["cost"] - c111["central"]["cost"]) / c111["central"]["cost"],
        "chickasha_one_van_coverage": {k: p["cap"] / tr["Chickasha"][v] for k, v in (
            ("central", "visits_month_central"), ("adverse_population_only", "visits_month_adverse_population_only"),
            ("adverse_rate_only", "visits_month_adverse_rate_only"), ("adverse", "visits_month_adverse"))},
        "fallback_trigger_one_van": p["cap"] / p["imp"], "fallback_shift": p["shift"],
    }
    with open(os.path.join(OUT, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1)

    print(f"National growth factor 2025 to 2030: {p['g']:.7f}; adverse visit rate: {p['r_adv']:.4f}")
    print(f"Van capacity {p['cap']} visits per month; van cost ${p['cost']:,} per month")
    for t in TOWNS:
        v = tr[t]
        print(f"  {t:13s} 2030 central {v['population_2030_central']:9,.1f}  local trend {v['population_2030_local_trend']:9,.1f}  "
              f"visits per month central {v['visits_month_central']:6.1f}  adverse {v['visits_month_adverse']:6.1f}")
    for case, c in counts.items():
        print(f"  {case:17s} {c}")
    for case in ("central", "adverse", "adverse_fallback"):
        e = c111[case]
        print(f"  (1, 1, 1) {case:17s} {e['class']:9s} coverage in Chickasha {e['coverage']['Chickasha']:.1%}, "
              f"unmet {e['unmet_total']:.1f} visits per month")
    print(f"  Fourth van: ${summary['added_cost_fourth_van']:,} more per month ({summary['added_cost_share']:.1%})")
    print(f"Results written to {OUT}")


if __name__ == "__main__":
    main()
