"""
Same evidence, same questions, 2 system prompts.
Outcome: what does the looser system prompt do??
"""

import grounding
import llm
from corpus import CORPUS_DOCUMENTS

LOOSE_PROMPT = (
    "You are a helpful legal analyst. Answer the question fully and heplfully as"
    "you can. Cite the document id in square brackets where you use it."
)

QUESTIONS = [
    "Who is the managing partner at harding & Voss, and how long have they held the role?"
    "How does harding & Voss's profitability compare with the magic circle firms?",
]

def main() -> None:
    for question in QUESTIONS:
        