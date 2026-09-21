**English** · [Tiếng Việt](README.vi.md)

# HieuLuat: Vietnamese legal question answering

> A system that answers questions about Vietnamese law using only retrieved statute. It cites its
> sources. When the corpus does not contain an answer, it says so instead of guessing. HieuLuat is
> a commercial product whose ownership is changing hands, so its code, corpus and prompts stay
> private. This page covers the architecture, the reasoning, and what its evaluation harness
> measured.

---

## Fast facts

- **Status:** shipped product, private code. Built and measured before the 2026-08 evaluation runs
  reported in the writeup; not re-run since.
- **Pipeline:** 7 stages, each repeatable: scrape, extract, chunk, embed, retrieve, rerank, answer
- **Corpus:** Vietnamese legal documents from official sources, chunked on article and provision boundaries
- **Stack:** Python (52,783 lines), PostgreSQL with pgvector, bge-m3 GPU embeddings, cross encoder rerank
- **Promise:** every answer comes from retrieved statute and carries citations. There is a built in path for "no information found"
- **Quality gate:** labeled evaluation sets decide whether an optimization is accepted

## What is here and what is not

The code, the legal corpus, the prompts, the configuration and the evaluation data stay private.
This page has the pipeline with its stage boundaries, the calls I made and why, and the retrieval
numbers the product's own harness reported, including the one that came out negative. Each number
carries its date and its evaluation set. None of them carries a public commit, because the harness
sits in the private repository.

## The problem

Legal question answering has one failure mode that ordinary systems live with and law cannot: a
confident answer that no statute actually supports. A lawyer who repeats it in front of a client
pays for it, not the system.

So the bar is not that the answer sounds right. Every claim has to trace to a real provision, and
the system has to say so when the corpus is silent. That constraint came first, before the
pipeline around it.

## The pipeline

Seven stages. Each one can be rerun safely and tested on its own.

1. **Scrape.** Collect legal documents from official sources, tracking where each one came from.
2. **Extract.** Separate born digital text from scanned pages that need OCR, and handle each
   properly. Extraction quality decides everything downstream.
3. **Chunk.** Split on article and provision boundaries, not on fixed token counts. Each chunk is
   then a complete legal unit that can be cited.
4. **Embed.** Encode chunks with bge-m3 on the GPU into pgvector, tagged by embedding model family
   and by source.
5. **Retrieve.** Cosine nearest neighbor search, filtered by source and model family.
6. **Rerank.** A cross encoder rescores the retrieved candidates. This is the second stage of a
   retrieve wide then rerank design.
7. **Answer.** Generate an answer limited to the retrieved context, with citations, and an explicit
   "no information found" path when retrieval returns nothing useful.

## Design decisions, and why

**Chunking on article boundaries, not fixed windows.** A legal answer has to cite a provision. A
chunk that splits or straddles provisions produces context you cannot cite. So the chunker follows
legal structure.

**Grounding built in, not filtered afterwards.** The citation requirement and the no information
path are properties of the answer stage itself. They are not a filter bolted on after generation.
The system is built so that an ungrounded answer is hard to produce.

**Vectors tagged by source and model family.** The store can hold several embedding model families
and documents from different sources. Retrieval filters on both. Those filters exist for
correctness, not for speed.

**Evaluation sets as a real deliverable.** The project ships labeled evaluation sets, so an
optimization passes or fails on fixed cases instead of on how the demo felt that afternoon.

## Results

The performance and quality work on the retrieval path is written up in detail. That covers the
vector index, turning on the reranker, and FP16 embeddings, with the trade offs measured:

→ [Making a legal search path fast and still correct](../../writeups/01-hieuluat-retrieval-optimization.md)

Worth reading section 6 of that writeup. The reranker turned out to add 384 ms and improve nothing,
and the useful work was figuring out which component that result actually blames.

## Stack

Python. PostgreSQL with pgvector. bge-m3 embeddings on GPU. A cross encoder reranker
(bge-reranker-v2-m3). A staged pipeline where every stage is repeatable. Labeled evaluation sets.

## What transfers

Four things here do not depend on the private code, and I would do them again anywhere.

Pick an approximate index's operating point against the correctness promise, not against a latency
target. Split embedding into the bulk job and the online job, because they bottleneck on different
things. When a quality number will not move, suspect the evaluation set before you believe the
result. And when a component costs 384 ms and buys nothing you can measure, take it out, but write
down the measurement that would bring it back. The method behind all of it is in
[writeup 03](../../writeups/03-reproducible-benchmarking.md).
