# Writeups

Architecture and measured results, one writeup per topic. Each is available as markdown, which
GitHub renders directly, and as a self contained HTML page.

| Writeup | Markdown | HTML |
|---|---|---|
| Making a legal search path fast and still correct | [.md](01-hieuluat-retrieval-optimization.md) | [.html](01-hieuluat-retrieval-optimization.html) |
| Tuning local LLM inference for a code engine | [.md](02-gen-system-inference-optimization.md) | [.html](02-gen-system-inference-optimization.html) |
| Reproducible benchmarking and regression gates | [.md](03-reproducible-benchmarking.md) | [.html](03-reproducible-benchmarking.html) |

Every table in the writeups is rendered from `benchmarks/results/measured.json`, and every row
carries the date, the commit and the machine it was measured on. The HTML pages open locally in a
browser; only the fonts and the math renderer come from a CDN.
