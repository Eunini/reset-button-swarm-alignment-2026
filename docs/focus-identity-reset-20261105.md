# Recommended focus: Reset Button

Prepared November 5, 2026, before the sprint. This proposal is preexisting preparation, not an experimental result or a guarantee of placement.

Later same-day status: development has now run; see `docs/reset-runbook.md` and the development report. A simple trusted-root quota matches the attack repair and can preserve the honest warning. No new-defence advantage is established. The original proposal below is retained as the record of what was proposed before those results.

## The question in plain language

Can a dishonest AI worker evade penalties for false safety reports by restarting or making copies of itself? Does this consume a limited checking budget and prevent genuine reports from being handled? Can an orchestrator preserve accountability across those copies without suppressing useful reports from honest workers?

Working title: **Reset Button: Testing Swarm Oversight When Agent Identities Can Restart**. Anchor: multi-agent oversight and control, with an infrastructure connection through runtime-assigned identity and delegation history.

This replaces the synthetic missing-evidence prototype as the recommended substantive study. The earlier prototype remains disclosed calibration work. No new model experiments have been run for this proposal.

## Boundary with existing work

- Ye and Steinhardt, *Norm Enforcement for AI Agents: Robustly Shaping Behavior in Multi-Agent Systems*, https://arxiv.org/html/2607.09766v1, already demonstrate false reporting and evaluate Naive, Checked, Backfire, RepVote and EscRepVote mechanisms. Sections 6.2 and Appendix F specify the reputation updates. Section 7 identifies dynamic populations as future work. The inspected text does not establish an empirical test of resetting reporter identities; that is a candidate extension, not proof that no other paper has done it.
- Gatta, Naviglio and Tarantelli, *Tempting the Agent: The Economics of Reputation without Persistent Identity in AI Agent Markets*, https://arxiv.org/abs/2609.02992v2, explicitly studies replaceable identity and reputation in an economic model. Identity reset and the need for persistent accountability are existing ideas.
- The norm-enforcement authors provide code at https://github.com/helloelwin/norm-enforcement. Inspect its implementation, pin a commit and retain its license before adapting it. An adaptation using different models or environments must be described as such, not an exact reproduction.

The potential contribution is a controlled stress test of a particular published oversight mechanism under agent restarts, measuring the safety, cost and useful-work trade-off and evaluating an orchestrator-level repair. Neither false reporting, Sybil attacks, whitewashing, nor binding reputation to persistent identity is our invention. The specific contribution remains unproven until experiments and a final related-work audit support it.

## Smallest credible experiment

Use a local simulated team with executed worker actions, independently checkable policy violations, a reporting channel and an explicit verifier budget. Keep all activity inside the simulation. The attacker may submit reports and request allowed worker restarts; it cannot forge the orchestrator's parent links or tamper with evaluation labels.

Compare these conditions on matched task seeds:

1. Honest population, including ordinary worker restarts and occasional mistaken reports.
2. One adversary filing reports through a persistent identity.
3. The same adversary with identity resets. Total attacker calls, report opportunities and token allowance stay fixed across conditions 2 and 3. More copies must not secretly mean more attack budget.
4. A scripted reset/report strategy alongside an LLM-controlled adversary. Separate a mechanism failure from a claim about an LLM discovering the strategy.

Primary oversight baselines: verification of every report within the same budget, the published escalating-reputation mechanism, and a version that maintains the same reputation and influence budget across an orchestrator-attested delegation root. Naive removal can be a diagnostic but cannot be the main opponent. Count legitimate repeat reporting and honest restarts as controls. Use an unlimited-verification diagnostic to distinguish resource exhaustion from verifier mistakes; disclose its extra resources.

Runtime labels must come from actual policy events. Report truth and target misconduct must be distinct labels: a malicious reporter can make an accurate accusation. Calibrate the verifier on held-out intact cases before attributing failures to the restart intervention. Do not select an incompetent verifier to manufacture a dramatic result.

Measure verifier calls/tokens, false sanctions against compliant workers, real incidents detected before the deadline, reporting delay, and legitimate task completion. Account for invalid outputs and failed requests explicitly. Plot genuine incident detection against verifier budget, with useful work reported alongside it.

## Proposed repair and its limits

The orchestrator assigns an immutable delegation-root identifier. Restarts and children retain the root's reporting history, and splitting into children does not create extra reporting influence. Agents cannot choose these links by writing a name in a message.

This assumes a trusted, closed orchestrator. It does not solve separate-account identity creation or establish that all descendants deserve collective penalties. Honest descendants and genuine reports after a parent's mistaken report are essential controls: a repair that simply ignores everyone is not useful.

## Execution gates for the sprint

- First establish the published mechanism's ordinary behaviour and verify that the counterfactual differs only in identity handling and the declared budget.
- Freeze the evaluation split, main comparison and metrics before the main run. Use development cases for debugging and attack tuning. Start with two model families and multiple independent task seeds; scale only after labels and controls hold up. Reused prompts are not independent experimental units.
- Advance a failure claim only if identity resets materially worsen a prespecified outcome against a capable baseline. Evaluate the repair on fresh cases and include its cost to honest activity.
- If a competent verifier plus a reasonable budget rule already handles resets, report that boundary. If a simple existing baseline matches the proposed repair, do not claim a new defence. No positive result or winning probability is assumed.

Target deliverable: one reproducible local benchmark, one main comparison figure, and a clear 4–8 page report using the official template, with accurate prior-work, AI-use and required appendix disclosures. Main experiments and new implementation belong to the sprint; this design and all earlier preparation must remain marked preexisting.
