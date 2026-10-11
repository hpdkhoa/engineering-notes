**English** · [Tiếng Việt](README.vi.md)

# Benchmarks

This folder holds the measured tables that the writeups quote.

`results/measured.json` holds the tables. Each project's own benchmark harness wrote its rows.

## Where each table comes from

**gen-system.** `bench/summarise.py` in the [gen-system repository](https://github.com/hpdkhoa/gen-system)
aggregates the raw benchmark runs under `results/<date>/raw/` into rows and merges them here. Every
gen-system table here comes from one campaign on 2026-09-09, run on a clean tree. Each table
states its date, its task set and its GPU. Rows carry `n`, and where the harness measured them, the min and max.
A cell showing n/a means the harness did not measure that value. It is not a rounded zero.

The gen-system repository keeps the raw files of that campaign, a note on what ran and what I
dropped, and a hash for each file. With them, anyone can rebuild the rows.

**HieuLuat.** Its retrieval bench wrote the index, rerank and embedding rows in August 2026, one
label per configuration, against a fixed evaluation set. That harness is private, so these rows show only the
date and the evaluation set. They have no run count and no range.

## The environment

[`ENVIRONMENT.md`](ENVIRONMENT.md) records the GPU, the driver, the Ollama and Go versions, and
the models on the machine that ran the gen-system campaign.

## Reading the tables

- `tokens per sec` is the decode throughput that Ollama reports for the run, averaged over `n` runs.
- `vram gb` is the peak VRAM that the driver sampled during the run.
- `stub rate pct` is the share of model written operations that failed the compile gate twice, so
  gen-system put an explicit stub in their place. It is the quality signal. The compile pass rate is
  100 percent by construction, so no table shows it.
- The SWE-bench tables are localization recall on the first 60 tasks of SWE-bench Verified. They are not a solve rate. The neighbourhood size column sits next to the recall, because a recall
number means little until you know how many files the search returned.
