import pandas as pd

# Maps friendly names the model can use to actual column names in our data.
INDICATORS = {
    "cpi_inflation": "cpi_inflation_rate",
    "bank_rate": "bank_rate",
    "wage_growth": "wage_growth_rate",
    "real_wage_growth": "real_wage_growth",
    "unemployment": "unemployment_rate",
    "real_interest_rate": "real_interest_rate",
    "taylor_rule_rate": "taylor_rule_rate",
}


def _filter(df, indicator, start_date=None, end_date=None):
    """Shared helper: picks one indicator and an optional date range."""
    column = INDICATORS[indicator]
    subset = df[["date", column]].dropna()
    if start_date:
        subset = subset[subset["date"] >= pd.to_datetime(start_date)]
    if end_date:
        subset = subset[subset["date"] <= pd.to_datetime(end_date)]
    return subset, column


def get_latest_value(df, indicator):
    """Returns the most recent available value for an indicator."""
    subset, column = _filter(df, indicator)
    if subset.empty:
        return {"error": f"No data available for {indicator}"}
    row = subset.iloc[-1]
    return {
        "indicator": indicator,
        "value": round(float(row[column]), 2),
        "date": row["date"].strftime("%B %Y"),
    }


def find_extreme(df, indicator, mode="max", start_date=None, end_date=None):
    """Finds the highest or lowest value of an indicator in a period."""
    subset, column = _filter(df, indicator, start_date, end_date)
    if subset.empty:
        return {"error": f"No data for {indicator} in that period"}
    row = subset.loc[subset[column].idxmax() if mode == "max" else subset[column].idxmin()]
    return {
        "indicator": indicator,
        "mode": mode,
        "value": round(float(row[column]), 2),
        "date": row["date"].strftime("%B %Y"),
    }


def compare_periods(df, indicator, start_date, end_date):
    """Compares an indicator's value at the start and end of a period."""
    subset, column = _filter(df, indicator, start_date, end_date)
    if len(subset) < 2:
        return {"error": f"Not enough data for {indicator} in that period"}
    first, last = subset.iloc[0], subset.iloc[-1]
    return {
        "indicator": indicator,
        "start_date": first["date"].strftime("%B %Y"),
        "start_value": round(float(first[column]), 2),
        "end_date": last["date"].strftime("%B %Y"),
        "end_value": round(float(last[column]), 2),
        "change": round(float(last[column] - first[column]), 2),
    }


def summarise_period(df, indicator, start_date=None, end_date=None):
    """Returns summary statistics for an indicator over a period."""
    subset, column = _filter(df, indicator, start_date, end_date)
    if subset.empty:
        return {"error": f"No data for {indicator} in that period"}
    values = subset[column]
    return {
        "indicator": indicator,
        "average": round(float(values.mean()), 2),
        "minimum": round(float(values.min()), 2),
        "maximum": round(float(values.max()), 2),
        "months_covered": len(values),
        "first_month": subset.iloc[0]["date"].strftime("%B %Y"),
        "last_month": subset.iloc[-1]["date"].strftime("%B %Y"),
    }
if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent))
    from calculations import build_merged_dataset, add_derived_metrics

    df = add_derived_metrics(build_merged_dataset())

    print(get_latest_value(df, "cpi_inflation"))
    print(find_extreme(df, "cpi_inflation", mode="max", start_date="2019-01-01"))
    print(compare_periods(df, "real_wage_growth", "2021-01-01", "2026-08-31"))
    print(summarise_period(df, "unemployment", start_date="2020-01-01", end_date="2021-12-31"))