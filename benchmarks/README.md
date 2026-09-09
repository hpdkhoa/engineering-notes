# Benchmarks

Every number quoted in the writeups comes from a run recorded here.

`results/measured.json` holds the measured tables. It is written by the projects' own
harnesses, never by hand.

- gen-system: `bench/summarise.py` in the gen-system repository aggregates the raw benchmark runs
  under `results/<date>/raw/` into rows and merges them here. Each results directory in that
  repository also carries a manifest with a hash for every raw file. It carries an attestation
  too, which says what ran, what did not, and what was dropped.
- HieuLuat: its retrieval bench writes the index, rerank and embedding rows the same way, one label
  per configuration, against a fixed evaluation set.

The tables in the writeups are rendered from this file, so a table in a writeup and the JSON here
cannot drift apart.

Each table carries a `_provenance` block: the date, the source commit, the frozen task set, and the
GPU. Rows carry `n` and, where the harness measured them, the min and max. A cell showing n/a means
the harness did not measure that value. It is not a rounded zero.

`ENVIRONMENT.md` records the GPU, the driver, and the installed models the runs were taken on.
