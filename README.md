# UK Economic Conditions Dashboard

An interactive dashboard tracking UK inflation, wages, unemployment and interest rates, using live data from the Office for National Statistics and the Bank of England, with AI-generated analysis grounded in verified figures.

Built with Python, pandas, Streamlit, Plotly and the Claude API.

## What it does

The dashboard tracks five core indicators: CPI inflation, Bank Rate, wage growth, real wage growth and unemployment, all updated from official sources.

It also calculates several metrics that are not published directly, including real interest rates, a simplified Taylor Rule estimate, the distance between current inflation and the Bank of England's 2% target, and where current readings sit relative to their own historical range.

Two AI features sit on top of this. The first produces a written summary of recent changes. The second answers natural language questions such as "when was inflation highest since 2019?" or "has wage growth kept up with inflation since 2021?"

## The core design decision

The AI never does arithmetic.

Large language models are unreliable at numerical work. They tend to produce plausible sounding figures rather than calculated ones, which is a serious problem for anything presenting itself as economic analysis. This project is built so that cannot happen.

All calculations happen in Python, in `src/calculations.py`, where they are transparent and testable. The AI receives finished figures and is asked only to explain them.

For the question answering feature, the AI uses tool calling. It chooses which Python function to run, that function computes the answer from the dataset, and the AI then explains the result. At no point does it retrieve a number from its own memory.

The AI is permitted to add historical context from general knowledge, for instance the causes of the 2022 inflation spike, but it is required to label this explicitly as context rather than data.

This separation is the point of the project rather than an implementation detail.

## Data sources

| Indicator | Source | Series |
|---|---|---|
| CPI inflation | ONS | D7G7 (MM23) |
| Wage growth | ONS | KAC3 (LMS) |
| Unemployment | ONS | MGSX (LMS) |
| Bank Rate | Bank of England | IUMABEDR (IADB) |

All data is published under the Open Government Licence v3.0. Full notes on endpoints, quirks and methodology decisions are in `DATA_SOURCES.md`.

## Notable data handling

The ONS time series export stacks annual, quarterly and monthly figures in a single column, distinguished only by the format of the row label. These are filtered down to monthly observations using a pattern match.

Indicators publish at different speeds. Unemployment lags furthest behind because it comes from the Labour Force Survey, while CPI and Bank Rate are more current. Rather than truncating every series back to the slowest one, each indicator displays its own latest available month and charts simply end where their data does.

Cleaned data is cached locally in `data/processed/` and only re-fetched on request. This avoids rate limiting from the source APIs and keeps the dashboard fast and available even when a government server is temporarily down.

## Project structure

```
├── app.py                 Streamlit dashboard, UI only
├── src/
│   ├── fetch.py           Data retrieval from ONS and BoE
│   ├── calculations.py    Merging and derived metrics, no AI involved
│   ├── ai_explain.py      Written summary of recent changes
│   ├── ai_tools.py        Python functions the AI is able to call
│   └── ai_qa.py           Tool calling loop for natural language questions
├── data/
│   ├── raw/               Untouched source files, exactly as downloaded
│   └── processed/         Cleaned, merged dataset
├── DATA_SOURCES.md        Source documentation and methodology decisions
└── requirements.txt
```

Raw files are kept unmodified so that any cleaning step can be independently verified against the original source.

## Running it locally

```bash
git clone https://github.com/noahlaing0-sketch/uk-economic-dashboard.git
cd uk-economic-dashboard

python -m venv venv
venv\Scripts\Activate        # Windows
source venv/bin/activate     # macOS and Linux

pip install -r requirements.txt
```

Create a `.env` file in the project root containing your API key:

```
ANTHROPIC_API_KEY=your-key-here
```

Then run:

```bash
streamlit run app.py
```

## Limitations

The Taylor Rule implementation is simplified. The standard formula uses an output gap, and since GDP is not included in this project, unemployment's deviation from its dataset average is used as a rough proxy for economic slack. It is labelled as simplified wherever it appears.

Coverage begins in January 2015.

All figures are aggregate national statistics, so they do not reflect variation across sectors, regions or income groups.

GDP is not currently included.

## Possible extensions

Exchange rates, GDP growth, anomaly detection, correlation analysis between unemployment and inflation, international comparisons, and statistical trend projection with AI-narrated caveats.