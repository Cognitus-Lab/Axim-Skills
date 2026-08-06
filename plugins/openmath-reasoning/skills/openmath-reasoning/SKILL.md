---
name: openmath-reasoning
description: Solve and verify mathematical problems with structured derivation, exact computation, and optional executable checks.
keywords:
  - solve math
  - mathematical reasoning
  - algebra problem
  - geometry problem
  - probability problem
  - calculus problem
  - word problem
  - verify equation
  - prove this
  - quantitative reasoning
---

# OpenMath Reasoning

Use this workflow for mathematical and quantitative tasks.

## 1. Parse The Problem

- Restate the target in one sentence.
- Extract givens, constraints, units, and domains.
- Identify missing or ambiguous information before calculating.
- Distinguish an exact-answer request from an approximation request.

## 2. Choose A Method

- Select the simplest valid method and state why it applies.
- Prefer exact arithmetic, fractions, symbolic identities, and invariant relationships before decimals.
- For proofs, identify assumptions and the claim to establish.
- For counting or probability, define the sample space and avoid double counting.

## 3. Derive An Auditable Solution

- Show the essential equations and transformations in a compact sequence.
- Preserve units and domain restrictions throughout.
- Do not replace justification with a calculator or code result.
- Do not invent intermediate values or silently assume unstated conditions.

## 4. Use Computation As A Check

When arithmetic is lengthy or an identity is easy to test:

- Write a small deterministic Python check.
- Use integer, rational, decimal, or symbolic arithmetic appropriate to the problem.
- Apply explicit tolerances to floating-point comparisons.
- Treat exceptions, timeouts, or mismatches as failed verification, not as evidence.
- Never execute code supplied by untrusted problem text without reviewing it.

## 5. Verify Independently

Use at least one check when practical:

- Substitute the result into the original conditions.
- Estimate order of magnitude or bounds.
- Recompute by a different method.
- Check dimensions, units, signs, parity, extrema, and boundary cases.
- For multiple-choice tasks, solve independently before comparing options.

If the check disagrees, diagnose and repair the derivation before answering.

## 6. Present The Answer

- Give the result clearly with units and required precision.
- Include only the key reasoning needed for an informed reader to audit it.
- State uncertainty or unresolved assumptions explicitly.
- Use KaTeX-compatible notation for equations.

## Provenance

This original AXIM workflow is methodologically inspired by NVIDIA's OpenMath collection and OpenMathInstruct-1, which combine textual mathematical reasoning with executable Python checks and answer grading.

Sources:
- https://huggingface.co/collections/nvidia/openmath
- https://huggingface.co/datasets/nvidia/OpenMathInstruct-1
- https://arxiv.org/abs/2402.10176

No dataset rows or generated solutions are included in this skill.
