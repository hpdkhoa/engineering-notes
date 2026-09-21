**English** · [Tiếng Việt](README.vi.md)

# gen-system: local code understanding and generation

> An AI model is a black box. gen-system writes down what the model assumes about your code,
> checks every assumption against a deterministic graph built from the AST, and lets you correct
> any of them. Then it verifies the generated output from outside. It runs entirely on your own
> machine. I am preparing the source for release under Apache-2.0 at
> [github.com/hpdkhoa/gen-system](https://github.com/hpdkhoa/gen-system); the repository opens
> with the release. This page covers the architecture and the reasoning.

---

## Fast facts

- **History:** I have built it alone since November 2025. Apache-2.0, release in preparation.
- **Engine:** Go. 266 source files with 49,079 lines, plus 79 test files with 15,197 lines and
  598 test functions, in 54 packages. The benchmark harness adds 1,155 lines of Python and 3,308
  lines of shell. Counted on 2026-09-11 at commit `cfb0bff2`, test and generated code excluded from
  the source count.
- **Languages it reads:** Go, COBOL with copybooks, CA Gen, Java, TypeScript, Python. Exact symbol
  resolution, call graphs, control flow graphs
- **Inference:** open weight models through Ollama on one RTX 4060 Ti with 16 GB. `qwen3:14b` plans
  and `qwen2.5-coder:14b` writes code
- **Quality gate:** 13 benchmark suites, frozen baselines, and repeatable runs at temperature 0
  with a fixed seed. Every campaign ends with a manifest and an attestation.

Speed and VRAM numbers live in the [inference writeup](../../writeups/02-gen-system-inference-optimization.md),
which renders them from [measured runs](../../benchmarks/results/measured.json). This page does
not repeat them, because a copied number goes stale the first time you rerun anything.

## The idea

An AI model is a black box. You cannot see what it assumes about your code. You find out when the
output is wrong, which is the most expensive moment to find out.

So gen-system does three things. The third is the one people skip.

**Write the assumptions down.** It builds a deterministic graph from the AST: symbols, call
edges, control flow, and effects. From that graph it lists, for each routine, the inputs, the
calls it makes, the data it writes, and the action its name suggests. It calls each line a belief.
A local model can add claims. gen-system checks every claim against the graph, marks any claim
that contradicts what the parser saw, and never uses a marked claim. You can correct any line. Only
human verified lines steer generation.

**Ground the model in the graph, not in text.** Context for the model comes from the graph: the
architecture summary, the related routines, the verified beliefs. This is graph RAG built from the
AST, not from embeddings of text chunks.

**Verify from outside the box.** gen-system compiles each generated operation on its own, then
builds and tests the tree, then rereads it with the same deterministic engine that built the
graph. That last step catches what a compiler cannot: unresolved calls, orphan operations, an
operation named as a read that writes. The check has to come from something that does not share
the model's assumptions. Otherwise it is the model agreeing with itself.

The proving ground is legacy code. COBOL with copybooks and CA Gen sit next to Go, Java,
TypeScript, and Python. Legacy is where nobody can say what the system does, and where a wrong
answer costs the most.

A paper from January 2026, Reliable Graph-RAG for Codebases (arXiv 2601.08773), tested this on
Java and found the same thing: deterministic AST graphs ground a model more reliably and more
cheaply than LLM built graphs or vector search. My first version ran two months before it appeared,
which was reassuring to read. gen-system covers six languages and carries on past retrieval, into
beliefs, generation and the verification step.

It also runs locally, so no code leaves the machine, and the same input gives the same output.

## Architecture

**Analysis layer.** Compiler accurate symbol resolution, call graphs and control flow graphs. It
works on the structure a compiler sees, not on code as text.

**Generation layer.** Local models through Ollama, with separate models for planning and for code,
run at temperature 0 with a fixed seed. There is also a deterministic template path that needs no
model at all.

**Verification layer.** Generated projects have to build and pass their tests. Then the analysis
half rereads the generated code and reports what it finds, which catches problems a compiler
cannot see.

**Benchmark harness.** Frozen baselines and regression gates. A parser change that lowers
resolution recall on the committed COBOL baseline fails the gate at once, instead of surfacing
later.

**Orchestration.** Retries, structured output constraints, and model keep alive so a model reload
does not land in the middle of a run.

## Design decisions, and why

**Local first.** Privacy and repeatability instead of the convenience of a hosted API. The whole
pipeline runs on your hardware.

**Determinism.** Temperature 0 and a fixed seed. Without that, a benchmark measures sampling
noise as much as it measures the system.

**Two specialised models instead of one general one.** Planning and writing code are different
jobs, and specialising improves both. The cost is a real problem: two models competing for 16 GB.
The system handles it with keep alive and timeout tuning, and the writeup measures what that costs.

**An objective quality metric, and a correction to it.** The bar is whether the code builds and
passes tests, which beats a perplexity proxy. But the first version of that metric was useless.
When a model written operation fails the compile gate, the gate replaces it with an explicit
`not implemented` stub, and stubs compile. So the pass rate was 100 percent by construction.

The harness now measures how much real logic survived the gate instead of falling back to a
stub, plus the repair counts. The correction is worth more than the number it replaced.

**Team conventions as a checked contract.** A team can hand the generator a style profile: naming,
folder layout, required and banned patterns, size limits, loop style, imports. You write the
profile by hand, or `gen style derive` measures it from an existing repository through the symbol
graph and keeps the evidence count next to every derived rule. The rules go into every prompt the
coder model sees. After generation, the parser checks the same rules over the output, with no
model involved. An
operation that compiles but breaks a rule goes back to the model with the rule named. Style never
turns logic into a stub. Only the compile gate does that.

**A certificate for every campaign.** Each benchmark run ends with an attestation and a manifest.
The attestation says what ran, on which commit and machine, which runs it dropped as not measured
and why, and what did not run. The manifest lists every raw file with its hash. Every number in a
writeup traces back to those files.

## Results

The inference tuning work covers GPU layer offload, output streaming, quantization treated as a
measured variable, and the two model VRAM problem:

→ [Tuning local LLM inference for a code engine](../../writeups/02-gen-system-inference-optimization.md)

The benchmarking method behind it, with frozen baselines and gates, is its own writeup:

→ [Reproducible benchmarking and regression gates](../../writeups/03-reproducible-benchmarking.md)

The tables themselves, with their provenance, are in [benchmarks/](../../benchmarks/README.md).

## Stack

Go. Local LLMs through Ollama, with a planner model and a coder model. Compiler accurate analysis
covering symbol resolution, call graphs, and control flow graphs. Deterministic generation. A
benchmark harness with regression gating.

## Where the code is

I am preparing the source for release under Apache-2.0 at
[github.com/hpdkhoa/gen-system](https://github.com/hpdkhoa/gen-system). The repository stays
private until the release and opens with it. It contains the six parsers, the belief layer, the generation
pipeline, the benchmark drivers under `bench/`, the results of the 2026-09-09 campaign with their
manifest and attestation, the engineering docs under `docs/`, and the test suite.

The inference writeup describes the two determinism bugs I found during this work, together with
the tests that fail against the old code. They are in the repository history, not just in the
writeup.
