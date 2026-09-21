**English** · [Tiếng Việt](README.vi.md)

# Snippets: small runnable examples

Small Python files that run on their own with toy data, showing techniques the projects use. None of
the production code, prompts, data or configuration from HieuLuat or gen-system is in here.

They exist so you can check a claim from a writeup yourself, without me handing over anything
private.

Each file runs with a standard Python 3 install. Only the standard library is needed, plus NumPy
where noted. No GPU, database, or network required.

| File | What it shows | From |
|---|---|---|
| `toy_retrieval.py` | Retrieve then rerank over fake vectors, and why you must check an index's recall | [retrieval optimization](../writeups/01-hieuluat-retrieval-optimization.md) |
| `roofline_demo.py` | Naive against blocked matrix multiply, and the memory versus compute intuition | [inference optimization](../writeups/02-gen-system-inference-optimization.md) |

Run either one directly:

```bash
python3 toy_retrieval.py
python3 roofline_demo.py
```

> > These are teaching examples. The real systems are larger and messier. HieuLuat's implementation
> is proprietary, and gen-system's is being prepared for release under Apache-2.0. Run these two
> and the claims in the writeups stop being claims.
