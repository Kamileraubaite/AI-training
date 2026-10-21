"""
How retrieved hits become the text the model reads
Failure: Lost in the middle
"""

# hits 
def order_for_context(hits: list[dict]) -> list[dict]:
    ranked = sorted(hits, key=lambda h: h["score"], reverse=True)

    front = ranked[0::2]
    back = ranked[1::2]

    return front + back[::-1]

def build_context(hits: list[dict]) -> str:
    return "\n\n".join(f"[{h['id']}] {h['title']}\n{h['text']}" for h in order_for_context(hits))