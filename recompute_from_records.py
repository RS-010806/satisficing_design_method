"""
Independent check of the worked example in Section 3.4 of the manuscript.

We wrote this script separately from screening.py and do not import it. With this script, we
  1. recompute every requirement measure and classification from inputs.json alone,
  2. compare them with each decision record in results/decision_records.csv, and
  3. check every number of the example that we quote in the manuscript.

This is an internal check by the authors, not a test with independent analysts.

Usage:  python screening.py            (writes results/)
        python recompute_from_records.py
If any check fails, we exit with status 1.
"""

import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOWNS = ("Anadarko", "Pauls Valley", "Chickasha")
TOL = 1e-6

failures = []
passed = 0


def check(label, ok, detail=""):
    global passed
    if ok:
        passed += 1
    else:
        failures.append(f"{label}: {detail}")


def close(label, got, want, tol=TOL):
    check(label, abs(got - want) <= tol, f"got {got!r}, expected {want!r}")


# ---------------------------------------------------------------- inputs
with open(os.path.join(HERE, "inputs.json")) as f:
    I = json.load(f)

growth = I["us_population"]["2030"] / I["us_population"]["2025"]
rate = I["visit_rate"]["value"]
rate_high = rate + I["z_95"]["value"] * I["visit_rate"]["standard_error"]
share = I["mobile_share"]["value"]
van_visits = round(I["median_annual_visits_per_clinic"]["value"] / 12)
van_cost = round(I["mean_annual_cost_primary_care_clinic"]["value"] / 12)
day_visits = van_visits / I["service_days_per_week"]["value"]
budget = I["budget_per_month"]["value"]
crit, imp = I["critical_coverage"]["value"], I["important_coverage"]["value"]
years = I["years_from_base_to_2025"]["value"]


def monthly_visits(s):
    """Central and adverse monthly visits for each town, recomputed from the published inputs."""
    central, adverse = {}, {}
    for t in TOWNS:
        now = I["towns"][t]["population_2025"]
        base = I["towns"][t]["estimates_base_2020"]
        pop_central = now * growth
        pop_trend = now * (now / base) ** (5 / years)
        central[t] = pop_central * rate * s / 12
        adverse[t] = max(pop_central, pop_trend) * rate_high * s / 12
    return central, adverse


def verdict(vans, need, use_fallback):
    cap = dict(zip(TOWNS, (n * van_visits for n in vans)))
    moved = False
    if use_fallback and vans[0] >= 1 and need["Chickasha"] > vans[2] * van_visits / imp:
        cap["Anadarko"] -= day_visits
        cap["Chickasha"] += day_visits
        moved = True
    cov = {t: min(1.0, cap[t] / need[t]) for t in TOWNS}
    unmet = sum(max(0.0, need[t] - cap[t]) for t in TOWNS)
    cost = van_cost * sum(vans)
    if cost > budget or any(cov[t] < crit for t in TOWNS):
        label = "Rejected"
    elif any(cov[t] < imp for t in TOWNS):
        label = "Flagged"
    else:
        label = "Accepted"
    return cov, unmet, cost, label, moved


central, adverse = monthly_visits(share)

# ---------------------------------------------------------------- compare with every decision record
path = os.path.join(HERE, "results", "decision_records.csv")
if not os.path.exists(path):
    sys.exit("results/decision_records.csv not found: run python screening.py first")
with open(path, newline="") as f:
    recs = list(csv.DictReader(f))

expected = [(a, b, c) for a in range(5) for b in range(5) for c in range(5) if a + b + c <= 4]
check("number of decision records", len(recs) == len(expected), f"{len(recs)} records, expected {len(expected)}")
key = {"Anadarko": "anadarko", "Pauls Valley": "pauls_valley", "Chickasha": "chickasha"}
counts = {"central": {}, "adverse": {}, "fallback": {}}
for r in recs:
    vans = (int(r["vans_anadarko"]), int(r["vans_pauls_valley"]), int(r["vans_chickasha"]))
    tag = r["allocation"]
    cov_c, _, cost, lab_c, _ = verdict(vans, central, False)
    cov_a, un_a, _, lab_a, _ = verdict(vans, adverse, False)
    cov_f, un_f, _, lab_f, moved = verdict(vans, adverse, True)
    for name, lab in (("central", lab_c), ("adverse", lab_a), ("fallback", lab_f)):
        counts[name][lab] = counts[name].get(lab, 0) + 1
    check(f"{tag} cost", int(r["monthly_cost"]) == cost, f"{r['monthly_cost']} vs {cost}")
    for t in TOWNS:
        close(f"{tag} central coverage {t}", float(r[f"central_coverage_{key[t]}"]), round(cov_c[t], 6))
        close(f"{tag} adverse coverage {t}", float(r[f"adverse_coverage_{key[t]}"]), round(cov_a[t], 6))
        close(f"{tag} fallback coverage {t}", float(r[f"fallback_coverage_{key[t]}"]), round(cov_f[t], 6))
    close(f"{tag} adverse unmet", float(r["adverse_unmet_total"]), round(un_a, 6))
    close(f"{tag} fallback unmet", float(r["fallback_unmet_total"]), round(un_f, 6))
    check(f"{tag} central class", r["central_class"] == lab_c, f"{r['central_class']} vs {lab_c}")
    check(f"{tag} adverse class", r["adverse_class"] == lab_a, f"{r['adverse_class']} vs {lab_a}")
    check(f"{tag} fallback applied", r["fallback_applied"] == ("yes" if moved else "no"), r["fallback_applied"])
    check(f"{tag} final class", r["classification"].split(",")[0] == lab_f, f"{r['classification']} vs {lab_f}")

# ---------------------------------------------------------------- numbers quoted in the manuscript
ch_now = I["towns"]["Chickasha"]["population_2025"]
ch_base = I["towns"]["Chickasha"]["estimates_base_2020"]
ch_2030 = ch_now * growth
ch_trend = ch_now * (ch_now / ch_base) ** (5 / years)
quoted = [
    ("growth factor", round(growth, 7), 1.0241136),
    ("upper visit rate", round(rate_high, 4), 1.8002),
    ("lower end of the visit-rate range", round(rate - 1.96 * I["visit_rate"]["standard_error"], 3), 1.428),
    ("upper end of the visit-rate range", round(rate_high, 3), 1.800),
    ("van capacity per month", van_visits, 291),
    ("van cost per month", van_cost, 81758),
    ("Chickasha 2030 population, central", round(ch_2030, 2), 17730.48),
    ("Chickasha visits per year", round(ch_2030 * rate, 2), 28616.99),
    ("Chickasha mobile-clinic visits per year", round(ch_2030 * rate * share, 2), 4292.55),
    ("Chickasha visits per month, central", round(central["Chickasha"], 2), 357.71),
    ("Chickasha 2030 population, local trend", round(ch_trend, 2), 18670.19),
    ("Chickasha visits per month, adverse", round(adverse["Chickasha"], 2), 420.13),
    ("Anadarko visits per month, central", round(central["Anadarko"], 1), 112.6),
    ("Anadarko visits per month, adverse", round(adverse["Anadarko"], 1), 125.5),
    ("Pauls Valley visits per month, central", round(central["Pauls Valley"], 1), 127.2),
    ("Pauls Valley visits per month, adverse", round(adverse["Pauls Valley"], 1), 141.9),
    ("(1, 1, 1) cost", van_cost * 3, 245274),
    ("(1, 1, 2) cost", van_cost * 4, 327032),
    ("fifth van, cost of five vans", van_cost * 5, 408790),
    ("(1, 1, 1) central coverage in Chickasha, percent", round(100 * verdict((1, 1, 1), central, False)[0]["Chickasha"], 1), 81.4),
    ("(1, 1, 1) adverse coverage in Chickasha, percent", round(100 * verdict((1, 1, 1), adverse, False)[0]["Chickasha"], 1), 69.3),
    ("(1, 1, 1) adverse unmet visits", round(verdict((1, 1, 1), adverse, False)[1], 1), 129.1),
    ("(1, 1, 1) fallback coverage in Chickasha, percent", round(100 * verdict((1, 1, 1), adverse, True)[0]["Chickasha"], 1), 83.1),
    ("(1, 1, 1) fallback unmet visits", round(verdict((1, 1, 1), adverse, True)[1], 1), 70.9),
    ("trigger, visit requests", van_visits / imp, 363.75),
    ("capacity moved per month", round(day_visits, 1), 58.2),
    ("Chickasha capacity with the shift", round(van_visits + day_visits, 1), 349.2),
    ("Anadarko capacity with the shift", round(van_visits - day_visits, 1), 232.8),
    ("threshold checks", len(recs) * (1 + 3 + 3) * 2, 490),
]
pop_only = ch_trend * rate * share / 12
rate_only = ch_2030 * rate_high * share / 12
quoted += [
    ("Chickasha coverage, local trend only, percent", round(100 * van_visits / pop_only, 1), 77.3),
    ("Chickasha coverage, upper visit rate only, percent", round(100 * van_visits / rate_only, 1), 72.9),
]
for label, got, want in quoted:
    close(label, got, want)

want_counts = {"central": {"Rejected": 31, "Accepted": 4},
               "adverse": {"Rejected": 31, "Flagged": 3, "Accepted": 1},
               "fallback": {"Rejected": 31, "Accepted": 4}}
for case in want_counts:
    check(f"counts {case}", counts[case] == want_counts[case], f"{counts[case]} vs {want_counts[case]}")

# planning share s: 10 percent, every one-van-per-town allocation accepted at the adverse values;
# 20 percent, only (1, 1, 2) accepted, even with the fallback rule
for s, accepted_with_fallback in ((0.10, {(1, 1, 1), (2, 1, 1), (1, 2, 1), (1, 1, 2)}), (0.20, {(1, 1, 2)})):
    c_s, a_s = monthly_visits(s)
    got = {v for v in [(1, 1, 1), (2, 1, 1), (1, 2, 1), (1, 1, 2)] if verdict(v, a_s, True)[3] == "Accepted"}
    check(f"share {s} accepted with the fallback rule", got == accepted_with_fallback, f"{sorted(got)}")
    if s == 0.10:
        check("share 0.10, (1, 1, 1) accepted at the adverse values without the fallback rule",
              verdict((1, 1, 1), a_s, False)[3] == "Accepted")
    else:
        check("share 0.20, (1, 1, 1) flagged at the central values", verdict((1, 1, 1), c_s, False)[3] == "Flagged")

if failures:
    print(f"{len(failures)} of {passed + len(failures)} checks failed:")
    for x in failures:
        print("  " + x)
    sys.exit(1)
print(f"All {passed} checks passed: every record and every quoted number agrees with inputs.json.")
