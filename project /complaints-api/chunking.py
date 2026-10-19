"""Split banking documents into chunks for retrieval.

A chunk is a dict:

    - id       "<doc id>#<two-digit-numbers>, kept stable for the same input
    - doc_id   the parent document, used for citations
    - title    the parent documents title
    - text     exactly what gets embedded and what the model will read

"""

import re


# Give each chunk an ID and retain its source document for citations.
def _chunk(doc: dict, number: int, text: str) -> dict:
    return {
        "id": f"{doc['id']}#{number:02d}",
        "doc_id": doc["id"],
        "title": doc["title"],
        "text": text,
    }

# Split document text into sentences, keeping section headings together.
def split_sentences(text: str) -> list[str]:
    units = []

    for line in text.splitlines():
        line = line.strip(" -*\t")

        if line:
            if line.startswith("## "):
                units.append(line)
            else:
                units.extend(
                    s for s in re.split(r"(?<=[.?!])\s+", line) if s)

    return units

# Group whole sentences without splitting them across chunks.
def pack(units: list[str], max_words: int) -> list[str]:
    groups, current, count = [], [], 0

    for unit in units:
        n = len(unit.split())

        if current and count + n > max_words:
            groups.append(" ".join(current))
            current, count = [], 0

        current.append(unit)
        count += n

    if current:
        groups.append(" ".join(current))

    return groups

# ------------------------CHUNKING STRATEGIES--------------------------------------

# whole document 
def whole_document(doc: dict) -> list[dict]:
    return [_chunk(doc, 0, doc["body"].strip())]

# Split documents by word count, optionally repeating boundary words.
def fixed_words(
    doc: dict, size: int = 100, overlap: int = 0) -> list[dict]:
    if not 0 <= overlap < size:
        raise ValueError("overlap must be at least 0 and smaller than size")

    words = doc["body"].strip().split()
    step = size - overlap
    chunks = []

    for number, start in enumerate(range(0, len(words), step)):
        chunks.append(
            _chunk(doc, number, " ".join(words[start:start + size])))

        if start + size >= len(words):
            break

    return chunks

# Build chunks from whole sentences using a target word count.
def sentences_packed(doc: dict, size: int = 100) -> list[dict]:
    units = split_sentences(doc["body"])
    packed = pack(units, size)
    chunks = []

    for number, text in enumerate(packed):
        chunks.append(_chunk(doc, number, text))

    return chunks

# Split by section, optionally adding the document title and heading.
def by_section(
    doc: dict, max_words: int = 150, contextual: bool = True) -> list[dict]:
    chunks, number = [], 0
    has_sections = "## " in doc["body"]

    parts = (re.split(r"(?m)^## ", doc["body"]) if has_sections else [doc["body"]])

    for part in parts:
        heading, _, text = (part.partition("\n") if has_sections else ("", "", part))
        heading, text = heading.strip(), text.strip()

        if not text:
            continue
        for piece in pack(split_sentences(text), max_words):
            if contextual:
                prefix = (f"{doc['title']} > {heading}\n" if heading else f"{doc['title']}\n")
                piece = prefix + piece
            chunks.append(_chunk(doc, number, piece))
            number += 1
    return chunks

STRATEGIES = {
    "whole_document": whole_document,
    "fixed_100": lambda d: fixed_words(d, size=100, overlap=0),
    "fixed_overlap_25": lambda d: fixed_words(d, size=100, overlap=25),
    "sentences_100": lambda d: sentences_packed(d, size=100),
    "sections_plain": lambda d: by_section(d, max_words=150, contextual=False),
    "sections_contextual": lambda d: by_section(d, max_words=150, contextual=True),
}

def chunk_corpus(docs: list[dict], strategy: str) -> list[dict]:
    return [chunk for doc in docs for chunk in STRATEGIES[strategy](doc)]