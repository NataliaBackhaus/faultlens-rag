def classify(element) -> str:
    if element.type == "table":
        return "table"
    elif element.type == "figure":
        return "figure"
    elif element.type == "text" or element.type == "heading":
        if element.text.startswith(("DANGER", "WARNING", "CAUTION", "NOTE")):
            return "safety"
        else:
            return "prose"
    else:
        return "prose"
