# OpenCode Reasoning

> Specification-driven coding for AXIM with algorithm selection, execution-based validation, critique, and repair.

## Overview

This plugin adds an original AXIM skill inspired by the documented methodology behind NVIDIA's OpenCodeReasoning and OpenCodeReasoning-II collections. It does not include or reproduce dataset rows. The skill teaches a disciplined loop for understanding requirements, designing a solution, implementing it, testing behavior, critiquing failures, and repairing defects.

## Triggered By

- Algorithm and data-structure problems
- Python or C++ implementation tasks
- Code generation, debugging, optimization, and review
- Requests to validate correctness or analyze complexity

## Method

1. Convert the prompt into an explicit specification.
2. Select an algorithm and state its invariants and complexity.
3. Implement a complete solution.
4. Execute representative and adversarial tests.
5. Critique the implementation against evidence.
6. Repair and rerun tests before completion.

## Sources And Attribution

Methodological inspiration:

- NVIDIA OpenCodeReasoning-II collection: https://huggingface.co/collections/nvidia/opencodereasoning-ii
- NVIDIA OpenCodeReasoning-2: https://huggingface.co/datasets/nvidia/OpenCodeReasoning-2
- NVIDIA OpenCodeReasoning: https://huggingface.co/datasets/nvidia/OpenCodeReasoning
- Technical report: https://arxiv.org/abs/2504.01943

The cited datasets are licensed under CC BY 4.0, with underlying source datasets subject to their own terms. This plugin contains original instructional guidance and no copied dataset examples.

## File Structure

```text
opencode-reasoning/
  .axim-plugin/plugin.json
  skills/opencode-reasoning/SKILL.md
  README.md
```
