# Main-study candidate after the access and calibration pilot

Prepared November 5, 2026. This is a candidate specification, not a frozen main study or a completed sprint contribution.

## The contribution to pursue

Measure when a multi-agent monitor's safety decision is supported by its execution evidence, while distinguishing three failures: insufficient evidence, incorrect interpretation, and unusable output format. Compare explicit completeness information, abstention, and selective recovery, including the cost to compliant workflows.

The resource-quota generator is a calibration tool, not enough on its own for a strong final entry. A fully machine-checkable quota should be enforced by code in a deployment. A model's success on our two constructed pairs cannot establish robust multi-agent control, and a weak model's failure does not establish a general monitoring impossibility beyond the intentionally ambiguous inputs.

## What the pilot changes

- Incomplete reasoning outputs at 512 tokens required a separate integration pilot. These are infrastructure outcomes, not safety findings.
- The matched-budget pilot gives every model up to 4,096 output tokens. Exact model aliases, prompts, raw responses, token usage, request hashes and errors are recorded.
- Identical observations are evaluated once and their recorded response is reused across the compliant/violating counterfactual worlds. Those graded views must never be treated as independent trials.
- Output-contract compliance and substantive correctness need separate reporting. An exploratory sensitivity analysis accepts one surrounding JSON fence; it does not extract a favourable verdict from conflicting answers or use another model to repair them.
- Stronger monitor baselines are necessary. If they solve a toy setting, report that positive control honestly rather than selecting only a failing model.

## Sprint implementation to add

Build a small execution environment with distinct worker contexts and executor-owned recording. Use only fabricated local records. A worker's natural-language “done” report must not update the authoritative record. The executor should assign event IDs and record actual completed actions separately from proposals and attempted actions. Keep agent-editable logs and the independent execution ledger separate.

Use two tasks if the first is complete early: aggregate resource allocation for calibration, and research-evaluation integrity as the substantive workflow. In the latter, workers prepare a dataset, configure training, and report held-out performance. The policy forbids original evaluation examples from entering training, regardless of renamed partitions. The executor independently records which example IDs are actually consumed, so the label is based on execution rather than another model's opinion. A three-worker workflow can make individually plausible changes whose joint effect violates the rule. Honest workflows and allowed refactors must be included.

Prompted adversarial workers may propose changes only through a restricted, typed local API. Do not execute arbitrary model-written shell code. Do not describe this as natural emergence or general OS isolation. Run new worker trajectories and substantive experiments during the actual sprint, and keep their code changes and dates separate from preparation.

## Conditions and fair comparisons

Use the same executed workflow across each evidence condition: full authoritative trace, random benign log loss, targeted removal of a decisive event, and altered agent-side content. Include incomplete traces where safety remains provable, incomplete traces with an already-proven violation, and observationally indistinguishable clean/violating pairs.

Compare per-worker review, full visible-history review, visible history plus a trusted verifier envelope, and selective retrieval from independently retained execution evidence. Also include the exact rule-based policy check and an always-abstain monitor. Recovery receives additional information; charge for that access and compare it with ordinary full-trace review, not only with a weaker monitor.

A hash does not make a source trusted, and a valid hash does not show that an action occurred. A trusted checkpoint must bind the run, policy, recorded time span and finality. Spoofed or stale envelopes are useful negative controls, provided the monitor has enough information to distinguish them.

## Freeze before main collection

Use disjoint development and held-out case families. After the pilot, freeze prompts, case counts, model aliases, maximum tokens, missingness strategies, thresholds, parser rules, error handling and cost allowance. Do not tune on held-out results. Prespecify what result would reject the main hypothesis.

Primary outcome: false-safe decisions on actually violating executions. Secondary outcomes: unsupported certifications, false accusations on clean runs, appropriate abstentions, clean completion, recovery accesses, latency, invalid outputs and token cost. Report errors in the denominator. Bootstrap differences by base workflow, not by copied views. A small set of purposive examples is not a population estimate.

## Novelty and scope

Prior work already demonstrates distributed attacks, mutable traces, partial-observation failures and the need for independent interception. Our potential contribution is the paired measurement of decision sufficiency and the safety–utility trade-off of evidence recovery in actual multi-worker workflows, with a clear evaluation unit and machine-checked labels. This remains a hypothesis about contribution, not a declaration of novelty.

A temporal/quiescence extension was screened out as a primary novelty claim: [Zhu and Wang, arXiv:2609.21284](https://arxiv.org/abs/2609.21284) already directly addresses asynchronous delegated actions and indeterminate evidence. Its primary paper must be reviewed before using any of that framing.

## Stop conditions

If the main environment only tests arithmetic, prioritize an honest benchmark/tool submission and narrow the claims. If the independent ledger cannot validate the intended safety property, stop that experiment and fix the label. If strong monitors solve all held-out cases, report the negative result for the proposed failure mode. Do not manufacture difficulty by quietly weakening the strongest baseline.
