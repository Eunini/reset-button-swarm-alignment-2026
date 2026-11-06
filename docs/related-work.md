# Related-work triage — checked November 5, 2026

These primary source abstracts were checked. **Full-text comparison is still required** before freezing a novelty claim. Summaries below are our paraphrases, not reproduced abstracts. Search results alone are not a bibliography.

| Work | Verified identity and relevance | Consequence for this project |
| --- | --- | --- |
| Makins, Angelini, Shams & Phuong (2026), *Multi-Agent AI Control: Distributed Attacks Hamper Per-Instance Monitors*, arXiv:2607.07368v2 | [Primary source](https://arxiv.org/abs/2607.07368v2). Studies coordinated attacks and the limitations of judging workers separately in FakeLab. | Fragmentation and the weakness of per-agent monitoring are prior results. Full global oversight is a required baseline. |
| Qin, Schmotz, Prinzhorn, Beurer-Kellner, Prabhu & Andriushchenko (2026), *LLM Agents Can Easily Tamper With Their Own Traces*, arXiv:2609.30266v1 | [Primary source](https://arxiv.org/abs/2609.30266v1). Examines editable local execution records and recommends recording beyond agent control. | Neither trace tampering nor external logging is our discovery. Test the decision consequences of missingness and limits of recovery. |
| Arslan (2026), *Audit Without Verification: When LLM Accountability Layers Relay Rather Than Check*, arXiv:2609.07680v1 | [Primary source](https://arxiv.org/abs/2609.07680v1). Compares filed agent reports with independently informative evidence in fault attribution. | Do not treat agent self-reports as authoritative execution evidence. Distinguish our safety certification task from fault attribution. |
| Greenblatt, Shlegeris, Sachan & Roger (2024), *AI Control: Improving Safety Despite Intentional Subversion*, arXiv:2312.06942v5 | [Primary source](https://arxiv.org/abs/2312.06942v5). Evaluates safety protocols against deliberately subversive models. | Report usefulness alongside safety and spell out adversarial access and trusted components. |

Other directions screened out at triage: generic consensus/source-provenance defences face close work in epistemic Sybil resistance and evidence laundering. A generic “agents agree but are wrong” demo is too weak a novelty claim. Do not add these screened works as citations without opening the actual primary source and checking its metadata.

Official starting point: [Resources and Guidelines](https://apartresearch.com/sprints/swarm-alignment-2026). The original DOCX, PDF and text template exports are in `sources/`. The page could be read through the web tool; a separate direct HTTP fetch returned 403. We have not fabricated a local copy of that page.
