"""
Small, pure helpers for scoring. No network and no model.
"""

import re

from grounding import is_refusal, normalise # one definition of refusal

def contains_evidence(chunk_text: str, evidence: str) -> bool:
    """ True if the chunk holds the whole evidence span. line breaks never break a match."""
    return normalise(evidence) in normalise(chunk_text)

# alternative matches
def alternative_matches(answer: str, alternative: str) -> bool:
    prefix = alternative.endswith("*")
    core = re.escape(alternative.rstrip("*").lower())
    ending = "" if prefix else r"(?![a-z0-9])"
    return re.search(rf"(?<![a-z0-9]){core}{ending}", answer.lower()) is not None

# keywords_present
# Examples from our banking evaluation questions:
# q09 (mortgage payment dates): ["due date", "bank receipt date", "account posting date"]
# The answer must mention all three dates.
#
# q20 (payment posting delay): ["two|2", "days"]
# The answer must mention either "two" or "2", and also "days".
#
# q04 (accessible format failure): ["replace*", "investigat*"]
# The answer must include words starting with "replace" and "investigat".
def keywords_present(answer: str | None, keywords: list[str]) -> bool:
    """True only for a non-refusal answer containing every keyword group."""

    if is_refusal(answer):
        return False

    return all(
        any(alternative_matches(answer, alt) for alt in group.split("|"))
        for group in keywords
    )
