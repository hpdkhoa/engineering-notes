"""
toy_retrieval.py: a teaching toy for the two stage retrieve then rerank pattern.
It also shows why you must measure the recall of an approximate index.

This is not HieuLuat. It has no bge-m3, no pgvector and no legal data. It uses random
vectors and a lossy "approximate" search on purpose, so you can run and check the idea.

Run:  python3 toy_retrieval.py
Deps: standard library only.
"""

import random
import math

random.seed(42)

DIM = 16
N_DOCS = 2000
TOP_K = 5          # how many results the user wants in the end
WIDE_K = 50        # how many we retrieve before reranking


def rand_vec():
    return [random.gauss(0, 1) for _ in range(DIM)]


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb + 1e-9)


# a corpus of fake "chunks"
corpus = [rand_vec() for _ in range(N_DOCS)]
query = rand_vec()


# exact search gives the ground truth. It is O(N), like a sequential scan.
def exact_topk(q, docs, k):
    scored = sorted(range(len(docs)), key=lambda i: cosine(q, docs[i]), reverse=True)
    return scored[:k]


# a toy "approximate" search. It scores the whole corpus with a cheap, noisy scorer
# (exact cosine plus noise). This models real ANN behaviour far better than random
# sampling. The ranking is roughly right but jittered, so the true top-k may not
# land in the approximate top-k. They almost always survive in a wider cut.
def approx_scores(q, docs, noise):
    return [cosine(q, docs[i]) + random.gauss(0, noise) for i in range(len(docs))]


def approx_topk(q, docs, k, noise):
    scores = approx_scores(q, docs, noise)
    order = sorted(range(len(docs)), key=lambda i: scores[i], reverse=True)
    return order[:k]


def recall_at_k(approx_ids, exact_ids):
    return len(set(approx_ids) & set(exact_ids)) / len(exact_ids)


# a toy "cross-encoder" reranker. It is an exact, expensive scorer that runs only on
# the small wide candidate set. The real one is a heavier model with the same shape.
def rerank(q, docs, candidate_ids, k):
    candidate_ids = sorted(candidate_ids, key=lambda i: cosine(q, docs[i]), reverse=True)
    return candidate_ids[:k]


print("=== Ground truth (exact search) ===")
truth = exact_topk(query, corpus, TOP_K)
print(f"True top-{TOP_K} doc ids: {truth}\n")

print("=== Why you must measure the recall of an approximate search ===")
print("A cheap approximate scorer ranks roughly right, with jitter. More 'noise'")
print("means a cheaper, coarser index and lower recall. This is the recall versus speed dial.")
print(f"{'noise level':>15} | {'recall@'+str(TOP_K):>10}")
print("-" * 30)
for noise in (0.50, 0.30, 0.20, 0.10, 0.05, 0.00):
    approx = approx_topk(query, corpus, TOP_K, noise)
    print(f"{noise:>15.2f} | {recall_at_k(approx, truth):>10.2f}")
print("\nA coarser, cheaper approximate search can drop the right answer.")
print("A legal RAG must say 'no info' when it has no answer. You pick the operating point")
print("where recall is high enough for that rule to hold, then minimize latency.\n")

print("=== Two stage retrieve then rerank ===")
NOISE = 0.20
# The single stage baseline takes the approximate top-K directly.
single = approx_topk(query, corpus, TOP_K, NOISE)
print(f"Single stage (approx top-{TOP_K}, noise={NOISE}):       recall@{TOP_K} = "
      f"{recall_at_k(single, truth):.2f}")

# Two stage: the same cheap scorer retrieves a wide set, then the exact reranker sorts it again.
wide = approx_topk(query, corpus, WIDE_K, NOISE)
final = rerank(query, corpus, wide, TOP_K)
print(f"Two stage  (retrieve {WIDE_K}, rerank to {TOP_K}): recall@{TOP_K} = "
      f"{recall_at_k(final, truth):.2f}")
print(f"   the wide set captured {len(set(wide) & set(truth))}/{TOP_K} true neighbors, "
      f"and the exact reranker brings them to the top.")
print("\nAt the same first stage cost, retrieving wide and then reranking")
print("recovers quality that the approximate top-K alone would miss.")
print("That is the core reason the two stage pattern improves grounding.")
