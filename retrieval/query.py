import json
import re

from ingest.aliases import load_aliases, resolve

ERROR_CODE_PATTERN = re.compile(
    r"\b(?:event|error|fault|code|E)[\s\-]?(\d+)\b",
    re.IGNORECASE,
)


def extract_with_regex(text: str) -> dict:
    result = {
        "error_code": None,
        "model": None,
        "source": "regex",
    }

    match = ERROR_CODE_PATTERN.search(text)
    if match:
        result["error_code"] = match.group(1)

    aliases = load_aliases()
    words = text.split()
    model = None

    for size in (3, 2, 1):
        for i in range(len(words) - size + 1):
            candidate = " ".join(words[i : i + size])
            res = resolve(candidate, aliases)
            if res:
                model = res
                break
        if model:
            break

    if model:
        result["model"] = model

    return result


def extract_with_llm(text: str, llm) -> dict:
    prompt = f"""Extract the inverter model and error code from this installer query.
    Return ONLY a JSON object with these fields:
    - error_code: string or null (e.g. "34", "E34")
    - model: string or null (e.g. "SB 2500HF", "Symo 10.0")

    Query: {text}"""

    response = llm.generate(prompt)
    match = re.search(r"\{.*\}", response, re.DOTALL)
    if match:
        result = json.loads(match.group())
        result["source"] = "llm"
        return result

    return {}


def parse_query(text: str, llm=None) -> dict:
    result = extract_with_regex(text)
    if llm and not (result["error_code"] and result["model"]):
        result = extract_with_llm(text, llm)

    if not result.get("model"):
        result["clarification"] = (
            "Which inverter model are you asking about? (e.g. SB 2500HF, Symo 10.0)"
        )
    else:
        result["clarification"] = None

    return result
