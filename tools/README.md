# tools

Notes for the author. These scripts rebuild parts of the portfolio on my own machine.

`fill_portfolio.py` runs where the private repositories live. It captures the environment with
`nvidia-smi` and `ollama list`, and injects the tables from `benchmarks/results/measured.json`
between the `<!--measured:...-->` markers in the writeups. It never copies source into this
repository. `--check` reports anything left unfilled.

`regen_writeup_html.py` rebuilds the HTML twin of each writeup, in English and Vietnamese. Run it
after `fill_portfolio.py`. Edit the markdown, never the HTML, then rerun it.
