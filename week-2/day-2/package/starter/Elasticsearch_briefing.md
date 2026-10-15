# Hybrid retrieval briefing: Elasticsearch, Team A

## Starter question: when would you set a retriever weight above 1.0?

Elastic's docs say that `weight` is an optional non-negative float that defaults to 1.0, and that the final score is a weighted sum of each child retriever's RRF score ([rrf retriever reference](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/retrievers/rrf-retriever)). Elastic's weighted-RRF post gives the per-retriever contribution as `weight × 1 / (rank + rank_constant)`, but its examples all use weights between 0 and 1, and it doesn't say when to go above 1.0 ([Elastic blog](https://www.elastic.co/search-labs/blog/weighted-reciprocal-rank-fusion-rrf)).

We think you would set a weight above 1.0 on the retriever you trust more for your queries. For our app that is BM25, because users ask about matter codes like `LP-3307`. Weights only matter relative to each other, so `2.0` for BM25 with `1.0` for vector behaves like `0.67` and `0.33`. Test any value against real queries rather than guessing (see the evidence section).

## How it does hybrid search

You send one `_search` request with an `rrf` retriever. It wraps two or more child retrievers, typically a `standard` (BM25 keyword) retriever and a `knn` (vector) retriever, runs them separately, and fuses their ranked lists into one list. At least two child retrievers are required. [source](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion)

```json
{
  "retriever": { "rrf": {
    "retrievers": [
      { "standard": { "query": { "match": { "title": "waterproof jacket" } } } },
      { "knn": { "field": "embedding", "query_vector": [0.12, 0.87, 0.44],
                 "k": 40, "num_candidates": 80 } }
    ],
    "rank_window_size": 40, "rank_constant": 60 } },
  "size": 10
}
```

## Fusion and its defaults

Method: rank-based, Reciprocal Rank Fusion (RRF). Each list adds `1 / (rank_constant + rank)` per document, with ranks starting at 1.

Defaults: `rank_constant` = 60 (at least 1) and `rank_window_size` = 10 (at least 1 and at least `size`). `rank_window_size` is how many results from each list are fused. [source](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/retrievers/rrf-retriever)

Weighting: yes, from Elastic Stack 9.2. Wrap each child as `{ "retriever": {...}, "weight": 2.0 }`. A child without the wrapper gets weight 1.0, and you can mix both forms in one request. [source](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/retrievers/rrf-retriever)

```json
"retrievers": [
  { "retriever": { "standard": { "query": { "match": { "title": "example" } } } }, "weight": 2.0 },
  { "retriever": { "knn": { "field": "vector", "query_vector": [1, 2, 3], "k": 10, "num_candidates": 50 } }, "weight": 1.0 }
]
```

Before 9.2, the main RRF page says each child retriever carries equal weight. [source](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion)

## The keyword side

Classic BM25 from an inverted index is the default. The `standard` retriever with a `match` query uses it, with no model needed. Elastic also offers a learned sparse model, ELSER, which it describes as trained for zero-shot text retrieval. [source](https://www.elastic.co/search-labs/blog/improving-information-retrieval-elastic-stack-hybrid)

## One catch

Per-retriever weights need Elastic Stack 9.2 or later. The `query` and `fields` shortcuts on the retriever date from 9.1. You also can't combine `query` and `retrievers` in the same request. [source](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/retrievers/rrf-retriever)

The reference page doesn't mention a license or subscription tier, so we couldn't confirm one. That is an open question.

## Evidence that hybrid helps

- **Who ran it:** Elastic's own researchers, testing their own product, so it is not a neutral benchmark.
- **Dataset:** a subset of BEIR (nine datasets).
- **Metric:** NDCG@10, averaged across datasets.
- **Gain:** BM25 + ELSER fused with RRF (k=20, N=1000) scored about 1.4% above ELSER alone and about 18% above BM25 alone. A weighted sum with weights tuned per dataset scored about 6% above ELSER alone and 24% above BM25 alone, but that is a best-case bound.

[source](https://www.elastic.co/search-labs/blog/improving-information-retrieval-elastic-stack-hybrid) (20 July 2023)

**What the docs say about testing:** Elastic's `_rank_eval` API takes a set of test queries with manually rated documents and returns metrics such as precision, mean reciprocal rank, and DCG. We think this is the tool for testing whether hybrid helps. We did not find a page where Elastic gives a hybrid-specific testing recipe, and the weighted-RRF post doesn't cover evaluation. [source](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/search-rank-eval)

## Core questions

1. **Rank or score.** Rank-based fusion (RRF) gains robustness. It needs no score normalisation, so lists with different score scales can be combined directly. It throws away how far apart the scores were: 0.90 vs 0.40 and 0.90 vs 0.89 both look like 1st and 2nd. Score-based fusion keeps those gaps and can be tuned, but it needs each list's scores rescaled first. In Elastic's benchmark the tuned weighted sum beat RRF, but the weights were tuned on the test data. [source](https://www.elastic.co/search-labs/blog/improving-information-retrieval-elastic-stack-hybrid)
2. **Does hybrid help.** Elastic's BEIR test: BM25 + ELSER with RRF was about 18% higher in NDCG@10 than BM25 alone and about 1.4% higher than ELSER alone. It was run by Elastic. [source](https://www.elastic.co/search-labs/blog/improving-information-retrieval-elastic-stack-hybrid)
3. **The keyword half.** BM25 example: Elasticsearch's default `standard`/`match` retriever. Learned sparse example: ELSER. [source](https://www.elastic.co/search-labs/blog/improving-information-retrieval-elastic-stack-hybrid)

## Advice for our app

The brief refers to a completed table from "Apply it to our app", but that section was not in the PDF text I extracted. The part below is built from the "what we have today" table on pages 1 and 2 of the PDF.

| Part | What we have today | Under Elasticsearch-style hybrid |
|---|---|---|
| Retrieval | Vector only: Voyage embeddings in Chroma, cosine ranking | BM25 + vector, fused with RRF |
| Keyword search | None | Add BM25 (we think this is what fixes `q24`) |
| Chunks sent to the model | Top 3 | Top 3 of the fused list |
| Relevance gate | Refuse below cosine 0.45 | Needs redesign: RRF scores are about 0.03, not cosines |

**Should we add hybrid search? Yes.** `q24`, "What is matter LP-3307?", is refused at every relevance floor we tried, and the brief's likely reason is that an embedding model can't make sense of a code like `LP-3307`. Keyword search would match `3307` exactly. We would add it, weight BM25 up if matter codes are common, and re-run our eval set, including `q24`, before and after.

## Open questions

- Which license tier the `rrf` retriever needs. The reference page doesn't say.
- When to set a weight above 1.0. Elastic's docs give no guidance, so our answer is reasoning, not sourced.
- Whether Elastic documents a hybrid-specific testing method beyond `_rank_eval`.
- The k1 and b defaults of 1.2 and 0.75 come from a [DEV Community article](https://dev.to/akshay_gupta/hybrid-search-in-elasticsearch-combining-bm25-and-knn-with-rrf-2k3e), because the brief's "Practical BM25, part 3" link returned a 404.
