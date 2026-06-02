# AgentSquare Notes

This document is a living note for the AgentSquare project.  
More sections can be added before and after this content over time.

## Agent as Modular Composition

Think of an agent as:

```text
Agent = [Planning] + [Reasoning] + [Tool Use] + [Memory]
```

Example:

```text
Agent A =
[Plan-and-Solve]
[Chain-of-Thought]
[Calculator]
[No Memory]
```

## Recombination vs Evolution

### Recombination: Swap Existing Modules

Recombination means replacing one module with another module that already exists in the current module pool.

Example module pools:

```text
Planning Pool:
  P1 = Plan-and-Solve
  P2 = ReAct
  P3 = Tree Search

Reasoning Pool:
  R1 = Chain-of-Thought
  R2 = Reflection
  R3 = Debate
```

Given a current agent:

```text
[P1, R1, T1, M1]
```

The LLM may suggest:

```text
"Maybe R2 is better than R1."
```

and create:

```text
[P1, R2, T1, M1]
```

or:

```text
[P3, R1, T1, M1]
```

Nothing new is invented.  
It simply replaces one existing module with another existing module.

In short:

```text
Recombination = choose different existing Lego blocks.
```

### Evolution: Create a New Module

Evolution means inventing a new module that did not previously exist in the pool.

Suppose the pool contains:

```text
P1 = Plan-and-Solve
```

The LLM reviews performance history and proposes a new planning strategy, creating a new module:

```text
P*
```

Example:

```text
Original:
  Make a plan then solve.

New (P*):
  Make a plan.
  Rank steps by difficulty.
  Solve easy steps first.
  Verify each step.
```

The planning pool becomes:

```text
P1
P2
P3
P*
```

`P*` did not exist before.  
It was invented and then added to the pool.

In short:

```text
Evolution = invent a new Lego block.
```

## One-Sentence Summary

Recombination:

```text
Replace a module with another module that already exists.
```

Example:

```text
Chain-of-Thought -> Reflection
```

Evolution:

```text
Create an entirely new module and add it to the pool.
```

Example:

```text
Chain-of-Thought -> Chain-of-Thought + Self-Verification + Retry
```

## Why Both Are Needed

If a system only uses recombination and has modules `A, B, C, D`, it can only try combinations of `A, B, C, D` forever.

It cannot discover modules such as `E, F, G` unless those new modules are created first.

Therefore:

- Evolution creates new modules.
- Recombination combines existing modules (including newly evolved ones).

## Soccer Analogy

- Recombination: build a new soccer team by selecting players from the existing player database.
- Evolution: discover and train a brand-new player who was never in the database.
