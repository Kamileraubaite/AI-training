"""
How retrieved hits become the text the model reads
Failure: Lost in the middle
"""

# hits
def order_from_context(hits: list[dict]) -> list[dict]:
    ranked = sorted(hits, key=lambda h: h["score"], reverse=True)

    front = ranked[0::2]
    back = ranked[1::2]
    new = front + back[::-1]

    return new