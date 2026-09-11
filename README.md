# Engineering portfolio: systems, applied LLMs, and GPU work

> Production systems I have designed and built, presented as architecture and measured results.
> gen-system is being prepared for release under Apache-2.0. HieuLuat is a commercial product with
> private code, so for it the writeup and the measured tables stand in for the source. Every
> gen-system number in this repository links to the campaign, the commit, and the manifest that
> produced it, so the claims can be checked without me in the room.

---

## About me

I am Khoa Hoang. I spent a year at National Australia Bank and two and a half years at FPT Software
as a solution architect, moving legacy systems to cloud native architectures.

The hard part was never the target design. It was that nobody could say for certain what the old
system actually did. That is a black box problem. An AI model has the same problem with your code,
and you usually find out when the output is wrong.

Since November 2025 I have been building my own systems full time. One is a Go engine that makes
an AI model's beliefs about a codebase visible and checkable. It grounds the model in a
deterministic graph built from the AST, and it verifies the output from outside. Its proving
ground is legacy code, COBOL and CA Gen included. The other is a Vietnamese legal question
answering system that refuses to answer without citing the law. Both follow one rule: **measure
it, do not assume it.**

---

## Why this repo looks like this

Each project here is real and shipped. gen-system's code, tests, benchmark drivers and engineering
docs are in [its own repository](https://github.com/hpdkhoa/gen-system), which opens with the
Apache-2.0 release. The other two stay private. HieuLuat is a commercial product whose ownership is
changing hands and holds real legal data. Beastwarden is still in development.

For the private ones, what is published is the part that shows the engineering: how the system is
built, why I made the calls I made, and what the numbers say. Every claim points at the test, the
measured run, or the table behind it.

If you are hiring, start with the writeups. Each one includes a section on something that went
wrong and what it cost, because that is where judgment shows. Writeup 03 states exactly how every
number was produced, and gen-system's task set is committed before the first run, so it cannot be
tuned to the results.

## The projects

| Project | What it is | Stack | Where |
|---|---|---|---|
| **gen-system** | Makes an AI model's beliefs about code visible and checkable, grounds it in a graph built from the AST, and verifies the output from outside | Go, local LLMs via Ollama, deterministic graph RAG | [projects/gen-system/README.md](projects/gen-system/README.md) |
| **HieuLuat** | A Vietnamese legal question answering system that will not answer without grounding | Python, pgvector, GPU embeddings (bge-m3), cross encoder rerank | [projects/hieuluat/README.md](projects/hieuluat/README.md) |
| **Beastwarden** | A deterministic tactics roguelite with a seeded core and about 2,000 tests. Also a case study in directing AI assisted development | TypeScript, Vite, Pixi, Vitest | [projects/beastwarden/README.md](projects/beastwarden/README.md) |
| **GPU and inference work** | Offload, streaming, quantization, two models on one card, roofline | Go harness, Ollama, Nsight method | [writeups/README.md](writeups/README.md) |

## The writeups

Start here. They are the point of the repo.

- **[Making a legal search path fast and still correct](writeups/01-hieuluat-retrieval-optimization.md)**
  Vector indexing, retrieve then rerank, FP16 embeddings. Includes a negative result: the reranker
  cost 384 ms and improved nothing, and section 6 works out which component that actually blames.

- **[Tuning local LLM inference for a code engine](writeups/02-gen-system-inference-optimization.md)**
  GPU offload, streaming, quantization as a measured variable, and two models sharing one 16 GB
  card. Section 4 is about discovering my own quality metric was broken, and what replaced it.

- **[Reproducible benchmarking and regression gates](writeups/03-reproducible-benchmarking.md)**
  The method underneath both: frozen baselines, gates, repeatable runs, and why an objective
  metric that cannot move is worse than a proxy.

## The evidence

- [benchmarks/README.md](benchmarks/README.md): where every table comes from and how to read it.
- [benchmarks/results/measured.json](benchmarks/results/measured.json): the measured tables, written
  by the harnesses, never by hand. The writeups render from this file.
- [benchmarks/ENVIRONMENT.md](benchmarks/ENVIRONMENT.md): the GPU, driver, runtime versions, commit
  and models the gen-system campaign was frozen with, and the capture time.
- The 2026-09-09 campaign's `ATTESTATION.md` and `MANIFEST.sha256` are in the gen-system
  repository beside the raw files.

## Snippets

The [snippets/](snippets/README.md) folder has small Python files that run on their own with toy
data. They show the ideas from the writeups without any production code in them.

## What I am working on next

Turning the GPU work from understanding into a demonstrated kernel: a hand written, profiled CUDA
kernel inside gen-system, measured by its own harness, with Nsight traces before and after and a
roofline analysis. Writeup 01 states the honest limit of the original target up front: the scoring
path it aimed at was under 1 ms of a 385 ms request, so the kernel is a capability demonstration,
not an end to end speedup.

## Contact and licensing

**Khoa Hoang**
[hpdkhoa2311@gmail.com](mailto:hpdkhoa2311@gmail.com) · [github.com/hpdkhoa](https://github.com/hpdkhoa)

The writeups, architecture docs, benchmark tables and snippets in this repo are shared for
portfolio review. See [LICENSE](LICENSE). gen-system is licensed separately under Apache-2.0 in its
own repository. The HieuLuat implementation is proprietary and not included here.
