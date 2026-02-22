import os
import json
from dotenv import load_dotenv
from groq import Groq

SYSTEM_PROMPT = """\
You are an expert trading coach and quantitative performance analyst. You will be 
given a JSON object containing a trader's statistical analysis data. Your job is to 
analyze this data deeply and produce a comprehensive, insightful report that helps 
the trader genuinely understand their performance and improve.

## STRICT DATA RULES — DO NOT VIOLATE
1. You must ONLY use values present in the JSON. Never invent, estimate, or 
   recalculate any number.
2. Every claim you make must be traceable to a specific value in the JSON.
3. If a segment has a trade count of 5 or fewer, you MUST flag it with ⚠️ and 
   note: "Low sample size — interpret with caution."
4. If `profit_factor` is `null`, interpret it as: "Profit factor is undefined 
   (no losing trades recorded), indicating a perfect win streak in this segment."
5. Do NOT fabricate new metrics or percentages not present in the JSON.

## ANALYSIS RULES
6. Do NOT simply restate or repeat numbers. Every statistic you mention MUST be 
   followed by an interpretation.
7. Cross-reference segments where relevant.
8. Write as a knowledgeable but friendly mentor speaking to a beginner or 
   intermediate trader.
"""


def build_prompt(analytics_json: dict) -> str:
    json_str = json.dumps(analytics_json, indent=2, default=str)
    return (
        "Below is the complete analytics JSON produced by a deterministic trading "
        "analytics engine. Interpret these results and produce a professional "
        "trading performance report.\n\n"
        "```json\n"
        f"{json_str}\n"
        "```"
    )


def generate_report(
    analytics_json: dict,
    model: str = "llama-3.3-70b-versatile",
    temperature: float = 0.3,
    max_tokens: int = 3000,
) -> str:
    load_dotenv()

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        raise ValueError("GROQ_API_KEY is not set in .env file.")

    client = Groq(api_key=api_key)

    chat_completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_prompt(analytics_json)},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )

    return chat_completion.choices[0].message.content