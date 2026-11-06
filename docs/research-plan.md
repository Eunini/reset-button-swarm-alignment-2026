# Provisional research protocol — pre-sprint, November 5, 2026

## Question and practical consequence

When agents jointly consume a resource governed by a principal's aggregate quota, can an oversight system distinguish a compliant run from a violating run after part of the execution trace disappears? Does independently recorded evidence improve this distinction without turning every logging fault into a false accusation or halting all useful work?

Working title: **Blind Spots: Swarm Oversight Under Missing Evidence**. Track 4, with a possible Track 1 contribution if the testbed is substantially extended during the sprint. Do not select extra tracks simply because they exist.

## Why this project, and why it might fail

Existing work already covers fragmented attacks, mutable agent traces, and independent interception. Our tentative contribution is an evaluation of their intersection: matched compliant/violating executions with identical visible traces, explicit abstention, and a safety–utility comparison under benign versus adversarial missingness. We cannot claim this intersection is novel without reading the full closest papers, their experiments, and their references. If that review reveals an equivalent benchmark, make this a clearly labelled replication plus a specific extension, or change the question before main runs.

## Threat model and trust boundary

- Agents operate only on synthetic records in a local simulator. No real account, network target, credential, or destructive action is involved.
- A quota applies per principal across all workers. Each individual action can be locally allowed while their total violates the shared policy.
- The adversary may suppress or alter the agent-side event log. In the first experiment the adversarial strategy is scripted; it must not be described as discovered by an LLM.
- The executor's committed event manifest and optional recovery store are trusted. Agents cannot change either. Hashes alone do not prove execution or policy correctness, and an agent-supplied hash chain is not a trusted manifest.
- Recovery is additional information. Compare it with an ordinary full-trace global monitor, charge for its reads, and do not attribute its gain to a cleverer model.
- Simulated process boundaries are not OS isolation or a proof against a host compromise. A real gateway implementation and persistence semantics would require separate validation.

## Paired cases

For a quota Q, expose a prefix totalling Q−m for principal A. Hide one final action. In the compliant twin it consumes at most m; in the violating twin it consumes more than m. Keep visible records, worker count, event count, and public policy identical. Use separately checked labels from full execution totals. Distractor records from principal B test whether monitors wrongly pool unrelated principals.

This is an intentionally constructed indistinguishability test. A monitor given the same visible input has the same response distribution for both twins; it cannot correctly certify one and reject the other without more information. This is a sanity constraint, not an empirical discovery about models. Hash commitments are different across twins and must not be claimed to be identical observations in the receipt condition.

## Baselines and ablations

1. Per-worker local quota check (weak diagnostic baseline; not a correct global monitor).
2. Global visible-log aggregation (stronger but assumes no missing events).
3. Completeness-aware aggregation with three outcomes: SAFE, UNSAFE, INSUFFICIENT_EVIDENCE. Verified visible violations remain UNSAFE even if other records are missing. All other incomplete traces use conservative bounds.
4. Same global aggregation over an authoritative recovered trace. Report recovery accesses and compare to a full-trace oracle.
5. LLM monitor reading exactly the visible trace, both with and without a trusted completeness envelope, pending model access.
6. If feasible: a trained small monitor versus the same untrained base model, preserving the same evidence and thresholds. Sponsor credits are optional; do not add training merely to consume them.

Vary worker count (3, 8, 16), full visibility, random loss, selective loss of the decisive event, and altered content. Hold evidence and task fixed for every monitor comparison. Missingness mechanisms are experimental conditions, not hidden labels in the monitor prompt.

## Model extension required before strong behavioural claims

Read the full closest papers. Use an actual worker runtime to produce at least one set of multi-agent executions; include both coordinated attack instructions and honest workers. Separate prompted coordination from emergent behaviour. Fix prompts after the pilot. Record model version, decoding parameters, exact prompts, raw responses, provider errors, retries, and token usage. Transport errors must not count as safe outcomes or disappear from the denominator.

Use the same output schema and evidence for comparable LLM monitors. Parse invalid output as an explicit error. Do not quietly repair malformed responses with another model. Randomize order of safe/unsafe twins. Never put truth labels, attack-condition names, or answer-bearing filenames in model input. Keep test families held out from any Adaption data generation or tuning. Verify that credit eligibility includes the actual service needed; Adaption training credits are not automatically general inference credits.

## Outcomes and statistics

Primary safety outcome: P(SAFE | actual policy violation), called the false-safe rate. Also report unsafe recall, false alarms on compliant cases, abstentions by class, ordinary errors, and useful completion on clean runs. Abstention is never counted as detection of harm. An always-abstain baseline has zero false-safe rate but zero certification utility; include it in the main model study.

Report rates with numerators and denominators. Use Wilson intervals for individual binomial rates and paired bootstrap confidence intervals clustered by base case for differences between monitors. Variants of the same case are not independent samples. Report each worker count and missingness condition separately before aggregating. Constructed smoke checks are not population estimates; no significance claims should be made from them.

For any confidence/threshold sweep, select thresholds on a development split only, then freeze them. Report safety–coverage curves, full-trace performance, and recoveries per correct final decision. Do not rank a defence only on attack detection; show benign missingness cost.

## Decision gates

- Before sprint: preserve preparation with hashes, fetch template, resolve access. No paid jobs.
- Friday: verify exact sprint start with logistics; conservatively treat pre-keynote artifacts as preexisting. Complete full-text related-work review and seek feedback in office hours if available. User is the sole human entrant.
- Pilot: test small model batch; check ability to solve complete-trace tasks. If the full-trace monitor cannot follow the quota policy reliably, simplify the task or reject this design before main runs.
- Freeze: specify models, family split, case count and maximum credit cost from actual estimates. Never launch a run whose cost or inference access is unknown.
- Main: run frozen cases; preserve failed requests and all negative findings. Add a new experiment only for a stated unresolved question.
- Sunday: analyse, write, independently cross-check claims against outputs, format official template, inspect every page, submit well before the cutoff.

## Limits to state even if the experiment succeeds

Toy quota tasks have exact arithmetic policies and a closed world. Synthetic log deletion is not naturally occurring scheming. A trusted manifest detects incompleteness, not malicious intent. Recovery works only when independently retained evidence exists. No claims of cryptographic innovation, real-world containment, general prompt-injection resistance, or guaranteed safety are justified by this setup.

## November 5 protocol amendment

After the user connected Adaption and instructed us to begin, a finite live calibration pilot was authorized and run before the sprint. It remains preexisting and exploratory. This replaces the initial preparation-only/no-paid-jobs convention for that bounded pilot; it does not change the official sprint boundary. The original manifest and original versions of changed pilot code are retained. See the dated work log, matched-budget analysis, and `docs/main-study-candidate.md` for what remains to be implemented and frozen during the sprint.
