import grounding

# failure 1 - ungrounded claims
# test that refusal needs not citations
def test_refusal_needs_no_citation():
    report = grounding.check_citations(grounding.REFUSAL_SENTENCE, ["doc-004"],)
    assert report["refusal"] is True and report["passed"] is True

# test fully cited answer passes
def test_fully_cited_answer_passes():
    answer = ("Staff must check the payment due date [doc-004]. "
              "Only authorised staff may approve nredress [doc-006]."
              )
    report = grounding.check_citations(answer, ["doc-004", "doc-006"])
    assert report["refusal"] is False 
    assert report["cited"] == ["doc-004", "doc-006"]
    assert report["invalid"] == []
    assert report["uncited_sentences"] == []
    assert report["passed"] is True

# test uncited is flagged 
def test_uncited_sentence_is_flagged():
    answer = (
        "Staff must check the payment due date."
    )
    report = grounding.check_citations(answer, ["doc-004"])
    assert report["uncited_sentences"] is not None
    assert report["passed"] is False

def test_citation_after_full_stop_counts():
    answer = "Staff must check the payment due date. [doc-004]"
    report = grounding.check_citations(answer, ["doc-004"])
    assert report["uncited_sentences"] == []
    assert report["passed"] is True
