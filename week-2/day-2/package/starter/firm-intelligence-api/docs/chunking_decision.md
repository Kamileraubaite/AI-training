# Chunking decision

**Date:** 13/10/2026  

**Decided by:** Kamile Raubaite

**Corpus:** documents.py + corpus.py (16 documents)

**Eval set:** eval_set.py (29 answerable, 3 unanswerable) 

**Embedding model:** voyage-3-lite

## Decision
We serve `sections_contextual` with a relevance floor of 0.50.

## Evidence
| Strategy | R@1 | R@3 | MRR | Context words@3 | Answer acc. | Refusal acc. |
|---|---|---|---|---|---|---|
| whole_document |0.69 |1.00 |0.84 |862 |0.72 |1.00 |
| sections_contextual|0.86 |1.00 |0.93 |197 |0.97 |1.00 |
| fixed_overlap_25 |0.52 |0.93 |0.67 |277 |0.55 |1.00 |

## Why this one
Contextual sections found the right information more easily and gave the AI less text to read. 

Having a floor of 0.50 keeps the accuracy at 97% whilst also using fewer tokens. 

Raising it to 0.55 had it use less tokens, however it had the accuracy at 90% in comparison to 97%.

## Known weaknesses

The winner still refuses q24, even though the documents contain the answer.
Its score (0.280) is too low to pass the floor. 

Some questions without answers still pass the floor, so the Ai should check whether the evidence is enough. 

Keyword checks don’t necessarily prove every answer is correct. 
Testing hybrid retrieval would help as the keyword seach could match 'LP-3307' from q24 in addition to vector search. 

## Revisit when

We should revisit when we add longer or new documents, change the models or update the prompt. 

Also review our decision if the system starts refusing questions it should be able to answer.