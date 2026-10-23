import chunking
from documents import DOCUMENTS
import pytest

DOC = next(d for d in DOCUMENTS if d["id"] == "doc-004")


# Splitting without overlap must preserve all words in order
def test_fixed_chunks_without_overlap_lose_no_words():
    chunks = chunking.fixed_words(DOC, size=100, overlap=0)
    rebuilt = " ".join(c["text"] for c in chunks).split()

    assert rebuilt == DOC["body"].split()

def test_overlap_repeats_exactly_the_overlap_words():
    chunks = chunking.fixed_words(DOC, size=100, overlap=25)

    for first, second in zip(chunks, chunks[1:]):
        assert first["text"].split()[-25:] == second["text"].split()[:25]

# test the overlap must be smaller than size
def test_overlap_must_be_smaller_than_size():
    with pytest.raises(ValueError):
        chunking.fixed_words(DOC, size=100, overlap=100)

# test sentence packing never cuts a sentence

def test_sentence_packing_never_cuts_a_sentence():
    # this splits the document into sentences and headings
    units = chunking.split_sentences(DOC["body"])
    # joins the units into groups, each group having at most 100 words
    chunks = chunking.pack(units, max_words=100)

    for sentence in units:
        found = False
        # Look for a chunk containing the whole sentence.
        for chunk in chunks:
            if sentence in chunk:
                found = True
                break
        # Fail if the complete sentence was not found.
        assert found, f"Sentence missing or cut: {sentence}"

# Contextual chunks must carry the banking document's title.
def test_contextual_sections_carry_title():
    chunks = chunking.by_section(DOC, contextual=True)
    for chunk in chunks:
        text = chunk["text"]

        assert text.startswith(DOC["title"] + " > ")
        heading = text.split("\n")[0].split(" > ", 1)[1]
        assert heading
        assert f"## {heading}" in DOC["body"]

# Plain chunks must not have the document title added as a prefix.
def test_plain_sections_carry_no_heading():
    assert not any("> " in c["text"] for c in chunking.by_section(DOC, contextual=False)) 