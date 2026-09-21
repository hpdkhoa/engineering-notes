**English** · [Tiếng Việt](README.vi.md)

# gen-system, HieuLuat, Beastwarden

Three systems I work on. This is what I can publish about each.

gen-system has [its own repository](https://github.com/hpdkhoa/gen-system) with the code, the tests
and the benchmark drivers. The other two I cannot open. HieuLuat runs on a law firm's real case
files and the company is being sold, so its source, prompts and legal corpus stay where they are,
and Beastwarden is half built. For those two this repository has the design docs and the tables,
and that is all it has.

Everything here is written twice, English and Vietnamese. The Vietnamese files end in `.vi`.

## The three systems

| System | What it does | Stack | Pages |
|---|---|---|---|
| gen-system | Reads a codebase into a deterministic graph built from the AST, states what the model assumes about each routine, and checks the generated code from outside | Go, local models through Ollama, graph RAG | [projects/gen-system/README.md](projects/gen-system/README.md) |
| HieuLuat | Vietnamese legal question answering. It cites the law it used, or it answers that it does not know | Python, pgvector, bge-m3 embeddings on GPU, cross encoder rerank | [projects/hieuluat/README.md](projects/hieuluat/README.md) |
| Beastwarden | A tactics roguelite with a seeded deterministic core and about 2,000 tests. Also my notes on directing AI assisted development | TypeScript, Vite, Pixi, Vitest | [projects/beastwarden/README.md](projects/beastwarden/README.md) |

## Writeups

- [01, making a legal search path fast and still correct](writeups/01-hieuluat-retrieval-optimization.md).
  Vector indexing, retrieve then rerank, FP16 embeddings, and how much of the request each stage
  actually costs.
- [02, tuning local LLM inference for a code engine](writeups/02-gen-system-inference-optimization.md).
  GPU layer offload, streaming, quantization as a measured variable, and two models sharing one
  16 GB card.
- [03, reproducible benchmarking and regression gates](writeups/03-reproducible-benchmarking.md).
  The method under the other two: frozen baselines, committed task sets, repeatable runs.

Each one has a section on something I got wrong. In 01 the reranker cost 384 ms and improved
nothing. In 02 my quality metric could not move, so it could never fail. I keep writing those
down, otherwise I walk into them again a year later.

The writeups are markdown. There is an HTML version of each one too, linked from
[index.html](index.html), if you would rather read it that way.

## Where the numbers come from

- [benchmarks/results/measured.json](benchmarks/results/measured.json) holds every table. The
  harnesses write that file. I do not type a number into a writeup by hand.
- [benchmarks/ENVIRONMENT.md](benchmarks/ENVIRONMENT.md) records the machine behind the gen-system
  tables: an RTX 4060 Ti with 16 GB, driver 595.71.05, Ollama 0.24.0, Go 1.25.0, and the commit the
  campaign froze at.
- The 2026-09-09 campaign keeps its raw files, `MANIFEST.sha256` and `ATTESTATION.md` in the
  gen-system repository, beside the code that produced them.
- gen-system rows carry the date, the commit, the frozen task set, `n` and a range. HieuLuat rows
  carry the date, the evaluation set and the GPU, because that harness is private.
- [benchmarks/README.md](benchmarks/README.md) explains how to read a table.

## Snippets

Two small Python files that run on toy data with no dependencies:

```bash
python snippets/toy_retrieval.py
python snippets/roofline_demo.py
```

`toy_retrieval.py` runs the retrieve then rerank pattern over random vectors, and shows why an
approximate index needs its recall measured. `roofline_demo.py` is naive against blocked matrix
multiply in plain Python, so the memory wall shows up without a GPU in the room. No production
code in either. See [snippets/README.md](snippets/README.md).

## Regenerating the repo

`tools/fill_portfolio.py` runs on my own machine, where the private repositories live. It collects
repository statistics from git, captures the environment with `nvidia-smi` and `ollama list`, and
injects the tables from `measured.json` between the `<!--measured:...-->` markers. It never copies
source into this repository.

`tools/regen_writeup_html.py` rebuilds the HTML twin of each writeup, English and Vietnamese. Run
it after `fill_portfolio.py`, or the twins go out of date with the markdown. The HTML files are
generated, so edit the markdown and rerun the tool.

## Status

- gen-system: preparing the Apache-2.0 release.
- HieuLuat: commercial, and its ownership is changing hands. The implementation stays private.
- Beastwarden: in development.
- Next: a hand written CUDA kernel inside gen-system, profiled with Nsight before and after, with a
  roofline analysis. The path it targets is under 1 ms of a 385 ms request, so it demonstrates the
  capability rather than speeding the request up.

## About me

Khoa Hoang. I spent a year at National Australia Bank, then two and a half years at FPT Software as
a solution architect, moving legacy systems onto cloud native architectures.

The target design was rarely the hard part. The hard part was that nobody could say what the old
system actually did, and the people who knew had left years ago. An AI model has the same trouble
with a codebase, except you find out when the output is wrong. I have built my own systems full
time since November 2025. Both come back to that: write down what the machine is assuming, then
run a check that can fail.

[hpdkhoa2311@gmail.com](mailto:hpdkhoa2311@gmail.com) · [github.com/hpdkhoa](https://github.com/hpdkhoa)

## License

See [LICENSE](LICENSE). The writeups, architecture docs, benchmark tables and snippets are here to
read and quote with attribution. gen-system is licensed separately under Apache-2.0 in its own
repository. HieuLuat's implementation is proprietary and is not included here.
