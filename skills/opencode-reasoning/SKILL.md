---
name: opencode-reasoning
description: Generate, test, critique, and repair code using explicit specifications, invariants, complexity analysis, and execution evidence.
keywords:
  - solve coding problem
  - code reasoning
  - algorithm problem
  - competitive programming
  - generate code
  - debug code
  - critique code
  - optimize algorithm
  - python solution
  - c++ solution
---

# OpenCode Reasoning

Use this workflow for algorithmic coding, implementation, debugging, and code critique.

## 1. Build The Specification

Before coding, extract:

- Inputs, outputs, types, ranges, and constraints.
- Required interface, language, environment, and dependencies.
- Time and memory expectations.
- Edge cases, invalid states, and ambiguous requirements.

Do not infer missing constraints silently. State assumptions or inspect the workspace when possible.

## 2. Design Before Implementation

- Choose the simplest algorithm that satisfies the constraints.
- State the key invariant or correctness argument.
- Estimate time and space complexity.
- Identify overflow, indexing, mutability, concurrency, and recursion-depth risks.
- Prefer standard-library components and existing project conventions.

## 3. Implement Completely

- Produce runnable code, not pseudocode, unless requested.
- Preserve the required function signature and I/O format.
- Separate parsing, core logic, and presentation when useful.
- Avoid unnecessary abstraction and hidden global state.
- Handle boundary conditions explicitly.

## 4. Validate With Execution

Create tests from the specification rather than from the implementation:

- Smallest and largest valid inputs.
- Empty, singleton, duplicate, sorted, reverse, and degenerate cases as applicable.
- Cases that distinguish the chosen algorithm from common incorrect approaches.
- Randomized differential checks against a simple reference implementation when feasible.
- Existing project tests and linters.

A passing happy-path example is not sufficient evidence.

## 5. Critique Against Evidence

Review the candidate independently:

- Does every requirement map to code?
- Is the invariant maintained?
- Are complexity claims accurate?
- Can integer overflow, precision loss, stale state, or off-by-one errors occur?
- Does the code mutate inputs unexpectedly?
- Are error and timeout results being mistaken for success?

Classify findings as confirmed defects, risks, or style improvements. Do not invent failures.

## 6. Repair And Revalidate

- Fix the root cause, not only the observed example.
- Add a regression test for each confirmed defect.
- Rerun relevant tests after every repair.
- Stop only when tests pass or clearly report the remaining blocker.

## Response Format

For nontrivial tasks, provide:

1. Approach and invariant.
2. Complexity.
3. Implementation or applied workspace changes.
4. Verification evidence.
5. Remaining assumptions or limitations.

## Provenance

This original AXIM workflow is methodologically inspired by NVIDIA's OpenCodeReasoning and OpenCodeReasoning-2 datasets, which emphasize reasoning-rich code generation, execution-derived pass rates, critique judgments, and iterative improvement for Python and C++.

Sources:
- https://huggingface.co/collections/nvidia/opencodereasoning-ii
- https://huggingface.co/datasets/nvidia/OpenCodeReasoning-2
- https://huggingface.co/datasets/nvidia/OpenCodeReasoning
- https://arxiv.org/abs/2504.01943

No dataset rows, benchmark questions, generated solutions, or critiques are included in this skill.
