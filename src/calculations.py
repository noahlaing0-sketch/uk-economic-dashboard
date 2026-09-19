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
    # long-run average in our dataset as a rough stand-in: unemployment
    # above average suggests slack (weaker case for higher rates), and
    # unemployment below average suggests a tight economy (stronger case
    # for higher rates). This is a simplification of the real Taylor Rule,
    # not the textbook version, and we say so clearly in the dashboard.
    neutral_rate = 2.0  # a commonly cited assumption for the UK's long-run "neutral" real rate
    inflation_target = 2.0
    average_unemployment = df["unemployment_rate"].mean()

    df["taylor_rule_rate"] = (
        neutral_rate
        + df["cpi_inflation_rate"]
        + 0.5 * (df["cpi_inflation_rate"] - inflation_target)
        - 0.5 * (df["unemployment_rate"] - average_unemployment)
    )

    return df

def build_merged_dataset():
    """
    Fetches all four indicators and merges them into a single DataFrame,
    aligned by month.
    """
    bank_rate_df = load_bank_rate(fetch_bank_rate())
    cpi_df = load_ons_monthly_series(fetch_cpi(), "cpi_inflation_rate")
    wage_df = load_ons_monthly_series(fetch_wage_growth(), "wage_growth_rate")
    unemployment_df = load_ons_monthly_series(fetch_unemployment(), "unemployment_rate")

    # Start with CPI as the base, then join the others onto it by date.
    # "inner" join keeps only months where ALL four indicators have data.
    merged = cpi_df.merge(bank_rate_df, on="date", how="inner")
    merged = merged.merge(wage_df, on="date", how="inner")
    merged = merged.merge(unemployment_df, on="date", how="inner")

    return merged.sort_values("date").reset_index(drop=True)


if __name__ == "__main__":
    df = build_merged_dataset()
    df = add_derived_metrics(df)

    print(df[["date", "cpi_inflation_rate", "bank_rate", "real_interest_rate",
               "wage_growth_rate", "real_wage_growth", "taylor_rule_rate"]].tail(10))
    print(f"\nTotal rows: {len(df)}")