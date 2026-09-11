# Tuning local LLM inference for a code engine

### GPU offload, streaming, quantization, and two models sharing one consumer card

> **Context:** gen-system makes an AI model's beliefs about code visible and checkable. It grounds
> the model in a graph built from the AST, and verifies the output from outside. See the
> [project page](../projects/gen-system/README.md). The source is being prepared for release under
> Apache-2.0. **What this covers:** tuning its inference layer. The quality test is objective: the
> generated code either builds and passes its tests, or it does not. Section 4 explains why the
> obvious version of that test is useless, and what replaced it.

---

## 0. The machine

One consumer GPU, not a lab machine. An NVIDIA RTX 4060 Ti with 16 GB, running Ollama, with a
planner model and a coder model sharing the card.

The production roles are `qwen3:14b` for planning and `qwen2.5-coder:14b` for code. The
quantization study uses `deepseek-coder-v2:16b-lite-instruct` at Q4_K_M, Q5_K_M, and Q8_0.

Decoding is deterministic: temperature 0, seed 42, top_p 1. That is verified, not assumed, and
section 6 says where the pin stops holding.

The exact GPU, driver, runtime versions, commit and model list are captured by the harness into
[ENVIRONMENT.md](../benchmarks/ENVIRONMENT.md). Every table in section 6 carries the commit and
date it was measured at, and is rendered from
[`benchmarks/results/measured.json`](../benchmarks/results/measured.json). The tables are the
source of every number. Where the text below reads a number out of a table, the table wins, and
the text is rewritten when the table changes.

## 1. Where it started

All inference went through one client to a local Ollama runtime. The picture was consistent. It was
correct, it was deterministic, and it was completely untuned.

- **Every call waited for the whole answer.** The client blocked until generation finished. A long
  code generation paid the full wait before the first token appeared, and nothing downstream could
  start early.
- **There were no GPU controls.** The request options set temperature, seed, and top_p. Nothing set
  how the GPU ran the model. No layer offload, no context size, no batch size. The runtime ran at
  its defaults.
- **The quantization was fixed.** The model tag carried one quant. That was a choice, never a
  measurement.
- **Two models shared 16 GB.** This is why the system needs keep alive and a long timeout. A
  model reload could land in the middle of a run, and nothing measured how much it cost.

The correctness layer was already strong. The performance layer was untouched, and that layer is
the actual job.

## 2. Move 1: expose the GPU controls

All model traffic passes through one function. Three settings are now read from the environment and
sent with every request:

| Variable | What it controls |
|---|---|
| `OLLAMA_NUM_GPU` | How many layers run on the GPU. This is the biggest lever. With two 14B models on 16 GB, whether the layers fit or spill to the CPU is the difference between fast and unusable. |
| `OLLAMA_NUM_CTX` | Context window size. The KV cache grows with it. Prompts here are large, so this trades VRAM for capability. |
| `OLLAMA_NUM_BATCH` | Prompt processing batch size, which sets prefill speed. |

Each setting is left out of the request when its variable is unset. A machine that sets none of
them sends exactly the same request as the old client did. That property is what keeps the
measurement honest. The tuned and untuned runs differ only by the setting being tested.

The bench driver sweeps `OLLAMA_NUM_GPU` and samples peak VRAM at each step.

## 3. Move 2: stream the output

Streaming sits behind `OLLAMA_STREAM`. The reader consumes the stream and joins the fragments back
into one string. That string is identical to what the old buffered path returned.

That matters more than it sounds. Everything downstream sees the same input either way: the JSON
extraction, the rule that generated function bodies must come back alone, and the determinism
check. Transport is not allowed to change meaning. A test asserts one unique output across five
identical streamed responses.

Buffered stays the default. Streaming is opt in until the measurement says otherwise.

What gets measured is time to first token and total time, with streaming on and off, on the same
prompt, three runs each.

## 4. Move 3: quantization, and the broken metric underneath it

Quantization is an experiment here, not a fixed choice. The same model runs at Q4_K_M, Q5_K_M, and
Q8_0 on the coder role, with the planner held fixed. Each run measures speed, VRAM, and quality.

The quality axis is where this got interesting, and where the first version of this writeup was
wrong.

**The obvious metric does not work.** The plan was to report compile pass rate. Generated code
either builds or it does not. Every run came back at 100 percent.

That is not because the model is perfect. It is **by construction**. When a model written operation
fails to compile, the engine sends it back to the model with the build error. If it still fails,
the engine replaces the body with an explicit `not implemented` stub. The stub compiles. The
service always builds.

A metric that cannot go down measures nothing. A quantization that badly damaged the output would
still score 100 percent.

**What replaced it.** The instrumentation now counts what actually changes. All of it comes from
the same code path production uses:

| Metric | What it catches |
|---|---|
| `ops_stubbed` and `stub_rate_pct` | How much model written logic failed the compile gate and fell back to a stub. This is the real quality signal. |
| `op_repair_attempts` and `op_repair_successes` | Repair rounds at the operation level, capped at 2 before the stub. A weaker quant should need more. |
| `heal_attempts_total` and `heal_success` | Repair rounds at the task level, capped at 3. |
| `go_test_pass` | Whether the generated backend passes its own tests, including one that fails if an operation panics at runtime. |
| `verify_findings` | What the project's own code understanding engine finds when it rereads the generated backend: unresolved calls, orphan operations, read operations that write. |
| `prompt_tokens` and `wall_s` | Cost per run. |

Compile pass rate is still reported. It is no longer the headline, and the reason it is useless is
now written down instead of hidden.

The task set is five fixed application ideas. They were frozen and committed before the first run,
so they cannot be tuned to fit the results.

## 5. Move 4: two models, one card

Two models competing for 16 GB is a real design problem with more than one good answer. Three
strategies run against the same frozen task set:

| Strategy | What it is | What it costs |
|---|---|---|
| A. Sequential with keep alive | The production default. One model resident at a time. | A model reload when the roles swap. Measured as the load time difference. |
| B. Both resident | Keep alive never expires, so both models should stay warm. | VRAM headroom, and speed under contention. Whether both even fit is itself a result, and section 6 gives the answer. |
| C. One shared model | The coder model plans as well, so nothing ever swaps. | Planning quality, visible as stub rate, repair counts, and extra entities. |

One clarification belongs everywhere this is described. **There is no scheduler.** "Sequential
scheduling with keep alive" means Ollama's own keep alive, two model roles, and measurement of what
that costs. No scheduling code was written. Claiming otherwise would not survive a reading of the
source.

## 6. Results

<!--measured:gen-->
### Measured results

*Rendered from `benchmarks/results/measured.json`. Every number below comes from the project's own harness on the machine described in section 0.*

**GPU-layer offload: tokens/sec vs VRAM**

| gpu layers | tokens per sec | vram gb | n | tok s min | tok s max |
|---|---|---|---|---|---|
| 20 | 7.9 | 4.7 | 3 | n/a | n/a |
| 30 | 10.2 | 6.3 | 3 | n/a | n/a |
| 40 | 14.3 | 8.0 | 3 | n/a | n/a |
| default | 30.8 | 9.4 | 3 | n/a | n/a |

*Measured 2026-09-09 · commit `cfb0bff21748` · bench/tasks.json (frozen 2026-08-27).*

**Streaming: time-to-first-token**

| config | ttft ms | total latency s | n | ttft min | ttft max |
|---|---|---|---|---|---|
| stream off (buffered) | 1883.7 | 1.88 | 3 | 1876.4 | 1897.5 |
| stream on (NDJSON) | 127.4 | 1.88 | 3 | 126.7 | 128.0 |

*Measured 2026-09-09 · commit `cfb0bff21748` · bench/tasks.json (frozen 2026-08-27).*

**Quantization sweep: speed vs VRAM vs generation quality**

| quant | tokens per sec | vram gb | ops total | stub rate pct | op repair attempts | heal attempts | go test pass | n | tok s min | tok s max | runs not measured |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Q4_K_M | 125.2 | 11.5 | 25.3 | 91.1 | 46.7 | 0.0 | 5.0 | 3 | 124.5 | 125.6 | 0 |
| Q5_K_M | 114.4 | 12.8 | 23.7 | 83.8 | 43.0 | 0.0 | 5.0 | 3 | 114.0 | 114.6 | 0 |
| Q8_0 | 41.3 | 15.3 | 24.0 | 76.7 | 40.0 | 3.0 | 4.7 | 3 | 41.0 | 41.5 | 0 |
| production | 30.7 | 9.6 | 3.0 | 44.4 | 2.7 | 0.0 | 5.0 | 3 | 30.7 | 30.7 | 0 |

*Measured 2026-09-09 · commit `cfb0bff21748` · bench/tasks.json (frozen 2026-08-27).*

**Two-model serving strategies**

| strategy | reload cost s | tokens per sec | ops total | stub rate pct | heal attempts | go test pass | n | runs not measured |
|---|---|---|---|---|---|---|---|---|
| A-sequential-keepalive | 1.98 | 30.7 | 3.0 | 0.0 | 0.0 | 5.0 | 3 | 0 |
| B-both-resident | 1.96 | 30.7 | 3.0 | 66.7 | 0.0 | 5.0 | 3 | 0 |
| C-single-shared | 1.97 | 30.7 | 3.0 | 0.0 | 0.0 | 5.0 | 3 | 0 |

*Measured 2026-09-09 · commit `cfb0bff21748` · bench/tasks.json (frozen 2026-08-27).*

**Understand benchmark: public repos at pinned commits**

| repo | files | parse errors | internal recall pct | call edges internal | cfgs total | cfgs with issue |
|---|---|---|---|---|---|---|
| cobolcraft | 268 | 0 | 100 | 298 | 330 | 0 |
| go-chi | 84 | 0 | 100 | 1212 | 411 | 0 |
| gorilla-mux | 17 | 0 | 100 | 274 | 158 | 0 |
| spf13-cobra | 36 | 0 | 100 | 984 | 403 | 0 |

*Measured 2026-09-09 · commit `cfb0bff21748` · bench/tasks.json (frozen 2026-08-27).*

**SWE-bench Verified: localization recall (not a solve rate)**

| hops | file recall mean | hit rate pct | mean neighbourhood files | median neighbourhood files | n tasks |
|---|---|---|---|---|---|
| 0 | 0.615 | 63.3 | 201.933 | 92.5 | 60 |
| 1 | 0.615 | 63.3 | 262.5 | 177.5 | 60 |
| 2 | 0.674 | 70.0 | 464.8 | 421.5 | 60 |

*Measured 2026-09-09 · commit `cfb0bff21748` · SWE-bench Verified, princeton-nlp, frozen sha256 fcef3a49f31e.*

**SWE-bench Verified: localization recall by repository**

| repo | hops | file recall mean | hit rate pct | seeds matched pct | n tasks |
|---|---|---|---|---|---|
| astropy/astropy | 2 | 0.716 | 77.3 | 100.0 | 22 |
| django/django | 2 | 0.649 | 65.8 | 92.1 | 38 |

*Measured 2026-09-09 · commit `cfb0bff21748` · SWE-bench Verified, princeton-nlp, frozen sha256 fcef3a49f31e.*

**SWE-bench Verified: can the parsers read the repositories**

| repo | files parsed | parse errors | internal recall pct | call edges internal |
|---|---|---|---|---|
| astropy/astropy | 786 | 0 | 92.6 | 22851 |
| django/django | 2572 | 0 | 96.1 | 50596 |

*Measured 2026-09-09 · commit `cfb0bff21748` · SWE-bench Verified, princeton-nlp, frozen sha256 fcef3a49f31e.*

<!--/measured-->

### What the numbers say

| Change | Effect | What is measured |
|---|---|---|
| GPU controls | Speed and fit on one card | Tokens per second and peak VRAM against offloaded layers |
| Streaming | Lower time to first token | Time to first token and total time, on and off, three runs |
| Quantization | Speed and VRAM against quality | Speed, VRAM, stub rate, repair counts, test pass |
| Two model strategies | Serving without reloads | Reload cost, speed, stub rate across three strategies |

Every table above comes from one campaign, run on 2026-09-09 at one clean commit, in one results
directory. The manifest and the attestation sit beside the raw files in the gen-system
repository. Three earlier campaigns led to it. The first ran with a dirty tree. The second and
third were one run that crossed midnight and split into two directories, which is how a date bug
in the drivers was found. Each of those found something the tables now reflect. Nine things are
worth reading out of the tables.

**The quality metric moved.** Stub rate is different for every quantization. That was the
whole point of replacing compile pass, which was 100 percent by construction. Gate 2 of the plan
asked for at least one metric that differs across quants. It does, and it has done so in every
campaign at every commit.

**The study model wrote very little code that compiled.** DeepSeek Coder V2 Lite at Q4_K_M
proposed about 25 operations per run and almost every one fell back to a stub after two repair
rounds. Q8_0 did better, but it still stubbed most of what it wrote. The production coder model
proposed far fewer operations per run, and about half of them survived. The rows are not on the
same footing: one rests on about 25 operations, the other on 3. The `ops_total` column is
there so the reader can see that before comparing stub rates.

**The task level repair loop does fire, rarely.** In most runs `heal_attempts` is 0 and
`go_test_pass` is 5 of 5, both by construction: stubs compile and pass. In one Q8_0 run the
generated backend built, its own tests failed, and the task level loop ran nine times. It took
four campaigns to see that column move twice. It is reported so nobody reads a 0 as a result.

**Speed and quality moved in opposite directions.** Q4_K_M was about three times faster than Q8_0
in tokens per second and used about 4 GB less VRAM. It also produced almost nothing that
compiled. For this pipeline, on this card, the faster quant is not the cheaper one.

**Strategy B once measured nothing, and the harness now catches that.** In the first campaign
the driver set `OLLAMA_KEEP_ALIVE=-1`, the request door sent it as the string "-1", Ollama
rejected every request, and the offline fallback schema built green. The first aggregation showed
B with a 0 percent stub rate, the best row in the table. Three fixes followed. The door sends a
bare integer as a number. The pipeline marks an idea with zero completed model requests as not
measured. The aggregator drops such runs and counts them in `runs_not_measured`. That column is
0 on every row above.

**The three strategies are the same strategy on this card.** Reload cost and tokens per second
are identical across A, B and C. The `ollama ps` capture at the end of the B run shows one
resident model, not two. The planner is 9.3 GB on disk and the coder 9.0 GB, and each needs its
KV cache and runtime beside it, so the pair does not fit in 16 GB together. "Both resident"
degrades to what A does. Whether both fit was itself a result, and the answer is no.

**Pinned sampling gives two outputs, not one.** Temperature 0, seed 42, and top_p 1 were set on
every request. On the production pair, every run of every campaign landed on one of exactly two
outputs: one with two of three operations stubbed, one with none. In one campaign strategy A got
the first output three times and B the second. In the next campaign the assignment flipped: A got
the second three times and B the first. Which output a run lands on depends on server state, not
on the strategy. With three operations per run, one flip moves the stub rate by a third. That is
why every row carries n and a range, and why the stub rate column in the strategies table should
not be read as a strategy effect. A determinism pin on a local server is a strong preference,
not a proof.

**A second metric that was 100 percent by construction.** Until this campaign the verify pass
counted a call as internal when any symbol carried its bare name. It then resolved the call by
that bare name. So a Python repository always scored 100 percent internal resolution. The resolver now
follows a package qualified call through the caller's imports, and a call it cannot place stays
unresolved. On the same SWE-bench repositories the internal resolution is now 92.6 percent for
astropy and 96.1 percent for django. The internal edge counts on the Go repositories dropped by
up to a seventh. Calls into packages the index does not hold are now external instead of
captured. Those are real numbers replacing a tautology. The same change reduced the
verify findings on generated backends from several hundred per run, almost all standard library
calls, to zero.

**SWE-bench: read the neighbourhood column before the recall column.** The table is localization
recall on the first 60 tasks of SWE-bench Verified in instance order, 22 astropy tasks and 38
django tasks. It is not a solve rate. Hop 1 adds nothing over hop 0. The seed identifiers from
the issue text already sit in the gold files, or they do not. Hop 2 raises recall while the
median neighbourhood grows to about 420 files, which is more than half of astropy and a sixth of
django. A net that wide catches gold files by width. The tighter resolver shrank that
neighbourhood by about a tenth with no change in recall, which says the width was never doing
the work. The seed rule takes up to 80 identifiers from the issue text by exact name. In a
repository of 2,500 files a name like `Model` matches in hundreds of places. The metric is
honest about that because the neighbourhood size is printed next to it. A tighter seed rule is
the next thing to build, and the number will drop when it is built.

## 7. Future work

Two directions, neither of them claimed as done.

The first is a hand written token generation kernel measured by this same harness: a matrix
times vector product over the coder model's quantized weights, profiled with Nsight, compared
against the tokens per second Ollama reaches in the quantization table. The roofline for that is
one division, memory bandwidth over bytes of weights read per token, and the production row above
already sits at 96 percent of it. The kernel's job is to reproduce that ceiling with my own code
and say where the remaining distance lives.

The second is feeding the rendered control flow graphs back to the model as repair context, behind
a flag, and measuring it properly. I expect no effect on Go repair, because the compiler already
tells the model what is wrong. I expect a possible effect on COBOL and on belief enrichment, where
there is no compiler to lean on. The result gets published either way, including if it is null.

## 8. What I would want a reader to take from this

Not "I tuned some settings." The untuned runtime was an opportunity. Each control became a measured
experiment. When the headline quality metric turned out to be 100 percent by construction, the
response was to say so and build a metric that can move.

The broken metric was not the only thing this pass turned up. The rest is the part I would actually
want read. Three stories, one shape.

**Two determinism bugs, found by reading my own code.** Neither came from a bug report. Determinism
is the load bearing claim of this system: temperature 0, fixed seed, identical output. Symbol
resolution broke it. It took the first match while walking a Go map, and Go randomizes that order.
Two exported symbols sharing a short name could resolve differently between runs, and the call
graph quietly changed shape.

I fixed it, wrote tests, and moved on. Then it turned out there was a second resolver on a
different code path with the same flaw, plus a worse one. It had no tier preference at all, so a
standard library symbol could capture a project call. My tests had gone through the fixed path and
passed while the bug sat next door. The second fix deletes the duplicate rather than repairing it.
Two functions answering the same question differently is how the split happened.

**Six tests that passed for the wrong reason.** A group of frontend tests had been failing. My first
read was that they looked environmental. They were not. Three failed because a test helper matched
nodes by name, while call nodes carry their identifier in a different field. Every lookup silently
found nothing, and a correct frontend took the blame. Two were a formatting artifact that rendered
a flowchart label as broken text. One asserted a rule that a later version had deliberately
replaced. Only one was genuinely platform specific.

**A resolver that could not miss.** The verify pass that rereads generated code reported 100
percent internal resolution on every Python repository. At the same time it reported hundreds of
unresolved calls on every generated backend. Both numbers came from the same shortcut: a call was matched
by its bare name against every symbol the index held. Following a call through the caller's
imports instead turned the 100 into 92.6 and 96.1 on two public repositories, and turned the
hundreds of findings into zero. Section 6 has both numbers.

All three stories have the same shape, and that shape is the point. **The failure was not a wrong
answer. It was a confident one.** A metric stuck at 100 percent. A test suite that was green on the
path I happened to test. Six red tests I was ready to explain away as someone else's problem. A
resolver that could not miss.

None of that is caught by running the thing and watching it work. It is caught by going back and
asking what each number would look like if it were lying to you. The tables in section 6 are only
worth what that habit is worth.

*All timings are native local GPU measurements taken through the project's own harness, on the
machine described in section 0. The method is in [reproducible benchmarking](03-reproducible-benchmarking.md).
Absolute speed depends on the GPU; the shape of each trade off is the part that transfers.*
