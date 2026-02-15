"""Parse forctx query string into tag tokens and content phrases."""

import re


def parse_forctx_query(query: str) -> tuple[list[str], list[str]]:
    """Parse query into (tag_tokens, content_phrases).

    - [#text] -> tag (text = single token, no spaces in v1)
    - [text] -> content phrase (text can contain spaces)
    - Bare words after extraction -> single-word content phrases
    """
    query = (query or "").strip()
    content_phrases: list[str] = []
    remainder = query

    # Extract all [ ... ] segments (content phrases)
    bracket_re = re.compile(r"\[([^\]]*)\]")
    for match in bracket_re.finditer(query):
        content_phrases.append(match.group(1).strip())
    remainder = bracket_re.sub(" ", query)

    # Split remainder by spaces; #tokens -> tags, rest -> bare words (content)
    tag_tokens: list[str] = []
    bare: list[str] = []
    for token in remainder.split():
        token = token.strip()
        if not token:
            continue
        if token.startswith("#"):
            tag_tokens.append(token[1:].strip())
        else:
            bare.append(token)

    content_phrases.extend(bare)
    return (tag_tokens, content_phrases)
