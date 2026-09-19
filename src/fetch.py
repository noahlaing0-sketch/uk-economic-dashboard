import requests
import pandas as pd
from pathlib import Path

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
if __name__ == "__main__":
    path = fetch_bank_rate()
    print(f"Saved Bank Rate data to: {path}")

    df = load_bank_rate(path)
    print(df.head())
    print(df.tail())