import json
from pathlib import Path

SYSTEM = (
    "You are a technical assistant for solar inverter installers. "
    "Answer using ONLY the passages provided. "
    "If the answer is not in the passages, say so. "
    "Never invent error codes, values or procedures. "
    "Respond in Json only, no extra text."
)

JSON_SCHEMA = """
{
    "diagnosis": "one sentence explaining what is happening",
    "causes": ["cause 1", "cause 2"],
    "steps": ["step 1", "step 2"],
    "safety": ["safety warning 1"],
    "citations": ["[1] doc_id p.X", "[2] doc_id p.Y"]
}
"""


def build_prompt(query: str, passages: list[dict]) -> str:
    ordered = sorted(
        passages,
        key=lambda p: 0 if any(w in p["text"] for w in ("WARNING", "DANGER", "CAUTION")) else 1,
    )

    lines = []
    for i, p in enumerate(ordered, 1):
        lines.append(f"[{i}] {p['doc_id']} p.{p['page']} - {p['text']}")

    passages_block = "\n\n".join(lines)

    return (
        f"{SYSTEM}\n\n"
        f"Passages:\n{passages_block}\n\n"
        f"Question: {query}\n\n"
        f"Respond with this exact JSON structure:\n{JSON_SCHEMA}"
    )


def generate_answer(client, query: str, passages: list[dict]) -> dict:
    prompt = build_prompt(query, passages)
    images = []
    for p in passages:
        if p["record_type"] == "figure":
            fig_name = f"{p['page']:04d}_{int(p['bbox'][0]):04d}.png"
            png_path = Path("data/figures") / p["doc_id"] / fig_name
            if png_path.exists():
                images.append(png_path)

    try:
        response = client.generate(prompt, images=images if images else None)
    except Exception:
        response = client.generate(prompt)

    if response.startswith("```"):
        response = response.split("```")[1]
        if response.startswith("json"):
            response = response[4:]

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return {"diagnosis": response, "causes": [], "steps": [], "safety": [], "citations": []}
