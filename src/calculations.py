import pandas as pd
from fetch import (
    fetch_bank_rate, load_bank_rate,
    fetch_cpi, fetch_wage_growth, fetch_unemployment,
    load_ons_monthly_series,
)


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
    print(df.tail(10))
    print(f"\nTotal rows: {len(df)}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")