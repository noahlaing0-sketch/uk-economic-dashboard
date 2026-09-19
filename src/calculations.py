from pathlib import Path
import pandas as pd
from fetch import (
    fetch_bank_rate, load_bank_rate,
    fetch_cpi, fetch_wage_growth, fetch_unemployment,
    load_ons_monthly_series,
)


def add_derived_metrics(df):
    """
    Adds calculated economic metrics to the merged dataset:
    - real_wage_growth: wage growth adjusted for inflation
    - real_interest_rate: Bank Rate adjusted for inflation
    - taylor_rule_rate: a simple Taylor Rule estimate of the "appropriate" rate
    """
    df = df.copy()

    # Real wage growth = nominal wage growth minus inflation.
    # If wages grow 4% and prices grow 3%, people are only ~1% better off in real terms.
    df["real_wage_growth"] = df["wage_growth_rate"] - df["cpi_inflation_rate"]

    # Real interest rate = Bank Rate minus inflation.
    # A 4% Bank Rate with 3% inflation is only mildly restrictive in real terms;
    # the same 4% rate with 1% inflation is much more restrictive.
    df["real_interest_rate"] = df["bank_rate"] - df["cpi_inflation_rate"]

    # A simple Taylor Rule:
    #   suggested rate = neutral rate + inflation
    #                     + 0.5 * (inflation - target)
    #                     + 0.5 * (output gap)
    # We don't have a real "output gap" measure in this project, so as a
    # simplification we treat the DEVIATION of unemployment from its own
    # long-run average in our dataset as a rough stand-in. This is a
    # simplification of the real Taylor Rule, not the textbook version,
    # and we say so clearly in the dashboard.
    neutral_rate = 2.0
    inflation_target = 2.0
    average_unemployment = df["unemployment_rate"].mean()

    df["taylor_rule_rate"] = (
        neutral_rate
        + df["cpi_inflation_rate"]
        + 0.5 * (df["cpi_inflation_rate"] - inflation_target)
        - 0.5 * (df["unemployment_rate"] - average_unemployment)
    )

    # How far current inflation is from the Bank of England's 2% target.
    df["distance_from_target"] = df["cpi_inflation_rate"] - inflation_target

    # What percentile the current month's inflation sits at, relative to
    # all inflation readings in our dataset (0 = lowest, 100 = highest).
    df["cpi_percentile"] = df["cpi_inflation_rate"].rank(pct=True) * 100

    return df


PROCESSED_PATH = Path("data/processed/merged_dataset.csv")


def build_merged_dataset(force_refresh=False):
    """
    Returns the merged dataset. Reads from the local processed file if it
    exists, and only re-fetches from ONS/BoE when explicitly asked or when
    no local copy exists. This avoids hammering the source APIs (which
    rate-limit) and keeps the dashboard fast and reliable.
    """
    if PROCESSED_PATH.exists() and not force_refresh:
        return pd.read_csv(PROCESSED_PATH, parse_dates=["date"])

    bank_rate_df = load_bank_rate(fetch_bank_rate())
    cpi_df = load_ons_monthly_series(fetch_cpi(), "cpi_inflation_rate")
    wage_df = load_ons_monthly_series(fetch_wage_growth(), "wage_growth_rate")
    unemployment_df = load_ons_monthly_series(fetch_unemployment(), "unemployment_rate")

    # "outer" keeps every month any indicator has data for, leaving gaps (NaN)
    # where a slower-publishing series hasn't caught up yet. Unemployment in
    # particular lags, since it comes from the Labour Force Survey.
    merged = cpi_df.merge(bank_rate_df, on="date", how="outer")
    merged = merged.merge(wage_df, on="date", how="outer")
    merged = merged.merge(unemployment_df, on="date", how="outer")

    # Trim to 2015 onwards — matches our Bank Rate fetch window and keeps the
    # dashboard focused on the recent, relevant period.
    merged = merged[merged["date"] >= "2015-01-01"]
    merged = merged.sort_values("date").reset_index(drop=True)

    # Save a clean copy so future runs don't need to re-fetch.
    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(PROCESSED_PATH, index=False)

    return merged

if __name__ == "__main__":
    df = build_merged_dataset()
    df = add_derived_metrics(df)

    print(df[["date", "cpi_inflation_rate", "bank_rate", "wage_growth_rate",
              "unemployment_rate", "taylor_rule_rate"]].tail(8))
    print(f"\nTotal rows: {len(df)}")