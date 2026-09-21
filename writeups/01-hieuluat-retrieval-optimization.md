**English** · [Tiếng Việt](01-hieuluat-retrieval-optimization.vi.md)

# Making a legal search path fast and still correct

### Vector indexing, reranking, and FP16 embeddings, with the trade offs measured

> **Context:** HieuLuat is a Vietnamese legal question answering system. See the
> [project page](../projects/hieuluat/README.md). It is a commercial product whose ownership is
> changing hands, so the code, the corpus and the prompts are private. **What this covers:** how I
> > made its search path fast without making it less trustworthy. A wrong answer that arrives
> quickly is still an answer a lawyer repeats to a client. The measurements are below. The code is
> not.

---

## 0. The machine

One consumer GPU. The rows in section 5 were measured in August 2026 by HieuLuat's own retrieval
bench on an NVIDIA RTX 4060 Ti with 16 GB, against a fixed, labeled evaluation set, and written into
[`benchmarks/results/measured.json`](../benchmarks/results/measured.json) one label per
configuration. The harness itself and its commit are in the private repository, so these rows
carry the date, the evaluation set and the GPU, and nothing more. They have not been re-run since. Where the text quotes a number, the table above it is the source:
the harness writes `measured.json`, `tools/fill_portfolio.py` renders the tables, and I fix the text
when a table moves.

## 1. Where it started

The search path had three parts that used the GPU or the database heavily: an embedder (bge-m3),
a pgvector cosine search, and a cross encoder reranker.

All three worked. Nobody had tuned any of them.

1. **The vector search had no index.** Postgres computed the distance to every row, then sorted.
   That is fine for a few thousand chunks. It gets slow as the corpus grows.
2. **The reranker was switched off.** The component that judges relevance best was not being used.
3. **The embedder ran in full precision.** No FP16 path, so it used more memory bandwidth than it
   needed to.

## 2. Move 1: add a real vector index

This was the cheapest change and the biggest win. I replaced the full scan with an approximate
nearest neighbor index. There are two options in pgvector: IVFFlat, which groups vectors into
lists, and HNSW, which builds a graph. Both replace a full scan with a lookup that scales.

**The catch is the word approximate.** These indexes can miss the true nearest neighbor. In most
products that is a small quality loss. In a legal product it is not. HieuLuat promises to say
"no information" when it cannot find an answer. If the index drops the chunk that held the answer,
the system says "no information" when the answer existed. That is a correctness bug, not a speed
tuning detail.

So the swap costs something. You trade recall against latency, and the dial is `probes` on IVFFlat
or `ef_search` on HNSW.

**What I measured.** Query latency as the corpus grows, for full scan, IVFFlat, and HNSW. Then
recall at k against latency as I turned the dial. That second curve is the useful one. It shows
how much latency buys how much recall, so the operating point can be chosen against the
correctness bar instead of guessed.

I was not shopping for the fastest index. I wanted the setting where recall still keeps the promise,
and then the lowest latency I could get at that setting.

## 3. Move 2: retrieve wide, then rerank

Once the index was in place, retrieval became cheap enough to pull a larger candidate set and
rescore it. The cross encoder scores each question and chunk pair, then keeps the best few.

This is a standard two stage pattern. It usually improves how well answers are grounded in the
source, which for legal work is the metric that matters.

It also creates a GPU batching problem worth solving properly. The reranker should score the whole
candidate set in one batched FP16 forward pass, not in a Python loop.

The cost is latency. Retrieving more and reranking it takes time. So the result to report has three
axes: recall, answer quality, and the added milliseconds.

## 4. Move 3: FP16 embeddings

Running bge-m3 in half precision roughly halves the memory it needs and the bandwidth it uses. On
a modern GPU it also speeds up the forward pass. Quality loss for this use is negligible.

The part worth getting right is that there are two different jobs here, and they have different
bottlenecks:

- **Bulk ingest**, when embedding again the whole corpus, is limited by throughput. Large batches and
  FP16 help a lot.
- **Online query**, when embedding one question, is limited by latency and fixed overhead. Batch
  size barely matters. Keeping the model warm matters more.

Using one batch size for both jobs is the common mistake. I measured them separately: the FP32 to
FP16 throughput difference, and a batch size sweep showing the embedder is limited by memory
bandwidth, which is what you would expect.

## 5. Results

<!--measured:hieuluat-->
### Measured results

*Rendered from `benchmarks/results/measured.json`. Every number below comes from the project's own harness on the machine described in section 0.*

**Vector index: recall vs latency**

| index | recall at 10 | p50 latency ms | p95 latency ms |
|---|---|---|---|
| sequential scan | 0.75 | 6.4 | 6.9 |
| sequential scan, FP32 embeddings | 0.75 | 6.4 | 7.6 |
| IVFFlat (lists=100) | 0.7 | 0.8 | 0.9 |
| IVFFlat (lists=100, probes=10) | 0.75 | 1.0 | 1.3 |
| HNSW (m=16) | 0.75 | 0.9 | 1.3 |

*Measured 2026-08, fixed evaluation set.*

**Two-stage rerank: quality vs added latency**

| config | answer quality pct | added latency ms |
|---|---|---|
| retrieve only (k=10) | 75.0 | 0 |
| retrieve k=50 + cross-encoder rerank | 75.0 | 383.6 |

*Measured 2026-08, fixed evaluation set.*

**Embedding precision: throughput & VRAM**

| precision | docs per sec bulk | vram gb |
|---|---|---|
| FP16 | 1414.5 | n/a |
| FP32 | 490.5 | n/a |

*Measured 2026-08, fixed evaluation set.*

<!--/measured-->

### What the numbers say

| Change | Effort | Effect | What I measured |
|---|---|---|---|
| Vector index (IVFFlat or HNSW) | Low | Search scales as the corpus grows | Latency against corpus size, recall at k against latency |
| Retrieve wide, then rerank | Medium | Better grounded answers | Recall, answer quality, added latency |
| FP16 embeddings | Low | Faster embedding, less VRAM | FP32 to FP16 throughput, batch size sweep |

Three things worth pulling out of it. The tuned index matches the exhaustive scan's recall at about a sixth of its
median latency. The reranker adds 384 ms and changes answer quality by nothing. FP16 embeds the
corpus about 2.9 times faster than FP32 in bulk, and the VRAM column reads n/a because the harness
did not sample it, not because it was zero. The first and second readings are section 6.

## 6. The recall ceiling, and why reranking did not help

One result in that table looks like a failure. It took me a while to work out which component it
blames.

Recall at 10 is 0.75 on the full scan. **The full scan is exhaustive.** It compares the question to
every row, so there is no approximation in it to lose recall to. That means 0.75 is not a result
about the index at all. It is the ceiling of what this embedding model finds at k equals 10 on this
evaluation set. About a quarter of the correct chunks are not in the top ten under any index.

Read against that ceiling, the index work did exactly what it should. HNSW and tuned IVFFlat both
return 0.75, matching the exhaustive scan, while cutting median latency from 6.4 ms to about 1 ms.
Untuned IVFFlat sits at 0.70, which is the honest cost of leaving `probes` at its default and the
reason the tuning step was not optional. So the index bought a roughly six times latency
reduction at no cost to recall. It did not "stay flat."

**The reranker is a different story, and a genuinely negative result.** Retrieving 50 candidates
and rescoring them added 384 ms and changed answer quality by nothing.

That follows from the ceiling. A reranker only reorders the candidates it was handed, so when the
right chunk never came back from retrieval, rescoring cannot invent it.

**What I have not separated.** A flat 0.75 across every configuration is also what a broken
evaluation set looks like. The measurement that tells the two apart is recall at 50, which is the
candidate set the reranker actually sees.

- If recall at 50 is also around 0.75, the misses are real retrieval misses. Then the fix is
  upstream of both the index and the reranker: better chunking, hybrid keyword and vector search,
  or a better embedding model for Vietnamese legal text.
- If recall at 50 is much higher, the candidates were there and the reranker failed to promote
  them. That is a reranker problem, and an easier one.

That number was not measured before the product changed hands, so the honest claim stays the
narrow one. The index is not the bottleneck, and the reranker has not earned its 384 ms. So it comes out of the default answer path, and it stays out until someone measures recall at 50.

## 7. Future work

The deepest extension is a hand written CUDA kernel for part of the scoring path. It would fuse the
normalize and dot product steps over the candidate set, profiled with Nsight against the NumPy and
pgvector versions. That is the difference between calling a GPU library and writing the kernel. With HieuLuat's code
private, that work now happens in gen-system, whose retrieval path has the same cosine scoring
shape; the plan is in the [inference writeup](02-gen-system-inference-optimization.md).

The caveat comes first, because it is the whole shape of the thing. The scoring path is under 1 ms
of a request that took about 385 ms with the reranker on. A kernel there demonstrates the
capability. It will not speed up the request. So I say that at the start, show the roofline that
predicts the result, and then measure it anyway.

## 8. What I would do again

I chose the index operating point against the safety promise rather than a latency target, and I
split the embedding work into the two jobs that bottleneck on different things. Neither is clever.
Both are what you skip when you are in a hurry.

Section 6 is the part I still think about. The reranking result came out negative and the recall
number sat flat enough to be embarrassing. Working out which component the flat number blames, and
naming the one measurement that would settle it, took longer than all the tuning did.

*Measurements were taken before and after against fixed evaluation sets, on the machine in
section 0. The method is in [reproducible benchmarking](03-reproducible-benchmarking.md). Absolute values depend on the GPU. The shape of each trade off should hold on another card.*
