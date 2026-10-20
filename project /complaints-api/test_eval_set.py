from documents import DOCUMENTS
from eval_set import EVAL_SET, answerable
from eval_tools import contains_evidence, keywords_present, normalise

ALL_DOCS = {d["id"]: d for d in DOCUMENTS}


# Each evaluation question must have a unique ID.
def test_ids_are_unique():
    ids = [q["id"] for q in EVAL_SET]
    duplicates = {id for id in ids if ids.count(id) > 1}

    assert not duplicates, f"Duplicate ids found: {duplicates}"

# Each expected evidence passage must exist in its source document.
def test_every_evidence_span_is_in_its_document():
    for q in answerable():
        assert contains_evidence(ALL_DOCS[q["doc_id"]]["body"], q["evidence"],), q["id"]

# Each evidence passage should appear only once across the documents.
def test_every_evidence_span_appears_exactly_once_in_the_whole_document():
    for q in answerable():
        total = sum(normalise(d["body"]).count(normalise(q["evidence"])) for d in ALL_DOCS.values())
        assert total == 1, f"{q['id']} evidence appears {total} times"

# Match complete terms and alternatives, but never score refusals as correct.
def test_keyword_matching_is_whole_word_and_refusal_aware():
    assert keywords_present("The payment was posted two days later [doc-007].",["two|2", "days"])
    assert not keywords_present("The provided documents do not contain enough information to answer this question.",["not|no"])
    assert not keywords_present("The delay was 12 days.", ["2"])
    assert keywords_present("Investigate the communication failure [doc-002].",["investigat*"])
    assert keywords_present("Check the due date and bank receipt date [doc-004].",["due date", "bank receipt date"])
    assert not keywords_present("Check the due date [doc-004].",["due date", "bank receipt date"])