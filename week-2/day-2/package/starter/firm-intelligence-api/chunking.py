import re 

"""
Chunking strategies
Every stategy takes a document and returns a list of chunks.

A chunk is a dict:

    - id       "<doc id>#<two-digit-numbers>, kept stable for the same input
    - doc_id   the parent document, used for citations
    - title    the parent documents title
    - text     exactly what gets embedded and what the model will read

"""

def _chunk(doc: dict, number: int, text:str) -> dict:
    # 2 -> 02
    # with padding - ['doc-105#01', 'doc-105#02', 'doc-105#10']
    # without padding - ['doc-105#01, doc-105#10', 'doc-105#2']
    return {
        "id": f"{doc['id']}#{number:02d}",
        "doc_id": doc["id"],
        "title": doc["title"],
        "text": text
    }

def split_sentences(text: str) -> list[str]:
    """Sentences, with each '## heading' line kept as a unit of its own
    """
    units = []
    for line in text.splitlines():
        line = line.strip(" -*\t")
        if line:
            if line.startswith("## "):
                units.append(line)
            else:
                units.extend(s for s in re.split(r"(?<=[.?!])\s+", line) if s)

    return units


def pack(units: list[str], max_words: int) -> list[str]:
    """Join whole units until adding the next one would pass max_words"""
    # groups holds finished chunks, current is the chunk being built, count is its word total
    groups, current, count = [],[], 0
    for unit in units:
        n =  len(unit.split())
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



# fixed words
def fixed_words(doc: dict, size: int = 100, overlap: int = 0) -> list[dict]:
    """Every 'size' words, regardless of sentence or sections. Cheap and blind"""
    if not 0 <= overlap < size:
        raise ValueError("overlap must be at least 0 and smaller than size")
    words = doc["body"].strip().split()
    step = size - overlap
    chunks = []

    # range(0, 385, 75)
    for number, start in enumerate(range(0, len(words), step)):
        chunks.append(_chunk(doc, number, " ".join(words[start:start + size])))
        if start + size >= len(words):
            break
    return chunks               
    
# Sentenced_packed
""" Whole sentences only, packed up to max_words. Never cuts a sentence in half. """
# Splits the document into chunks whilst still keeping sentences whole
def sentences_packed(doc: dict, size: int = 100) -> list[dict]:
    # split the document into sentences and headings
    # using our split_sentences function we made
    units = split_sentences(doc["body"])
    # pack the sentences into chunks, each chunk having at most 'size' words
    packed = pack(units, size)
    # create an empty list to store the finished chunks
    chunks = []
    # go through each group of text and give it a number starting from 0
    for number, words in enumerate(packed):
        # then turn the text into a chunk dictionary and add it to our list.
        chunks.append(_chunk(doc, number, words))
        # return the list of chunks
    return chunks


# def sentence_packed(doc: dict, max_words: int = 100) -> list[dict]:
#  return[_chunk(doc, number, text) for number, text in enumerate(pack(split_sentences(doc["body"]), max_words))]

def by_section(doc: dict, max_words: int = 150, contextual: bool = True) -> list[dict]:
    """
    One chunk per '## " section... long sentences are packed by section
    contextual=True | Prefixes each chunk with 'Document Title > Section Heading', so a chunk that never names
    its subject still carries it into the embedding

    ## Tokyo
    The office has underperformed against its original business case and is under review. It employs 38 lawyers, against the 60 forecast when it opened. Revenue per lawyer is the lowest in the firm. The board's assessment of the office is filed under matter reference LP-3307 and is not for external circulation. A decision is expected by the end of the first quarter.
    """

    chunks, number = [], 0
    parts = re.split(r"(?m)^## ", doc["body"]) if "## " in doc["body"] else [doc["body"]]
    for part in parts:
        heading, _, text = part.partition("\n") if "## " in doc["body"] else ("", "", part)
        heading, text = heading.strip(), text.strip()
        if not text:
            continue
        for piece in pack(split_sentences(text), max_words):
            if contextual:
                prefix = f"{doc['title']} > {heading}\n" if heading else f"{doc['title']}\n" 
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

# import chunking, corpus

# COMBINE OLD AND NEW DOCS 

# loop through and call chunk_corpus
