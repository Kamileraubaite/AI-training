# Chunking Decision — Banking Complaints API

## Decision

Use **`sections_contextual`** with a **relevance floor of `0.40`** as the current preferred configuration for document retrieval and grounded answers.

This is a decision based on the current **10 banking documents with `##` section headings** and the **32-question evaluation set**. It is not yet a verified statement about the live API configuration or performance on unseen questions.

## Evidence: retrieval

Run using `eval_retrieval.py` after adding section headings to the existing documents, without the separate additional corpus.

| Strategy | R@1 | R@3 | R@5 | MRR | Context words@3 |
|---|---:|---:|---:|---:|---:|
| `whole_document` | 0.90 | 1.00 | 1.00 | 0.95 | 381 |
| `fixed_100` | 0.72 | 0.83 | 0.86 | 0.78 | 203 |
| `fixed_overlap_25` | 0.79 | 1.00 | 1.00 | 0.89 | 233 |
| `sentences_100` | 0.79 | 0.97 | 1.00 | 0.88 | 213 |
| `sections_plain` | 0.83 | 1.00 | 1.00 | 0.90 | 91 |
| `sections_contextual` | **0.90** | **1.00** | **1.00** | **0.95** | **122** |

`sections_contextual` tied with `whole_document` for the strongest R@1, R@3 and MRR, but retrieved **122 rather than 381 average context words at top 3** (about 68% fewer). `sections_plain` retrieved fewer words still, but had lower R@1 and MRR. These rankings come from exact expected evidence checks, not human judgements of whether every alternative passage is useful.

## Evidence: answer and refusal checks

Run using `eval_answers.py` with the shortlisted section strategies. Answer accuracy uses the existing `keywords_present()` check; refusal accuracy uses `is_refusal()`. These are evaluation-set metrics, not proof of complete factual correctness.

| Floor | Strategy | Answer accuracy | Refusal accuracy | Model calls | Avg input tokens per call | Failures |
|---|---|---:|---:|---:|---:|---|
| 0.35 | `sections_plain` | 1.00 | 1.00 | 30 | 299 | None |
| 0.35 | `sections_contextual` | 1.00 | 1.00 | 30 | 353 | None |
| **0.40** | **`sections_plain`** | **1.00** | **1.00** | **30** | **285** | **None** |
| **0.40** | **`sections_contextual`** | **1.00** | **1.00** | **30** | **326** | **None** |
| 0.45 | `sections_plain` | 0.93 | 1.00 | 29 | 261 | False refusals: q22, q28 |
| 0.45 | `sections_contextual` | 0.93 | 1.00 | 27 | 303 | False refusals: q06, q28 |
| 0.50 | `sections_plain` | 0.90 | 1.00 | 28 | 231 | False refusals: q22, q28; wrong/keyword-check failure: q09 |
| 0.50 | `sections_contextual` | 0.93 | 1.00 | 27 | 286 | False refusals: q06, q28 |

At floor 0.35, `whole_document` was also tested: answer accuracy **0.97**, refusal accuracy **1.00**, **29** model calls, **593** average input tokens, and false refusal **q06**.

## Rationale

- At floor **0.40**, both section strategies passed all recorded answer and refusal checks, with fewer average input tokens than at 0.35.
- Raising the floor to **0.45** or **0.50** introduced false refusals, so the lower token figures at those thresholds do **not** justify choosing them.
- `sections_contextual` ranked expected evidence better than `sections_plain` (R@1 **0.90 vs 0.83**, MRR **0.95 vs 0.90**), while both passed the recorded answer and refusal checks at 0.40.
- `sections_plain` used fewer tokens (**285 vs 326** average input tokens at 0.40). We accept this difference in exchange for stronger retrieval ranking and preserved section/title context.

## Scope and limitations

1. This evaluation used **32 questions** and the current **10 synthetic banking documents**. Performance on new or changed documents and questions is untested.
2. Answer accuracy is based on **keyword presence**, which may miss unsupported claims, incomplete reasoning, or correct alternative wording. Manually review a sample of answers and citations before claiming factual accuracy.
3. Retrieval success checks whether expected evidence text appears in a retrieved chunk; it may count relevant alternative evidence as a miss.
4. Average input tokens are reported **per model call**, not per question or as total usage. Output tokens and end-to-end costs were not measured.
5. The retrieval run and the answer runs measure different stages. The live `/knowledge/search` and `/knowledge/ask` code still needs to be checked to confirm it uses **`sections_contextual`** and **`0.40`**.
6. If documents, evaluation questions, embeddings, or search logic change, rerun the evaluations before relying on this decision.

## Next steps

1. Verify `chunk_index.py` indexes only the intended `DOCUMENTS`, rather than the abandoned extra corpus.
2. Check the live knowledge endpoints and configuration before changing any serving defaults.
3. Add human checks for answer grounding and citation support.
4. Keep copies of the results for each floor under `eval_results/` so the decision remains reproducible.

## Commands used

```bash
.venv/bin/python eval_retrieval.py
.venv/bin/python eval_answers.py whole_document sections_plain sections_contextual --floor 0.35
.venv/bin/python eval_answers.py sections_plain sections_contextual --floor 0.40
.venv/bin/python eval_answers.py sections_plain sections_contextual --floor 0.45
.venv/bin/python eval_answers.py sections_plain sections_contextual --floor 0.50
```
