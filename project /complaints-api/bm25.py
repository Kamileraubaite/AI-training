"""BM25 keyword search over banking document chunks.

No network or model calls.
"""

import math
import re
from collections import Counter

k1 = 1.5  # Controls how much repeated words increase the score.
B = 0.75  # Controls the adjustment for chunk length.


# Split text into lowercase words and numbers.
# For example, "PRD-003" becomes ["prd", "003"].
def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())

#BM25 class
    # idf
    # score
    # search

class BM25Index:
    def __init__(self, chunks: list[dict]) -> None:
        if not chunks:
            raise ValueError("Cannot build index from zero chunks")
        self.chunks = chunks
        self.term_counts = [Counter(tokenize(c["text"])) for c in chunks]
        self.lengths = [sum(counts.values()) for counts in self.term_counts]
        self.avg_length = sum(self.lengths) / len(chunks)

        # Count how many chunks contain each term.
        self.doc_freqs = Counter()
        for counts in self.term_counts:
            self.doc_freqs.update(counts.keys())

    def idf(self, term: str) -> float:
        n = len(self.chunks)
        df = self.doc_freqs.get(term, 0)
        return math.log(1 + (n - df + 0.5) / (df + 0.5))  
    
    def score(self, query_terms: list[str], position: int) -> float:
        counts = self.term_counts[position]
        length_norm = (1 - B) + B * (self.lengths[position] / self.avg_length)
        total = 0.0
        for term in set(query_terms):
            tf = counts.get(term, 0)

            if tf:
                total += self.idf(term) * tf * (k1 + 1) / (tf + k1 * length_norm)
        return total
    
    def search(self, query: str, k: int = 10) -> list[dict]:
        terms = tokenize(query)
        scored = []
        for position, chunk in enumerate(self.chunks):
            Bm25 = self.score(terms, position)
            if Bm25 > 0:
                scored.append({"chunk": chunk, "bm25": Bm25})
        scored.sort(key=lambda hit: hit["bm25"], reverse=True)
        return scored[:k]