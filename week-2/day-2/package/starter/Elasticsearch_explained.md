# Elasticsearch and Hybrid Search, Explained (Team A)

A plain-language guide to what Elasticsearch is and how it does hybrid retrieval. It is written for the "Hybrid Retrieval in the Real World" research task.

---

## 1. What is Elasticsearch?

Elasticsearch is a search engine and document store. You put JSON documents in (this is called *indexing*), then ask questions over a REST API and get ranked results back.

It can search in two very different ways:

| | Keyword search (BM25) | Vector search (kNN) |
|---|---|---|
| Matches on | The actual words | The meaning |
| Good at | Exact codes and names, e.g. `LP-3307` | Paraphrases, e.g. "car" finds "automobile" |
| Weak at | Synonyms and rewording | Rare tokens an embedding model has never learned |
| Needs a model? | No | Yes (e.g. Voyage embeddings) |
| Our app has it? | **No** | **Yes** (Chroma + cosine) |

---

## 2. How keyword search works: the inverted index

A normal index maps document to words. An inverted index flips this and maps each word to the documents that contain it. That is why finding `3307` is instant and exact.

```
Documents                         Inverted index
─────────                         ──────────────
doc1: "matter LP-3307 opened"     matter ──► doc1, doc3
doc2: "billing policy update"     3307   ──► doc1
doc3: "matter closed"             billing──► doc2
                                  closed ──► doc3
```

### BM25: how results are ranked
BM25 is the default scoring formula. A document scores higher when:

- the search term appears **more often** in it (term frequency),
- the term is **rare** across all documents (inverse document frequency),
- the document is **short** rather than long (length normalisation).

Two settings tune it. The defaults are from a [DEV Community article](https://dev.to/akshay_gupta/hybrid-search-in-elasticsearch-combining-bm25-and-knn-with-rrf-2k3e):

- `k1` (default 1.2) controls how quickly repeated words stop adding score.
- `b` (default 0.75) controls how strongly long documents are penalised.

---

## 3. Why hybrid? Our `q24` problem

Our app uses vector search only. The question *"What is matter LP-3307?"* is refused at every relevance floor we tried.

```
Query: "What is matter LP-3307?"

Vector search          Keyword search
─────────────          ──────────────
"LP-3307" means        Finds the token
nothing to the         "3307" exactly
embedding model        in the right chunk
      │                      │
 low cosine score        strong BM25 match
      │                      │
  REFUSED by 0.45        FOUND
  relevance gate
```

Each method covers the other's blind spot. Hybrid search runs both and merges the results.

---

## 4. How Elasticsearch does hybrid search

You send **one request** containing an `rrf` retriever with two child retrievers. Elasticsearch runs both and fuses their ranked lists.

```
                    ┌────────────────────┐
   user query ────► │    rrf retriever   │
                    └─────────┬──────────┘
              ┌───────────────┴───────────────┐
              ▼                               ▼
   ┌─────────────────────┐        ┌─────────────────────┐
   │ standard retriever  │        │    knn retriever    │
   │ (BM25, keywords)    │        │ (vector, meaning)   │
   └──────────┬──────────┘        └──────────┬──────────┘
              │ ranked list A                │ ranked list B
              └───────────────┬──────────────┘
                              ▼
                  Reciprocal Rank Fusion
                              ▼
                   one merged ranked list
                              ▼
                      top `size` results
```

Example request (from Elastic's [RRF reference](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion)):

```json
{
  "retriever": {
    "rrf": {
      "retrievers": [
        { "standard": { "query": { "match": { "title": "waterproof jacket" } } } },
        { "knn": { "field": "embedding", "query_vector": [0.12, 0.87, 0.44],
                   "k": 40, "num_candidates": 80 } }
      ],
      "rank_window_size": 40,
      "rank_constant": 60
    }
  },
  "size": 10
}
```

It needs **at least two** child retrievers.

---

## 5. Reciprocal Rank Fusion (RRF)

RRF only looks at **position** in each list, not the scores.

```
score(doc) = sum over each list of   1 / (rank_constant + rank)
```

Ranks start at 1, and `rank_constant` defaults to **60**. That value comes from the Cormack, Clarke and Buettcher 2009 SIGIR paper.

### Worked example (k = 60)

| Doc | Keyword rank | Vector rank | Calculation | RRF score |
|---|---|---|---|---|
| A | 1 | 5 | 1/61 + 1/65 | 0.0318 |
| B | 2 | 1 | 1/62 + 1/61 | 0.0325 |
| C | 3 | not in list | 1/63 | 0.0159 |

B wins because it ranks well in **both** lists, even though A topped the keyword list. A document that appears in only one list gets only one contribution.

### Defaults

- `rank_constant`: 60 (must be at least 1; higher values give lower-ranked documents more influence).
- `rank_window_size`: defaults to the request's `size`. It is how many results from each list are considered.

---

## 6. Rank-based vs score-based fusion

| | Rank-based (RRF) | Score-based |
|---|---|---|
| How it works | Uses only each list's order | Rescales each list's scores, then adds them |
| Gains | No normalisation needed, robust, no tuning | Keeps *how much* better one result is |
| Throws away | The size of score gaps | Nothing, but it needs careful normalisation and tuning |

The score-gap point in one picture:

```
Vector scores:   0.90   0.40          0.90   0.89
Ranks:            1st    2nd           1st    2nd
                  ▲ big gap            ▲ tiny gap
RRF sees both cases as identical (1st, 2nd).
```

In Elastic's own benchmark (section 9) a tuned weighted sum beat RRF. But the weights were tuned on the test datasets, so it is a best case rather than a fair fight.

---

## 7. Weighting one retriever above the other

This was the Team A starter question: *"When would you set one above 1.0?"*

The sources disagree, so note the version:

- The main RRF page says each child retriever has an equal weight and needs no tuning.
- Elastic's newer [weighted RRF post](https://www.elastic.co/search-labs/blog/weighted-reciprocal-rank-fusion-rrf) says each contribution becomes `weight × 1 / (rank + rank_constant)`. The retriever reference says this is available from Elastic Stack **9.2**.

**Our reasoning, not Elastic's:** set a weight above 1.0 when you trust one retriever more for your queries. If users often search for matter codes, weight BM25 up.

> Open: the exact JSON field for setting weights. Check the [rrf retriever reference](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/retrievers/rrf-retriever) before relying on it.

---

## 8. Where the keyword half comes from

| Type | Example | How it works |
|---|---|---|
| Classic BM25 | Elasticsearch's default `standard`/`match` query | Inverted index plus the formula in section 2. No model needed. |
| Learned sparse | Elastic's ELSER | A trained model produces weighted terms (including related words not in the text). It is still searched like keywords. |

---

## 9. Does hybrid actually help? (Core question 2)

Source: Elastic's [BEIR benchmark post](https://www.elastic.co/search-labs/blog/improving-information-retrieval-elastic-stack-hybrid), 20 July 2023.

- **Who ran it:** Elastic, testing its own product. It is evidence, but not neutral.
- **Dataset:** a subset of BEIR (nine datasets).
- **Metric:** NDCG@10, averaged across datasets.
- **Results:**
  - BM25 + ELSER with RRF (k=20, N=1000): about **18% higher** than BM25 alone and about **1.4% higher** than ELSER alone.
  - Weighted sum with tuned weights: about 24% above BM25 alone and 6% above ELSER alone (best-case bound).

---

## 10. One catch

Weighted RRF needs Elastic Stack **9.2 or later**. I also couldn't confirm which license tier the `rrf` retriever needs. Check Elastic's subscription page.

---

## 11. Advice for our app

**Should we add hybrid search? Yes.** Our app has no keyword search, and `q24` fails for exactly the reason keyword search fixes.

Things to watch:

- Our relevance gate refuses anything under a cosine of 0.45. RRF scores are tiny numbers (around 0.03) and are not cosines, so the gate has to be redesigned after fusion. One option is to gate on the vector score or on a keyword match.
- Test it. Re-run the eval set, including `q24`, before and after.

---

## 12. Open questions

- The exact field and syntax for per-retriever weights.
- The license tier for the `rrf` retriever.
- The "Practical BM25, part 3" URL from the brief returned a 404, so the `k1` and `b` defaults come from a DEV Community article.

---

## Sources

- [Elastic: RRF reference](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion)
- [Elastic: rrf retriever reference](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/retrievers/rrf-retriever)
- [Elastic: Weighted RRF](https://www.elastic.co/search-labs/blog/weighted-reciprocal-rank-fusion-rrf)
- [Elastic: Hybrid retrieval benchmark](https://www.elastic.co/search-labs/blog/improving-information-retrieval-elastic-stack-hybrid)
- [DEV Community: BM25 + kNN with RRF](https://dev.to/akshay_gupta/hybrid-search-in-elasticsearch-combining-bm25-and-knn-with-rrf-2k3e)
- Cormack, Clarke and Buettcher, SIGIR 2009 (named in the task brief; not read directly)
