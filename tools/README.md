# tools

Notes for the author. These scripts rebuild parts of the portfolio on my own machine.

`fill_portfolio.py` runs where the private repositories live. It captures the environment with
`nvidia-smi` and `ollama list`, and injects the tables from `benchmarks/results/measured.json`
between the `<!--measured:...-->` markers in the writeups. It never copies source into this
repository. `--check` reports anything left unfilled.

`regen_writeup_html.py` rebuilds the HTML twin of each writeup, in English and Vietnamese. Run it
after `fill_portfolio.py`. Edit the markdown, never the HTML, then rerun it.

`check_tone.py` checks every `.md` and `.html` against my writing rules. The rules: no dashes as
punctuation, sentences of 28 words or fewer, active voice in English and Vietnamese, no assurance
words and no AI tone. Run `python tools/check_tone.py` before each commit. It exits 1 on any hit.
