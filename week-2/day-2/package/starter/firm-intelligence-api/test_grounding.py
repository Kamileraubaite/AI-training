import grounding

SOURCES = {
    "doc-101": "Harding & Voss closed the year with revenue of $1.24 billion, up 1.4 percent.",
    "doc-107": "Fixed-share partners are excluded from the equity partner count.",
}

# failure 1 - ungrounded claims
# test that refusal needs not citations

def test_refusal_needs_no_citations():
    report = grounding.check_citations(grounding.REFUSAL_SENTENCE, ["doc-101"])
    assert report["refusal"] is True and report["passed"] is True

# test fully cited answer passes
def test_fully_cited_answer_passes():
    answer = (
        "Harding & Voss reported revenue of $1.24 billion [doc-101]. "
        "Fixed-share partners are excluded from the equity partner count [doc-107]."
    )
    report = grounding.check_citations(answer, ["doc-101", "doc-107"])
    assert report["refusal"] is False
    assert report["cited"] == ["doc-101", "doc-107"]
    assert report["invalid"] == []
    assert report["uncited_sentences"] == []
    assert report["passed"] is True

# test uncited sentence is flagged
def test_uncited_sentence_is_flagged():
    answer = (
        "Harding & Voss reported revenue of $1.24 billion. "
    )
    report = grounding.check_citations(answer, ["doc-101"])
    assert report["uncited_sentences"] is not None
    assert report["passed"] is False

# test citation after the full stop still counts
def test_citation_after_full_stop_counts():
    answer = "Harding & Voss reported revenue of $1.24 billion. [doc-101]"
    report = grounding.check_citations(answer, ["doc-101"])
    assert report["uncited_sentences"] == []
    assert report["passed"] is True
