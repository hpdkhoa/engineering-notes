**English** · [Tiếng Việt](03-reproducible-benchmarking.vi.md)

# Reproducible benchmarking and regression gates

### Frozen baselines, gates, determinism, and the two metrics that measured nothing

> **Context:** I tuned both projects here against fixed, repeatable measurements. gen-system keeps
> its harness and results in [its repository](https://github.com/hpdkhoa/gen-system). HieuLuat is
> deprecated after the company's acquisition. Its harness stayed private, but its rows follow the
> same rules. **What this covers:** the three rules, what a frozen baseline and a gate are, how I
> make runs repeatable and where they are not, and the two times a quality metric turned out to
> measure nothing. Each of those two lessons cost me a campaign.

---

## 1. The three rules

I have broken all three at least once.

1. Measure before and after, every time. I report every change against a recorded baseline.
   Without a baseline I make no claim.
2. Make runs repeatable where the work allows it. Otherwise a rerun moves the number and you
   cannot tell your change from the noise.
3. Tie quality to something objective. Speed bought with silent quality loss is not a win. So I
   measure quality next to performance and never assume it holds.

## 2. Frozen baselines

A baseline is a recorded measurement of the system before a change, tagged with a version and taken
under fixed conditions. It lives in a file.

I report every optimization in both projects against one, so "this change improved throughput" is
a sentence someone else can check.

## 3. Regression gates

Measuring after the fact only helps if somebody looks. A gate makes the regression fail the build
instead.

In gen-system, the harness can diff a benchmark run against a committed baseline. A drift beyond a
tolerance exits non zero. The frozen COBOL baseline works this way. It is a third party COBOL
repository at a pinned commit, with its resolution recall on record. The gate catches a parser
change that lowers that recall, instead of someone finding it weeks later.

The same idea applied to HieuLuat's labeled evaluation sets. I accepted a change to the retrieval
path only if measured quality held or improved on those fixed cases. I rejected a faster index that
quietly dropped recall instead of shipping it.

## 4. Repeatability

Where the work allows it, I make runs deterministic. gen-system generates at temperature 0 with a
fixed seed, and a suite checks that the same prompt gives one unique output across repeated runs.

A difference between two runs then reflects the change you made, not random variation. Where a
component is random, I repeat the runs and report a range instead of a single number.

The pin makes runs likely to repeat. It does not prove they will. The determinism suite passes on a
single prompt. The full generation pipeline still landed on one of two distinct outputs across
repeated runs, on the same model with the same seed. Which one it lands on depends on the state of
the local server, not on anything in the run. That is why every gen-system table in this repository
carries `n` and a range. I do not report a difference of one run in three as a finding.

## 5. Choosing a quality metric that can move

Both projects measure quality directly rather than through a proxy. gen-system got the
choice of metric wrong the first time.

The plan was to report compile pass rate. Does the generated code build? It came back at 100
percent on every run. The engine replaces a failing operation with a stub that compiles. The metric
could not go down, so it measured nothing.

The replacement counts what varies. It counts how much generated logic survived the compile gate
instead of falling back to a stub, and how many repair rounds that took. Details are in
[section 4 of the inference writeup](02-gen-system-inference-optimization.md).

This matters most for quantization work, where the whole risk is silent quality loss. Most
inference writeups can only show a perplexity curve and hope it tracks usefulness. A metric that is
objective but stuck is worse than a proxy, because it looks like evidence. So I check that the
metric can move.

It happened a second time, in the other direction. The verify pass that rereads generated code
scored internal resolution at 100 percent on every Python repository it saw. It counted a call as
internal when any symbol carried its bare name, and then resolved it by that bare name, so it
could not miss. Making the resolver follow a call through the caller's imports turned that 100
into 92.6 and 96.1 on two public repositories. A number that goes down when the tool gets
stricter is a number that measures something. The fixed test for it loads the same repository
with and without a standard library attached and requires the internal recall to be equal.

HieuLuat had the same shape of problem from the other side: a recall that stayed at 0.75 under
every index and every reranker setting. Section 6 of the [legal search
writeup](01-hieuluat-retrieval-optimization.md) reads that flat number as a ceiling of the
embedding model rather than a result about the index. It also names the one measurement, recall at
50, that would settle it.

## 6. Where this shows up

- The [legal search path writeup](01-hieuluat-retrieval-optimization.md): recall and latency
  measured against fixed evaluation sets under this method. Section 6 there is a worked example
  of reading a flat number correctly.
- The [inference writeup](02-gen-system-inference-optimization.md): speed, VRAM, stub rate, and
  repair counts all run through the benchmark harness against frozen baselines.
- The [benchmarks folder](../benchmarks/README.md): the measured tables themselves, and the
  environment I measured them on.

## 7. What the commit order proves, and what it does not

I commit the task set before the first run, so I cannot shape it around the results.

The public gen-system history starts on the day I prepared the repository for release, so a reader
cannot see the weeks before it. What a reader can check is the order inside that history. The
commit that adds the task set comes before the commit that adds the results directory. The task
file also records the frozen date. Each campaign also keeps its raw files with a hash list, so a
reader can rebuild any table. HieuLuat's bench is private, so its rows have no such trail.

Section 5 took the longest to learn. I had a metric for months before I noticed it could only return
one value.

*The figures live in the two project writeups, and they depend on the card in
[ENVIRONMENT.md](../benchmarks/ENVIRONMENT.md). The rules here do not.*
