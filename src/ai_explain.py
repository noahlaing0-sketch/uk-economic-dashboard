import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

MODEL = "claude-sonnet-5"


def build_data_summary(df, months=12):
    """
    Builds a compact, factual summary of recent data to send to the model.
    Everything here is already computed in Python — the model receives
    finished numbers and is never asked to calculate anything itself.
    """
    recent = df.tail(months)

    lines = []
    for _, row in recent.iterrows():
        parts = [f"{row['date'].strftime('%b %Y')}:"]
        if row["cpi_inflation_rate"] == row["cpi_inflation_rate"]:  # not NaN
            parts.append(f"CPI inflation {row['cpi_inflation_rate']:.1f}%")
        if row["bank_rate"] == row["bank_rate"]:
            parts.append(f"Bank Rate {row['bank_rate']:.2f}%")
        if row["wage_growth_rate"] == row["wage_growth_rate"]:
            parts.append(f"wage growth {row['wage_growth_rate']:.1f}%")
        if row["real_wage_growth"] == row["real_wage_growth"]:
            parts.append(f"real wage growth {row['real_wage_growth']:.1f}%")
        if row["unemployment_rate"] == row["unemployment_rate"]:
            parts.append(f"unemployment {row['unemployment_rate']:.1f}%")
        if row["real_interest_rate"] == row["real_interest_rate"]:
            parts.append(f"real interest rate {row['real_interest_rate']:.2f}%")
        lines.append(" ".join(parts))

    return "\n".join(lines)


SYSTEM_PROMPT = """You are an economic analyst writing a short commentary for a UK economic dashboard.

You will be given verified UK economic data that has already been calculated. Your job is to explain what it shows.

Strict rules:
- Use ONLY the figures provided. Never state a number that is not in the data given to you.
- Never estimate, extrapolate, or recall figures from your own knowledge.
- Clearly separate OBSERVATIONS (what the data shows) from INTERPRETATION (why it might be happening). Mark interpretation with hedging language such as "this may reflect" or "one possible explanation".
- If the data is insufficient to support a claim, say so rather than speculating.
- Be concise: 3-4 short paragraphs maximum.
- Write in plain English for an interested non-economist. Avoid jargon; where a term is unavoidable, explain it briefly.
- Do not give investment advice or make predictions about future values."""


def explain_recent_changes(df, months=12):
    """
    Sends recent computed data to Claude and returns a written explanation.
    """
    data_summary = build_data_summary(df, months)

    message = client.messages.create(
        model=MODEL,
        max_tokens=800,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Here is the most recent {months} months of UK economic data:\n\n"
                    f"{data_summary}\n\n"
                    "Explain what has been happening in the UK economy over this period."
                ),
            }
        ],
    )

    return message.content[0].text


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent))
    from calculations import build_merged_dataset, add_derived_metrics

    df = add_derived_metrics(build_merged_dataset())
    print(explain_recent_changes(df))