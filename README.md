# Structured satisficing design method: worked example

Code and data for the worked example in Section 3.4 of the manuscript

> R. A. Shah, S. Hajihashemi, J. K. Allen and F. Mistree, "A Structured Satisficing Design Method for Configuring Decisions Under Uncertainty Using Future-Representative Data," revised manuscript submitted to *Research in Engineering Design*.

In the example, a regional health planner allocates mobile primary-care clinics (vans) to three Oklahoma towns, Anadarko, Pauls Valley and Chickasha, for 2030. We start from the United Nations projection of the U.S. population, translate it into the monthly clinic visits that the residents of each town need, and screen all 35 allocations with four vans or fewer at the central values and at the adverse end of each forecast range, with and without a fallback rule that the stakeholders agree in advance.

## Files

| File | Content |
|---|---|
| `inputs.json` | Every input with its value, unit, status (published, calculated, planning assumption or stakeholder requirement) and source |
| `screening.py` | The three steps of the method: translation (Step 1), screening (Step 2) and decision records (Step 3) |
| `recompute_from_records.py` | A separately written check that recomputes every measure and classification from `inputs.json`, compares them with each decision record, and checks every number of the example that we quote in the manuscript |
| `make_figures.py` | Draws Figs. 1 to 3 of the manuscript |
| `results/translation.csv` | 2030 population and monthly visits for each town (Table 5 and Appendix A) |
| `results/screening.csv` | Capacity, coverage, unmet visits, cost and classification of every allocation in each of the three cases |
| `results/decision_records.csv` | One decision record for each of the 35 allocations (Table 7 and Appendix B) |
| `results/sensitivity.csv` | Classifications for planning shares of 10, 15 and 20 percent (Appendix C) |
| `results/summary.json` | The values that we quote in the text |
| `figures/` | Figs. 1 to 3 |

## How to run

```bash
python screening.py                 # writes results/
python recompute_from_records.py    # checks every record and every quoted number
pip install -r requirements.txt     # only for the figures
python make_figures.py              # writes figures/
```

You need Python 3.8 or later. With `screening.py` and `recompute_from_records.py`, you use the Python standard library only; with `make_figures.py`, you also use matplotlib.

## Results of the example

- At the central values, we reject 31 allocations and accept 4. With one van in each town, (1, 1, 1), the planner covers 81.4 percent of the needed visits in Chickasha for $245,274 per month.
- At the adverse end of the forecast ranges, we flag (1, 1, 1), (2, 1, 1) and (1, 2, 1): with one van in Chickasha, the planner covers 69.3 percent of the needed visits there, below the important threshold of 80 percent.
- With the fallback rule, under which the Anadarko clinic team serves Chickasha one day per week when the Chickasha team records 364 or more visit requests in a month, we accept these three allocations again: the planner covers 83.1 percent in Chickasha at no added cost. With a fourth van in Chickasha, (1, 1, 2), the planner meets every requirement for $327,032 per month, that is, $81,758 or one third more.

## Status of the inputs

We use published data where we found them, and we label every other input as a planning assumption: the share of primary-care visits that the stakeholders assign to the mobile clinics (15 percent), the capacity of one van (291 visits per month), the cost of one van ($81,758 per month) and the five service days of each van. We treat the towns as illustrative service communities and the 2030 values as planning scenarios, not local forecasts.

## Note on the check

We wrote `recompute_from_records.py` separately from `screening.py`. We regard the agreement of the two scripts as an internal check by the authors, not as a test with independent analysts.

## License

We release the code and data under the MIT License (see `LICENSE`).
