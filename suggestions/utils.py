import json


def format_suggestions_for_display(suggestions: dict) -> str:
    """
    Returns a human-readable string for blog suggestions.
    """
    titles = "\n".join(f"- {t}" for t in suggestions.get("titles", []))
    meta = suggestions.get("meta_description", "")
    slug = suggestions.get("slug", "")
    keywords = ", ".join(suggestions.get("keywords", []))

    return (
        f"Titles:\n{titles}\n\n"
        f"Meta description: {meta}\n"
        f"Slug: {slug}\n"
        f"Keywords: {keywords}"
    )


def to_json(suggestions: dict) -> str:
    """Convert suggestions dict to pretty JSON string."""
    return json.dumps(suggestions, indent=2, ensure_ascii=False)
