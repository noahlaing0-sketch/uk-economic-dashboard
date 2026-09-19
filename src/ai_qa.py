import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

from ai_tools import (
    get_latest_value, find_extreme, compare_periods, summarise_period, INDICATORS
)

load_dotenv()
client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
MODEL = "claude-sonnet-5"

INDICATOR_LIST = list(INDICATORS.keys())

TOOLS = [
    {
        "name": "get_latest_value",
        "description": "Get the most recent available value for an economic indicator.",
        "input_schema": {
            "type": "object",
            "properties": {
                "indicator": {"type": "string", "enum": INDICATOR_LIST},
            },
            "required": ["indicator"],
        },
    },
    {
        "name": "find_extreme",
        "description": "Find the highest or lowest value of an indicator, optionally within a date range.",
        "input_schema": {
            "type": "object",
            "properties": {
                "indicator": {"type": "string", "enum": INDICATOR_LIST},
                "mode": {"type": "string", "enum": ["max", "min"]},
                "start_date": {"type": "string", "description": "YYYY-MM-DD, optional"},
                "end_date": {"type": "string", "description": "YYYY-MM-DD, optional"},
            },
            "required": ["indicator", "mode"],
        },
    },
    {
        "name": "compare_periods",
        "description": "Compare an indicator's value at the start and end of a date range, and the change between them.",
        "input_schema": {
            "type": "object",
            "properties": {
                "indicator": {"type": "string", "enum": INDICATOR_LIST},
                "start_date": {"type": "string", "description": "YYYY-MM-DD"},
                "end_date": {"type": "string", "description": "YYYY-MM-DD"},
            },
            "required": ["indicator", "start_date", "end_date"],
        },
    },
    {
        "name": "summarise_period",
        "description": "Get average, minimum and maximum for an indicator over a date range.",
        "input_schema": {
            "type": "object",
            "properties": {
                "indicator": {"type": "string", "enum": INDICATOR_LIST},
                "start_date": {"type": "string", "description": "YYYY-MM-DD, optional"},
                "end_date": {"type": "string", "description": "YYYY-MM-DD, optional"},
            },
            "required": ["indicator"],
        },
    },
]

FUNCTIONS = {
    "get_latest_value": get_latest_value,
    "find_extreme": find_extreme,
    "compare_periods": compare_periods,
    "summarise_period": summarise_period,
}

SYSTEM_PROMPT = """You answer questions about UK economic data for a dashboard.

You have tools that query a verified dataset covering January 2015 onwards. Data comes from the ONS (inflation, wages, unemployment) and the Bank of England (Bank Rate).

Rules on figures:
- ALWAYS use the tools to get figures. Never state a number from your own knowledge or memory.
- You may call multiple tools to answer one question.
- If a question needs data outside the available range (before 2015), say so clearly.

Rules on context and explanation:
- You may add historical or economic context from your general knowledge (e.g. known causes of a period of high inflation), but you MUST clearly label it as such — for example "For context, this period is generally attributed to..." or "This isn't from the data, but..."
- Never present general knowledge as if it came from the dataset.
- Keep the distinction visible: what the data shows, versus what may explain it.

Style:
- Be concise and write in plain English for a non-economist.
- Do not give investment advice or predict future values."""



def answer_question(df, question, max_turns=6):
    """
    Answers a question using tool calls. Claude decides which tools to use;
    all figures are computed in Python by those tools.
    """
    messages = [{"role": "user", "content": question}]

    for _ in range(max_turns):
        response = client.messages.create(
            model=MODEL,
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        if response.stop_reason != "tool_use":
            return "".join(
                block.text for block in response.content if block.type == "text"
            )

        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                function = FUNCTIONS[block.name]
                result = function(df, **block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result),
                })

        messages.append({"role": "user", "content": tool_results})

    return "I couldn't complete that question within the allowed number of steps."


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent))
    from calculations import build_merged_dataset, add_derived_metrics

    df = add_derived_metrics(build_merged_dataset())

    for q in [
        "When was inflation highest since 2019?",
        "Has wage growth kept up with inflation since 2021?",
    ]:
        print(f"\nQ: {q}")
        print(answer_question(df, q))