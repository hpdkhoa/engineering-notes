# Khoa Hoang: engineering portfolio

I build local AI systems that write down what the model assumes and check its output with
something that shares none of its assumptions. This repository holds the writeups, the benchmark
tables and two small snippets. Every page is in English and Vietnamese; the Vietnamese files end
in `.vi`.

## Projects

| Project | What it does | Stack | Status |
|---|---|---|---|
| gen-system | Reads a codebase into a deterministic graph built from the AST, lists what the model assumes about each routine, and checks the generated code from outside | Go, local models through Ollama, graph RAG | Open source, Apache-2.0 |
| poselab-mcp | An MCP server that gives a model measured spatial answers for posing first-person arms and a rifle in Blender: how deep parts clip, how squarely a surface faces the eye, and a solver for rifle moves | Python, MCP, headless Blender | Open source, MIT, version 0.4.0 |
| Beastwarden | A tactics roguelite with a seeded, deterministic simulation core. It is also where I direct AI assisted development under rules a machine checks | TypeScript, Vite, Pixi, Vitest | In development, private |
| HieuLuat | Vietnamese legal question answering that cites the law it used, or says it does not know | Python, pgvector, bge-m3 embeddings, cross encoder rerank | Deprecated after the company's acquisition |

### Links

- gen-system: [GitHub](https://github.com/hpdkhoa/gen-system)
  · [live demo](https://gen-system.500kv.co/demo/)
  · [project page](https://gen-system.500kv.co/)
- gen-system MCP server: [npm package `gen-understand`](https://www.npmjs.com/package/gen-understand)
  · [docs](https://github.com/hpdkhoa/gen-system/blob/main/docs/mcp.md)
- poselab-mcp: [GitHub](https://github.com/hpdkhoa/poselab-mcp)
  · [PyPI](https://pypi.org/project/poselab-mcp/)
  · [MCP Registry](https://registry.modelcontextprotocol.io/v0/servers?search=io.github.hpdkhoa/poselab-mcp)
- Beastwarden:

## gen-system in numbers

I measured these on one RTX 4060 Ti with 16 GB, in the campaign of 2026-09-09.

- 100% of internal calls resolved, 0 parse errors, on four public repositories: 405 files,
  268 of them COBOL.
- First token in 127 ms with streaming, against 1,884 ms with a buffered call. Fifteen times
  sooner.
- 30.8 tokens per second with Ollama's default GPU offload, against 7.9 with 20 layers on the
  GPU. Almost four times faster.
- About 2 seconds to swap between the two models on one 16 GB card, with keep alive.
- 0.674 file recall on 60 SWE-bench Verified tasks at two graph hops. It measures how well
  gen-system finds the files a fix touches. It writes no fix.
- Test coverage is 55% of all statements, from `go test -cover` on 2026-10-08. The
  core runs higher: control flow graphs 93%, beliefs 85%, symbol index 76%, parsers 72%.

## poselab-mcp in numbers

Five posing tasks, three trials each. Pose Lab's own measurements graded every trial.

- 15 of 15 passed with measured answers, against 11 of 15 with pictures alone.
- Half the tool calls (17.3 against 34.8 per task) and a third of the time (45 s against
  153 s).

## Writeups

- [01, making a legal search path fast and still correct](writeups/01-hieuluat-retrieval-optimization.md).
  Vector indexing, retrieve then rerank, FP16 embeddings, and how much of a request each stage
  costs. HieuLuat is deprecated after the company's acquisition; the writeup stays as a record of
  the method.
- [02, tuning local LLM inference for a code engine](writeups/02-gen-system-inference-optimization.md).
  GPU layer offload, streaming, quantization as a measured variable, and two models sharing one
  16 GB card.
- [03, reproducible benchmarking and regression gates](writeups/03-reproducible-benchmarking.md).
  Frozen baselines, regression gates, repeatable runs, and a quality metric that can move.

Each writeup has a section on something I got wrong. In 01 the reranker cost 384 ms and improved
nothing. In 02 my quality metric could not move, so it could never fail.

The writeups are also on the [landing page](index.html) as HTML.

## Benchmarks

The tables behind the writeups are in
[benchmarks/results/measured.json](benchmarks/results/measured.json), and
[benchmarks/README.md](benchmarks/README.md) explains how to read them. The machine behind the
gen-system tables is in [benchmarks/ENVIRONMENT.md](benchmarks/ENVIRONMENT.md).

## Snippets

Two small Python files that run on toy data with no dependencies:

```bash
python snippets/toy_retrieval.py
python snippets/roofline_demo.py
```

`toy_retrieval.py` runs retrieve then rerank over random vectors, and shows why an approximate
index needs its recall measured. `roofline_demo.py` compares naive and blocked matrix multiply in
plain Python, so the memory wall shows up without a GPU. See [snippets/README.md](snippets/README.md).

## Next

A hand written CUDA kernel inside gen-system, profiled with Nsight before and after, with a
roofline analysis. The path it targets takes under 1 ms of a 385 ms request, so the goal is the
skill, and the request will stay about as fast.

## About me

Khoa Hoang. I spent a year at National Australia Bank, then two and a half years at FPT Software as
a solution architect, moving legacy systems onto cloud native architectures.

There, nobody could say what the old system did, and the people who knew had left years ago. An AI
model has the same trouble with a codebase, and you find out when the output is wrong. Since
November 2025 I have built my own systems full time. Each one writes down what the model assumes,
then runs a check that can fail.

[hpdkhoa2311@gmail.com](mailto:hpdkhoa2311@gmail.com) · [github.com/hpdkhoa](https://github.com/hpdkhoa)

## License

See [LICENSE](LICENSE). You can read and quote the writeups, tables and snippets with attribution.
gen-system (Apache-2.0) and poselab-mcp (MIT) carry their own licenses in their own repositories.
HieuLuat's implementation is proprietary, and this repository does not hold it.
