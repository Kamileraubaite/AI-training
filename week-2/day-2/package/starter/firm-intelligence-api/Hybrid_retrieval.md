# Research Task : Hubrid Retrieval 

#### 1. Rank or score? There are two families of fusion. Rank-based fusion (such as Reciprocal Rank Fusion) uses only each list's order . Score-based fusion rescales each list's scores and adds them. What does each gain, and what does each throw away?

Reciprocal Rank Fusion is a rank aggregation method that combines rankings of multiple sources into a single , unified ranking. 

Rank - It combines different search lists without comparing their original score scales.
What it throws away - It doesnt pay key attention to the actual scores, only the ranking. ie. 

0.90 could be ranked 1st 
0.40 could be ranked 2nd - However it doesn't look at how much the scores differ

Score - It puts each searches scores onto a comparable scale, then combines them. It can identify that A scored much higher than B. 
What it throws away - the original score scale, and depends on how the scores are normalised and weighted. 

#### 2. Does hybrid actually help? Find one published comparison with numbers: hybrid against keyword-only or vector-only . Note the dataset, the metric, the size of the gain,and who ran it.

Microsoft tested Azure AI Search on BEIR benchmark datasets. Hybrid search scored 48.4 on NDCG@10, compared with 45.0 for vector-only and 40.6 for keyword-only. This shows that combining the two improved retrieval in that experiment. However, Microsoft tested its own product, so we should check whether the improvement also happens in our app.

#### 3. Where does the keyword half come from? In production, is it classic BM25 from an inverted index, or a learned sparse model? Find one example of each.



#### Elastic search 

### What is it?

Elasticsearch is a search engine that helps you quickly find relevant information in large amounts of data, such as documents, products or logs.

Search | type |	What it looks for
Keyword search	Matching words, names or exact IDs
Vector search	Similar meaning, using embeddings
Hybrid search	Combines keyword and vector results

## Evidence
| Search type | What it looks for |
|---|---|
| Keyword search| Matching words, names or exact IDs| 
| Vector search | Similar meaning, using embeddings| 
| Hybrid search | Combines keyword and vector results|

sources - 
