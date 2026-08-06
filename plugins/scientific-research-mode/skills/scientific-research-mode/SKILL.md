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
  - research operations
  - UX research
  - usability testing
  - product specification
  - SUS UEQ NASA-TLX
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

## Research Repository Operations

Treat the research repository as a governed system of record, not a file dump:

- Assign each question, protocol, evidence item, dataset, artifact, review, insight, decision, and action a stable identifier.
- Maintain lineage from source → claim → analysis → finding → product/scientific decision.
- Store owner, access scope, consent basis, retention period, sensitivity, license, verification state, and revision history.
- Use a controlled taxonomy for method, population, modality, domain, study status, evidence strength, and confidence.
- Deduplicate before reuse and preserve superseded versions rather than silently overwriting them.
- Separate raw restricted data from shareable findings and redact PII before broader access.
- Require explicit governance for consent, privacy, ethics, deletion, and reuse across teams or purposes.
- Make repository search return context, provenance, freshness, and limitations—not isolated quotations.

## UX And Human-Computer Interaction Research

Select methods from the decision being made:

- Use generative research to discover needs, workflows, motivations, mental models, constraints, and problem structure.
- Use evaluative research to assess an existing concept or implementation through usability tests, A/B tests, tree tests, card sorting, accessibility studies, or telemetry.
- Define target participants, exclusions, recruitment channel, sample rationale, tasks, scenarios, success criteria, moderator script, consent, and data-handling plan before sessions.
- Keep observation, participant quotation, interpretation, severity, recommendation, and product decision as separate fields.
- Triangulate self-report, observed behavior, task outcomes, telemetry, and system performance when available.
- Report accessibility barriers and assistive-technology context explicitly rather than averaging them away.

### UX Instruments And Metrics

- SUS: score using the published instrument procedure; report sample size and score uncertainty. Do not reinterpret individual items as standalone validated scales.
- UEQ: preserve the instrument's scale structure and benchmark assumptions; report dimensions rather than only one aggregate.
- NASA-TLX: declare whether raw or weighted scoring is used and do not mix scoring variants in one comparison.
- Pair subjective instruments with task success, completion time, error/recovery count, abandonment, assistance, and accessibility outcomes.
- Predefine primary UX outcomes and distinguish formative findings from confirmatory hypothesis tests.
- Treat synthetic UX datasets as pipeline/teaching fixtures only. Never use synthetic observations to infer actual user behavior or product quality.

## Asynchronous UX Peer Review

Before execution, peer-review participant screeners, research plans, scripts, surveys, card sorts, and task materials. Before publication, peer-review the final report.

- Reviewer comments must identify artifact revision, location, severity, rationale, and suggested resolution.
- Authors own the final decision but must record accepted, rejected, and deferred suggestions with rationale.
- Block execution for unresolved consent, privacy, safety, recruitment-bias, leading-question, or invalid-measure issues.
- Block publication for unsupported claims, missing limitations, broken evidence links, or conclusions broader than the participants/tasks.
- Summaries should include a short purpose statement, 3–4 high-level insights, links to plan/report/evidence, and actionable next steps with owners.

## Product Management And Product-Spec Validation

Connect research to a versioned product decision artifact:

- Require problem, target user, evidence, desired outcome, non-goals, scope, user journey, requirements, constraints, risks, instrumentation, launch criteria, rollback, and unresolved questions.
- Keep a spec format version and positive revision number.
- Reject missing mandatory sections, duplicate section identifiers, unsupported artifact types, and invalid section order.
- Warn—but do not necessarily fail—on empty or implausibly short required sections; a human must resolve warnings before approval.
- Trace every material requirement to research evidence or an explicitly labeled assumption.
- Define falsifiable success and guardrail metrics before implementation.
- Validate desirability, usability, feasibility, viability, safety, privacy, accessibility, and operational support separately.
- After evidence changes, revise the specification rather than rewriting history; preserve decision logs and superseded revisions.

## Research-to-Product Handoff

- Translate findings into opportunities before jumping to features.
- Rank insights by evidence strength, frequency, severity, strategic relevance, and uncertainty.
- Give each action an owner, due date, success signal, dependency, and evidence link.
- Record when product constraints override research recommendations and why.
- Re-evaluate after launch with the same operational definitions used at baseline.

## Safety Boundary

This mode provides research assistance, not autonomous scientific authority. Medical, clinical, biological, chemical, environmental, and other safety-critical conclusions require qualified domain review, applicable ethics approval, and compliance with law and institutional policy.

## Architectural Attribution

AXIM's implementation is original. Its workbench concepts are informed by open-science practice and the public Apache-2.0 OpenScience architecture at https://github.com/synthetic-sciences/openscience, including staged research, specialist critique, artifacts, provenance, and publication workflows. No OpenScience source code or bundled skill text is included here.

Additional public methodological references informing this original AXIM guidance:

- ResearchOps Community Research Repositories Project: https://github.com/researchops/research_repositories — repository taxonomy, governance, privacy, ethics, reuse, and research/data/governance workstreams.
- JupyterLab UX Research: https://github.com/jupyterlab/ux-research — centralized research assets and inclusive asynchronous peer review of screeners, plans, materials, and reports.
- Mohsen Rafiei UX Datasets Collection: https://github.com/mohsen-rafiei/UX_datasets — synthetic UX/HCI datasets using SUS, UEQ, NASA-TLX, telemetry, accessibility, cognitive, and mixed methods; reference fixtures only, subject to its own non-commercial/attribution terms.
- Sourcegraph UX Research Handbook (archived): https://github.com/sourcegraph/handbook/blob/main/content/departments/product/design/research/index.md — generative/evaluative method classification and research-repository practice.
- ProductSpec validation guidance: https://github.com/gokulrajaram/ProductSpec/blob/main/docs/validate-your-first-product-spec.md — versioned specification structure, mandatory-section/order validation, duplicate rejection, and errors-versus-warnings.

These sources are attributed references. AXIM does not bundle or reproduce their templates, datasets, source code, or proprietary content.
