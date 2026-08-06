# OpenMath Reasoning

> Structured mathematical problem solving for AXIM with concise derivations, optional executable checks, and independent verification.

## Overview

This plugin adds an original AXIM skill inspired by the documented methodology behind NVIDIA's OpenMath collection and OpenMathInstruct-1. It does not include or reproduce dataset rows. The skill teaches the agent to separate problem interpretation, derivation, computation, verification, and final presentation.

## Triggered By

- Algebra, arithmetic, geometry, probability, combinatorics, and calculus questions
- Word problems and quantitative reasoning
- Requests to verify a mathematical result or proof
- Problems where Python can safely check arithmetic or symbolic identities

## Method

1. Normalize the problem and list givens.
2. Select a justified method.
3. Derive the result with exact quantities when possible.
4. Use executable computation only as a verification aid.
5. Check the result independently.
6. Present a concise, auditable answer.

## Sources And Attribution

Methodological inspiration:

- NVIDIA OpenMath collection: https://huggingface.co/collections/nvidia/openmath
- NVIDIA OpenMathInstruct-1: https://huggingface.co/datasets/nvidia/OpenMathInstruct-1
- Paper: https://arxiv.org/abs/2402.10176

OpenMathInstruct-1 is governed by the NVIDIA dataset license. This plugin contains original instructional guidance and no copied dataset examples.

## File Structure

```text
openmath-reasoning/
  .axim-plugin/plugin.json
  skills/openmath-reasoning/SKILL.md
  README.md
```
