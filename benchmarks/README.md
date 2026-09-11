# Benchmarks

Every number quoted in the writeups comes from a run recorded here. This folder is the evidence
the rest of the repository rests on.

`results/measured.json` holds the measured tables. It is written by the projects' own harnesses,
never by hand. The tables in the writeups are rendered from this file by `tools/fill_portfolio.py`,
so a table in a writeup and the JSON here cannot drift apart.

## Where each table comes from

**gen-system.** `bench/summarise.py` in the [gen-system repository](https://github.com/hpdkhoa/gen-system)
aggregates the raw benchmark runs under `results/<date>/raw/` into rows and merges them here. Every
gen-system table in this repository comes from one campaign, run on 2026-09-09 at commit
`cfb0bff2` on a clean tree. Each table carries a `_provenance` block with the date, the commit, the
frozen task set and the GPU. Rows carry `n`, and where the harness measured them, the min and max.
A cell showing n/a means the harness did not measure that value. It is not a rounded zero.

The campaign's results directory in the gen-system repository also holds two files that make the
numbers checkable without me in the room:

- `ATTESTATION.md` says what ran, on which commit and machine, which runs were dropped as not
  measured and why, and what did not run.
- `MANIFEST.sha256` lists every raw file with its hash.

**HieuLuat.** Its retrieval bench wrote the index, rerank and embedding rows in August 2026, one
label per configuration, against a fixed evaluation set. That harness lives in the private HieuLuat
repository, so these rows carry the date and the evaluation set but no public commit, no `n`
column, and no manifest. They are reported as the product's harness reported them.

## The environment

[`ENVIRONMENT.md`](ENVIRONMENT.md) records the GPU, the driver, the Ollama and Go versions, the
commit, and the models present when the gen-system campaign was frozen, with the capture time.

## Reading the tables

- `tokens per sec` is decode throughput reported by Ollama for the run, averaged over `n` runs.
- `vram gb` is peak VRAM sampled by the driver during the run.
- `stub rate pct` is the share of model written operations that failed the compile gate twice and
  were replaced by an explicit stub. It is the quality signal; compile pass rate is 100 percent by
  construction and is not a table.
- The SWE-bench tables are localization recall on the first 60 tasks of SWE-bench Verified. They
  are not a solve rate, and the neighbourhood size column is printed next to the recall so the
  width of the net is visible.
