# Paper Summaries

## Table of Contents

1. [SkillGrad: Optimizing Agent Skills Like Gradient Descent](#1-skillgrad-optimizing-agent-skills-like-gradient-descent)
2. [SkillOpt: Executive Strategy for Self-Evolving Agent Skills](#2-skillopt-executive-strategy-for-self-evolving-agent-skills)
3. [SkillFlow: Scalable and Efficient Agent Skill Retrieval System](#3-skillflow-scalable-and-efficient-agent-skill-retrieval-system)

---

## 1. SkillGrad: Optimizing Agent Skills Like Gradient Descent

**ArXiv:** https://arxiv.org/abs/2605.27760  
**Code:** https://github.com/wwwhy725/SkillGrad

> **Background — What is an Agent Skill?**  
> Agent skills provide a lightweight way to adapt LLM agents to specialized domains by storing reusable procedural knowledge in structured files.

> **Current challenges**  
> - These skills are often unreliable, incomplete, or outdated.
> - Existing skill-evolution methods often address these deficiencies through heuristic reflections without an explicit optimization formulation.

> **This work**  
> SkillGrad is a gradient descent-inspired framework for optimizing agent skills. It treats the skill package as a structured parameter and optimizes it in a gradient-descent-like loop:
>
> 1. **Loss evidence** — Task executions produce trajectory-level outcomes that serve as loss signals.
> 2. **Text-based gradients** — Automatic diagnoses convert that evidence into correction directions (analogous to per-example gradients).
> 3. **Momentum** — A momentum agent accumulates recurring diagnostic patterns into a persistent memory overlay, stabilizing optimization across iterations.
> 4. **Parameter update** — An LLM-based patcher applies layer-aware edits to the skill package, producing the next version of the skill.

> **Benchmarks**  
> - **SpreadsheetBench Verified** — Primary in-domain benchmark for spreadsheet manipulation (cell- and sheet-level Excel tasks); hard accuracy on a fixed 120-task test split.
> - **WikiTableQuestions (WikiTQ)** — Out-of-domain transfer benchmark for semi-structured table QA over Wikipedia tables; denotation accuracy on a fixed 70-example subset.

> _Summary placeholder — fill in later._

---

## 2. SkillOpt: Executive Strategy for Self-Evolving Agent Skills

**ArXiv:** https://arxiv.org/abs/2605.23904  
**Code:** https://github.com/microsoft/SkillOpt

> _Summary placeholder — fill in later._

---

## 3. SkillFlow: Scalable and Efficient Agent Skill Retrieval System

**ArXiv:** https://arxiv.org/abs/2504.06188  
**Code:** https://github.com/IBPA/skill-flow

> _Summary placeholder — fill in later._
