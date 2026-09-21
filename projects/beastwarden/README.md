**English** · [Tiếng Việt](README.vi.md)

# Beastwarden: a deterministic tactics roguelite

> A browser based turn based grid tactics game in TypeScript, using Vite and Pixi. The simulation
> core is pure, seeded, and deterministic. The test suite enforces the design rather than
> describing it.
>
> > It is also where I direct AI assisted development under rules a machine checks. The other two
> projects talk about that problem. This one has to live with it. The source stays private while
> the game is in development. This page covers the architecture and how I work on it.

---

## Fast facts

- **Engine:** TypeScript, with a Vite and Pixi web client
- **Tests:** 1,993 passing at the last verified baseline
- **Core purity:** no DOM, no `Date.now`, no `Math.random` in the simulation core. This is enforced
  by lint rules and custom guards, not by convention
- **Determinism:** the same seed gives the same everything. The battle forecast must equal what the
  dice actually do
- **Process:** a roadmap of bounded work packages, and a verify gate that must pass before any
  session ends: typecheck, lint, custom guards, the full test run, and a build

## Design decisions, and why

**A pure deterministic core, enforced by tooling.** The simulation in `src/core` is a pure function
of state and seed. That is not taste. A forecast is only honest if the forecast and the battle run
the same code.

The interface can predict a battle outcome by running the same core the battle itself will run. A
test then asserts that the prediction and the real roll never disagree. It is the same reason gen-
system generates at temperature 0. A test against a moving target proves nothing.

**Rules as guards, not comments.** Two custom guards run in CI next to lint and typecheck.

The first bans the "is dead" flag pattern outright. Death is deletion. An entity that no longer
exists cannot be half alive somewhere else in the state.

The second flags any exported symbol that nothing outside the tests imports. It ratchets down from
an explicit allow list, so unused public surface cannot quietly pile up.

A rule a reviewer has to remember is a rule a machine should check instead.

**Closed unions instead of open plugins.** Adding new content, such as a skill, is pure
configuration. Adding a new kind of effect or dice rule is a code change. Every handler that
switches on that type has to acknowledge it before the build passes.

The compiler enumerates the design space. Adding a case without handling it everywhere is a type
error, not a runtime surprise.

**AI assisted, human directed, with the discipline written down.** The game is built in bounded
work packages across AI assisted sessions, under a standing agreement.

The rules above are not negotiable. Every session ends with the full verify gate green. Progress
ledgers get updated, so the next session starts from verified truth instead of optimistic memory.

gen-system goes at that problem from the tool side. Here I am the one giving the instructions and
living with what comes back, which teaches you different things.

## Why it is in here

Same bet as HieuLuat and gen-system, made a third time in a different language and a different
domain: design the correctness property in, then let a machine enforce it.

It is also the only one of the three you can play. Hover a damage forecast, watch the dice land on
exactly that number, and the determinism claim stops being a bullet point.

## Stack

TypeScript. Vite. Pixi for WebGL 2D. Vitest. Custom lint guards. A seeded random number generator
in the simulation core. DragonBones for skeletal animation.

## What is not here, and why

The game is in active development, so the source, the content, and the design documents stay
private for now. The claims above describe what the tooling enforces, and the test count is from
the last verified baseline.
