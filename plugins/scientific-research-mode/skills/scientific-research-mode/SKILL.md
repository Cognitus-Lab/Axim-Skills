---
name: scientific-research-mode
description: Conduct rigorous scientific research from question formulation through literature, hypotheses, methods, experiments, analysis, critique, provenance, and publication.
keywords:
  - scientific research
  - research mode
  - literature review
  - hypothesis generation
  - experimental design
  - reproduce results
  - verify citations
  - scientific manuscript
  - data analysis
  - peer review
---

# Scientific Research Mode

Use this skill whenever AXIM Scientific Research Mode is enabled or the user requests a rigorous research workflow.

## Stage 1: Question

- Convert the goal into a specific, answerable research question.
- Define population/system, variables, outcomes, scope, and decision criteria.
- Record assumptions, ambiguities, ethical constraints, and what would falsify the main claim.

## Stage 2: Literature

- Build a reproducible search strategy: databases, query strings, date range, inclusion/exclusion criteria, and deduplication.
- Prefer peer-reviewed primary sources and authoritative datasets.
- Verify every DOI, PMID, arXiv identifier, URL, author, year, and title before citing.
- Record what claim each source supports; a source's existence does not prove claim support.
- Report conflicting findings, publication bias, missing evidence, and freshness limits.

## Stage 3: Hypotheses

- Generate competing, falsifiable hypotheses rather than one favored story.
- State predictions that distinguish alternatives.
- Separate prior knowledge from new inference.
- Identify plausible confounders and causal alternatives.

## Stage 4: Method

Document before execution:

- Study or computational design.
- Inputs, provenance, licenses, and data exclusions.
- Controls, randomization, blinding, leakage prevention, and stopping rules.
- Primary and secondary outcomes.
- Statistical model, effect size, uncertainty interval, multiple-testing correction, and power/sample-size rationale.
- Software, versions, environment, parameters, random seeds, and expected artifacts.
- Failure criteria, rollback, and safety constraints.

## Stage 5: Execution

- Never claim execution without direct tool output.
- Preserve raw outputs and logs; do not overwrite evidence with cleaned results.
- Hash important artifacts.
- Record errors, timeouts, failed runs, excluded runs, and deviations from the protocol.
- Do not silently tune on test data or remove inconvenient observations.

## Stage 6: Analysis

- Validate schema, missingness, outliers, units, assumptions, and data leakage first.
- Report descriptive statistics before inferential claims.
- Include effect sizes and uncertainty, not p-values alone.
- Run sensitivity, robustness, negative-control, and subgroup checks when justified.
- Distinguish exploratory from confirmatory analysis.
- Make plots truthful, labeled, accessible, and reproducible.

## Stage 7: Critique

Perform an adversarial review before synthesis:

- Can the result be explained by leakage, confounding, selection, measurement error, multiple comparisons, or failed controls?
- Do citations support the exact statements and quoted values?
- Are statistical assumptions and uncertainty handled correctly?
- Are results reproducible from the recorded method and artifacts?
- Are conclusions broader than the data justify?

Classify each issue as blocking, major, minor, or informational. Advance only after blocking errors are fixed or explicitly unresolved.

## Stage 8: Synthesis

- Integrate evidence by strength and relevance, not by count.
- Separate findings, interpretation, speculation, and recommendations.
- State limitations, contradictory evidence, uncertainty, and generalizability.
- Never turn absence of evidence into evidence of absence.

## Stage 9: Publication

Produce an auditable package:

- Abstract and structured manuscript/report.
- Methods detailed enough for reproduction.
- Results tied to artifact identifiers.
- Verified references.
- Figures/tables with source data and regeneration instructions.
- Data/code/material availability and ethical statements where applicable.
- Limitations and negative results.

## Required Provenance

For every important claim or result, record:

- Evidence source and locator.
- Claim supported.
- Verification state.
- Tool or computation used.
- Parameters, version, seed, timestamp, and artifact digest.
- Known limitations and reviewer decision.

## Safety Boundary

This mode provides research assistance, not autonomous scientific authority. Medical, clinical, biological, chemical, environmental, and other safety-critical conclusions require qualified domain review, applicable ethics approval, and compliance with law and institutional policy.

## Architectural Attribution

AXIM's implementation is original. Its workbench concepts are informed by open-science practice and the public Apache-2.0 OpenScience architecture at https://github.com/synthetic-sciences/openscience, including staged research, specialist critique, artifacts, provenance, and publication workflows. No OpenScience source code or bundled skill text is included here.
