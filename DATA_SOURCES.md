Data Sources

## Bank Rate — Bank of England
- **Source:** Bank of England Interactive Statistical Database (IADB)
- **Series code:** IUMABEDR (Monthly average of official Bank Rate)
- **Endpoint used:** `_iadb-fromshowcolumns.asp` (not `fromshowcolumns.asp`, which returns
  an HTML page instead of raw CSV)
- **Notes:** Requires a browser-like User-Agent header, or the server returns 403 Forbidden.


## CPI Inflation — Office for National Statistics (ONS)
- **Source:** ONS time series download tool
- **Series code:** D7G7 (CPI Annual Rate, All Items, 2015=100)
- **Dataset:** MM23 (Consumer Price Inflation time series dataset)
- **Endpoint used:** `https://www.ons.gov.uk/generator?format=csv&uri=/economy/inflationandpriceindices/timeseries/{series}/{dataset}`
- **Notes:** The raw file mixes annual, quarterly, and monthly figures in one column,
  distinguished only by label format (e.g. "2026", "2026 Q2", "2026 AUG"). We filter to
  monthly rows only using a regex pattern on the label column.


## Known issues / decisions
- I used **CPI** (not CPIH) as the headline inflation measure, matching the Bank of
  England's 2% target and general public usage of "inflation."
- The ONS's newer `api.beta.ons.gov.uk` dataset API (used for CPIH) stopped updating in
  January 2026, per a notice on their own site, I deliberately used the older but
  actively-maintained `generator` CSV tool instead, which is confirmed live and current
  as of September 2026.

  Calculated metrics (derived, not fetched)

These are computed in `calculations.py` from the four fetched indicators above —
not pulled from any external source.

- **Real wage growth** = wage growth rate − CPI inflation rate.
- **Real interest rate** = Bank Rate − CPI inflation rate.
- **Taylor Rule rate (simplified)** — the standard Taylor Rule uses an "output gap"
  (how far GDP is from its potential), which is out of scope for this project since
  GDP wasn't included as a core indicator. As a substitute, we use unemployment's
  deviation from its own average across our dataset as a rough proxy for economic
  slack. This is a simplification of the textbook Taylor Rule, not the real thing,
  and should be described as such anywhere it's shown or discussed.
  - Assumed neutral real rate: 2.0%
  - Inflation target: 2.0% (matches the Bank of England's actual target)