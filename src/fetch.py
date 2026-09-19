import requests
import pandas as pd
from pathlib import Path

import re
def load_cpi(path="data/raw/cpi_raw.csv"):
    """
    Loads the raw ONS CPI file and extracts only the monthly figures,
    discarding the annual and quarterly rows mixed into the same file.
    """
    df = pd.read_csv(path, header=None, names=["label", "value"])

    # Keep only rows shaped like "2025 DEC" (year, space, 3-letter month)
    monthly_pattern = re.compile(r"^\d{4} [A-Z]{3}$")
    df = df[df["label"].astype(str).str.match(monthly_pattern)].copy()

    # Split "2025 DEC" into a year and a month, then build a real date
    parts = df["label"].str.split(" ", expand=True)
    year = parts[0]
    month = parts[1].str.capitalize()  # "DEC" -> "Dec", which pandas' date parser expects
    df["date"] = pd.to_datetime(year + " " + month, format="%Y %b") + pd.offsets.MonthEnd(0)

    df = df.rename(columns={"value": "cpi_inflation_rate"})
    df["cpi_inflation_rate"] = df["cpi_inflation_rate"].astype(float)
    df = df[["date", "cpi_inflation_rate"]].sort_values("date").reset_index(drop=True)

    return df

def fetch_bank_rate(date_from="01/Jan/2015", date_to="now"):
    """
    Downloads the monthly average Bank of England Bank Rate
    from the Bank of England's statistical database (IADB).
    Series code IUMABEDR = Monthly average of official Bank Rate.
    """
    url = "https://www.bankofengland.co.uk/boeapps/database/_iadb-fromshowcolumns.asp"
    params = {
        "csv.x": "yes",
        "Datefrom": date_from,
        "Dateto": date_to,
        "SeriesCodes": "IUMABEDR",
        "CSVF": "TN",
        "UsingCodes": "Y",
        "VPD": "Y",
        "VFD": "N",
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()

    raw_path = Path("data/raw/bank_rate_raw.csv")
    raw_path.write_text(response.text)

    return raw_path
def load_bank_rate(path="data/raw/bank_rate_raw.csv"):
    """
    Loads the raw Bank Rate CSV into a pandas DataFrame with proper column names and types.
    """
    df = pd.read_csv(path, header=0, names=["date", "bank_rate"])
    df["date"] = pd.to_datetime(df["date"], format="%d %b %Y")
    return df
def fetch_cpi(series_id="d7g7", dataset_id="mm23"):
    """
    Downloads the headline UK CPI annual inflation rate (%) from the ONS.
    Series D7G7 in dataset MM23 = CPI Annual Rate, All Items, 2015=100.
    """
    url = "https://www.ons.gov.uk/generator"
    params = {
        "format": "csv",
        "uri": f"/economy/inflationandpriceindices/timeseries/{series_id}/{dataset_id}",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()

    raw_path = Path("data/raw/cpi_raw.csv")
    raw_path.write_bytes(response.content)

    return raw_path
if __name__ == "__main__":
    path = fetch_bank_rate()
    print(f"Saved Bank Rate data to: {path}")

    df = load_bank_rate(path)
    print(df.head())
    print(df.tail())
if __name__ == "__main__":
    bank_rate_path = fetch_bank_rate()
    print(f"Saved Bank Rate data to: {bank_rate_path}")
    df = load_bank_rate(bank_rate_path)
    print(df.head())
    print(df.tail())

    cpi_path = fetch_cpi()
    print(f"\nSaved CPI data to: {cpi_path}")
if __name__ == "__main__":
    bank_rate_path = fetch_bank_rate()
    print(f"Saved Bank Rate data to: {bank_rate_path}")
    bank_rate_df = load_bank_rate(bank_rate_path)
    print(bank_rate_df.tail())

    cpi_path = fetch_cpi()
    print(f"\nSaved CPI data to: {cpi_path}")
    cpi_df = load_cpi(cpi_path)
    print(cpi_df.tail())