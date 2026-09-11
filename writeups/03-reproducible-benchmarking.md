# Reproducible benchmarking and regression gates

### The method that makes every other number in this repository worth reading

> **Context:** both projects here are tuned against fixed, repeatable measurements: gen-system,
> whose harness and results are in [its repository](../projects/gen-system/README.md), and
> HieuLuat, whose harness is private but whose rows follow the same rules. **What this covers:**
> the three rules, what a frozen baseline and a gate are, how repeatable runs are made and where
> they are not, and the two times a quality metric turned out to measure nothing. An optimization
> without a before number is a guess. A benchmark you cannot reproduce is a story.

---

## 1. The three rules

Performance work is only as good as its measurement. Three rules cover all of it.

1. **Measure before and after, every time.** Every change is reported against a recorded baseline.
   No baseline, no claim.
2. **Make runs repeatable where the work allows it.** That is what turns a measurement into
   evidence. You want to measure the system, not sample noise.
3. **Tie quality to something objective.** Speed bought with silent quality loss is not a win. So
   quality gets measured next to performance, never assumed to hold.

## 2. Frozen baselines

A baseline is a recorded measurement of the system before a change, tagged with a version and taken
under fixed conditions. It is stored, not remembered.

Every optimization in both projects is reported against one. That is what makes a sentence like
"this change improved throughput" checkable instead of something you have to take on trust.

## 3. Regression gates

The stronger version of "measure after" is to make a regression fail the build automatically.

In gen-system, a benchmark run can be diffed against a committed baseline, and a drift beyond a
tolerance exits non zero. The frozen COBOL baseline works this way: a third party COBOL repository
at a pinned commit, whose resolution recall is recorded. A parser change that lowers that recall
is caught by the gate, not found weeks later.

The same idea applies to HieuLuat's labeled evaluation sets. A change to the retrieval path is
accepted only if measured quality holds or improves on those fixed cases. A faster index that
quietly drops recall is rejected rather than shipped.

## 4. Repeatability

Where the work allows it, runs are made deterministic. gen-system generates at temperature 0 with a
fixed seed, and a suite checks that the same prompt gives one unique output across repeated runs.

The payoff is that a difference between two runs reflects the change you made, not random
variation. Where a component is genuinely random, the honest answer is repeated runs and a reported
range, not a single number.

The pin is a strong preference, not a proof. The determinism suite passes on a single prompt. The
full generation pipeline still landed on one of two distinct outputs across repeated runs, on the
same model with the same seed. Which one it lands on depends on the state of the local server,
not on anything in the run. That is why every gen-system table in this repository carries `n` and
a range. A difference of one run in three is not reported as a finding.

## 5. Choosing a quality metric that can actually move

Both projects measure quality directly rather than through a proxy. That is the useful part. But
choosing the metric is harder than it looks, and gen-system got it wrong the first time.

The plan was to report compile pass rate. Does the generated code build? It came back at 100
percent on every run. Not because the model was perfect, but because the engine replaces a failing
operation with a stub that compiles. The metric could not go down, so it measured nothing.

The replacement counts what actually varies: how much generated logic survived the compile gate
rather than falling back to a stub, and how many repair rounds that took. Details are in
[section 4 of the inference writeup](02-gen-system-inference-optimization.md).

This matters most for quantization work, where the whole risk is silent quality loss. Most
inference writeups can only show a perplexity curve and hope it tracks usefulness. A metric that is
objective but stuck is worse than a proxy, because it looks like evidence. So the lesson is not
simply to pick an objective metric. It is to check that the metric can actually move.

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
embedding model rather than a result about the index, and names the one measurement, recall at
50, that would settle it.

## 6. Where this shows up

- The [legal search path writeup](01-hieuluat-retrieval-optimization.md): recall and latency
  measured against fixed evaluation sets under this method. Section 6 there is a worked example
  of reading a flat number correctly.
- The [inference writeup](02-gen-system-inference-optimization.md): speed, VRAM, stub rate, and
  repair counts all run through the benchmark harness against frozen baselines, with the
  provenance of every table printed under it.
- The [benchmarks folder](../benchmarks/README.md): the measured tables themselves, the
  environment they were taken on, and where the manifest and attestation for the gen-system
  campaign live.

## 7. What I would want a reader to take from this

Reproducible measurement is not paperwork. It is what makes the rest of this repository evidence
instead of assertion.

I build the baseline first. I commit the task set before the first run, so it cannot be tuned to
fit the results. I gate on a quality metric and keep runs repeatable. Then when I say a change made
something faster while quality held, there is a number behind every word.

One honest note on that proof. The public gen-system history starts on the day the repository was
prepared for release, so a reader cannot see the weeks before it. What a reader can check is the
order inside that history: the commit that adds the task set comes before the commit that adds the
results directory. The frozen date is also written inside the task file. Each campaign also ends
with an attestation and a manifest. The manifest lists every raw file with its hash. So the
numbers in the writeups can be traced to files and not to memory. HieuLuat's rows cannot offer
that trail, because the harness is private, and the tables say so instead of implying otherwise.

The part that took longest to learn is in section 5. Having a metric is not the same as having a
metric that works.

*This writeup describes method. The figures live in the project writeups and depend on hardware.
The method is the part that transfers.*
