**English** · [Tiếng Việt](README.vi.md)

# Writeups

One writeup per topic: the architecture, and the numbers the harness reported. Each is available as markdown, which
GitHub renders directly, and as a self contained HTML page. The [landing page](../index.html)
links the HTML versions.

| Writeup | Markdown | HTML |
|---|---|---|
| Making a legal search path fast and still correct | [.md](01-hieuluat-retrieval-optimization.md) | [.html](01-hieuluat-retrieval-optimization.html) |
| Tuning local LLM inference for a code engine | [.md](02-gen-system-inference-optimization.md) | [.html](02-gen-system-inference-optimization.html) |
| Reproducible benchmarking and regression gates | [.md](03-reproducible-benchmarking.md) | [.html](03-reproducible-benchmarking.html) |

Every table in the writeups is rendered from [`benchmarks/results/measured.json`](../benchmarks/results/measured.json).
The gen-system rows carry the date, the commit, the frozen task set, `n` and a range, and the
campaign's manifest and attestation are in the gen-system repository. The HieuLuat rows carry the
date, the evaluation set and the GPU, because their harness is private. The environment is in
[`benchmarks/ENVIRONMENT.md`](../benchmarks/ENVIRONMENT.md). The HTML pages open locally in a
browser; only the fonts come from a CDN.
