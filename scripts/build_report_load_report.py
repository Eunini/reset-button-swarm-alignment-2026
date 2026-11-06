"""Report for the new during-sprint extension, using actual saved outputs."""
from datetime import datetime,timezone
import json
from pathlib import Path
import sys
from docx import Document
from docx.shared import Pt,Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/sprint-report-load-20261106'
sys.path.insert(0,str(ROOT/'src'))
from reset_button import VERIFIER_INSTRUCTIONS


def build():
    a=json.loads((OUT/'analysis.json').read_text());s=json.loads((OUT/'summary.json').read_text())
    receipts=[json.loads(p.read_text()) for p in (OUT/'responses').glob('*.json')]
    incomplete=sum(r.get('error')=='incomplete_output' for r in receipts)
    followup=a.get('interactive_followup')
    def pval(policy,mistake):return next(r for r in a['primary'] if r['policy']==policy and r['initial_mistake']==mistake)['detected']
    doc=Document(ROOT/'sources/official-template.docx');front=doc.tables[0]
    for child in list(doc._element.body):
        if child is not front._element and child.tag!=qn('w:sectPr'):doc._element.body.remove(child)
    for cell in (front.cell(0,0),front.cell(1,0)):cell._tc.clear_content();cell.add_paragraph()
    st=doc.styles['normal'];st.font.name='Times New Roman';st.font.size=Pt(10.5);st.paragraph_format.line_spacing=1.04;st.paragraph_format.space_after=Pt(6)
    for name in ('Heading 2','Heading 3'):
        doc.styles[name].font.name='Times New Roman';doc.styles[name].font.size=Pt(12 if name=='Heading 2' else 10.5)
        doc.styles[name].font.bold=True;doc.styles[name].paragraph_format.space_before=Pt(8);doc.styles[name].paragraph_format.space_after=Pt(5)
    pending=[False]
    def para(text='',size=None):
        p=doc.add_paragraph(style='normal');r=p.add_run(text)
        if size:r.font.size=Pt(size)
        return p
    def heading(text,level=2):
        p=doc.add_paragraph(text,style=f'Heading {level}')
        if pending[0]:p.paragraph_format.page_break_before=True;pending[0]=False
    def page():pending[0]=True
    def table(head,rows):
        t=doc.add_table(rows=1,cols=len(head))
        if 'Table Grid' not in doc.styles:doc.styles.add_style('Table Grid',WD_STYLE_TYPE.TABLE)
        t.style='Table Grid'
        for c,x in zip(t.rows[0].cells,head):c.text=str(x)
        for row in rows:
            for c,x in zip(t.add_row().cells,row):c.text=str(x)
        for i,row in enumerate(t.rows):
            for c in row.cells:
                for p in c.paragraphs:
                    p.paragraph_format.space_after=Pt(3)
                    for r in p.runs:r.font.size=Pt(9);r.bold=i==0
        borders=OxmlElement('w:tblBorders')
        for edge in ('top','left','bottom','right','insideH','insideV'):
            e=OxmlElement('w:'+edge);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'B7B7B7');borders.append(e)
        t._tbl.tblPr.append(borders)
    header=doc.sections[0].header.paragraphs[0];header.text='SWARM ALIGNMENT HACKATHON • NOVEMBER 2026';header.alignment=WD_ALIGN_PARAGRAPH.CENTER
    for r in header.runs:r.font.size=Pt(8)
    foot=doc.sections[0].footer.paragraphs[0];foot.text='Reset Button | ';foot.alignment=WD_ALIGN_PARAGRAPH.CENTER
    field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');foot._p.append(field)
    c=front.cell(0,0);p=c.paragraphs[0];p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    r=p.add_run('Reset Button: Reporting Limits,\nHonest Bursts and Inherited Distrust');r.bold=True;r.font.size=Pt(18)
    p=c.add_paragraph('Inioluwa Atanda\nIndependent researcher • solo entry');p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    correct=sum(v['correct'] for v in s['verifier_controls']);vn=sum(v['n'] for v in s['verifier_controls'])
    abstract=(f'Peer-reporting controls must resist false complaints while allowing useful warnings. We extend a preexisting '
              f'identity-reset testbed during the sprint to measure how legitimate report volume and an initial honest mistake '
              f'change that trade-off. We generate 1,024 workload streams from 32 task seeds across four honest-report loads, '
              f'two mistake conditions, two attacker-principal counts and two arrival patterns. Paired exact-checker replays '
              f'compare process reputation, trusted-root reputation, checking every report and four fixed root quotas at equal '
              f'budgets. In the primary eight-warning, sixteen-check condition, root reputation detects {pval("root_rep",0):.0f}/8 '
              f'incidents without an initial honest mistake but {pval("root_rep",1):.0f}/8 after one; quota four detects '
              f'{pval("quota:4",0):.0f}/8 and {pval("quota:4",1):.0f}/8 respectively. These values describe constructed policies, '
              f'not autonomous swarm behaviour. Supplemental controls obtain {correct}/{vn} correct judgments across two '
              f'hosted models on paired, neutrally named evidence, and twelve small episodes let a prompted AI reporter '
              f'choose complaints and identity resets turn by turn. However, {incomplete}/96 interactive outputs are truncated; '
              f'that protocol failed calibration and supports no method or model ranking. Higher-budget follow-ups also stopped on timeout or truncation. The contribution is a reproducible workload-sensitive oversight evaluation. Quotas, reputation and persistent '
              f'identity are existing mechanisms; no new-defence or spontaneous-attack discovery is claimed. The objective '
              f'sandbox policy remains directly enforceable by code.')
    if followup:
        valid=96-followup['summary']['invalid_actions']
        abstract=abstract.replace('The contribution is a reproducible',f'An explicit 16,384-token follow-up yields {valid}/96 valid actions on the same cases and is reported as calibration. The contribution is a reproducible')
    words=len(abstract.split());assert 150<=words<=250,words
    c=front.cell(1,0);c.paragraphs[0].add_run('Abstract').bold=True;c.add_paragraph(abstract)
    heading('1. Introduction')
    para('A false-report filter can save checking capacity by discounting unreliable reporters. Agent copying creates an identity problem, but preventing aliases from erasing history is only part of the design task. A reporting policy must also accommodate an honest parent and its children sending many correct warnings, including after a mistaken complaint.')
    para('Our earlier preparation showed an identity-reset bypass, but a simple trusted-root quota matched the proposed history-based repair on that workload. The new question is whether this comparison survives genuine report bursts and inherited distrust. We retain the simple quota as a strong baseline and evaluate its limits rather than claiming a superior new defence.')
    heading('2. Related Work')
    para('Ye and Steinhardt [1] study false reporting and escalating reputation in LLM-agent simulations. We reuse the disclosed mathematical rule and an adaptation of its public code; our sequential workflow is not an exact reproduction. Gatta et al. [2] already study replaceable identity and reputation in agent markets. Neither identity persistence nor quotas are our inventions. This extension adds a controlled legitimate-load comparison, paired anti-shortcut verifier controls and small interactive reporter episodes. No exhaustive novelty claim is made.')
    page();heading('3. Methods')
    heading('3.1 Workload streams and independent labels',3)
    para('We reuse the preexisting closed Lab executor and report-policy code. Each stream has eight compliant targets and H distinct incident targets, where H is 1, 4, 8 or 12. Compliant workers fit training samples and evaluate heldout samples; incident workers fit at least one heldout sample. A separate function labels the actual executed sample use. All worker IDs now use the same opaque format, so their names do not reveal labels.')
    para('One honest trusted root issues the H genuine warnings through a child identity. In the mistake condition its parent first files one incorrect complaint. An adversary has exactly 24 false-report opportunities, divided across either one or three independent trusted roots. Principal count changes do not increase the total attack allowance. Reports are randomly mixed or attack-first; a seeded stream is identical across policy, budget and alias replays. Stable identity retains each process ID, including the planned parent-to-child delegation. Reset assigns a fresh alias per report while preserving trusted roots.')
    heading('3.2 Policies and budgets',3)
    table(['Policy','Behaviour'],[['Checked','Verify each report while calls remain.'],['Process reputation','The disclosed escalating rule, keyed by process ID.'],['Root reputation','The same rule, keyed by executor-attested delegation root.'],['Root quota 1, 2, 4 or 8','Verify at most q reports per trusted root, also respecting the global budget.']])
    para('For v verified valid and f invalid reports, reputation is (2+v)/[3+v+3f(f+1)/2]. Scores accumulate by target and trigger checking at 0.666. A positive verification stops the target; uncertainty consumes a check without changing reputation. The sweep uses exact executor judgments and budgets 8 and 16. It contains 28,672 paired policy replays of 1,024 streams, not 28,672 independent experiments. Primary comparisons use H=8, budget 16, one attacker root and mixed arrivals. Task seed is the unit of variation; no significance claim is made from deterministic zero-variance cells.')
    heading('3.3 Model controls and interactive episodes',3)
    para('Sixteen fresh verifier-control seeds generate paired compliant/violating worlds with the same neutral worker ID and the same report reason. Neutral and violation-asserting reasons are crossed with both worlds. Two models judge 64 inputs each without expected labels. Separately, two models × three policies × two fresh seeds produce twelve eight-turn episodes. A prompted adversarial reporter chooses a target, a reason and whether to restart after seeing feedback. Genuine witnesses and the exact checker remain scripted; an invalid action uses its turn. These two-seed comparisons support no model ranking or claim of spontaneous strategy discovery.')
    page();heading('4. Results')
    doc.add_picture(str(OUT/'figures/honest-load.png'),width=Inches(6.35))
    para('Figure 1. Exact-checker detection across honest report load. Each point averages 32 paired seeds at budget 16, one attacker root and mixed arrivals. All-report reset aliases preserve trusted roots. Curves concern constructed policy behaviour, not autonomous swarms. Policy differences may follow directly from thresholds and caps.',size=8.5)
    table(['Policy','No initial mistake','One initial mistake'],[[p,f'{pval(p,0):.2f}/8',f'{pval(p,1):.2f}/8'] for p in ['identity_rep','root_rep','quota:4','quota:8']])
    para('Table 1. Mean genuine incidents detected in the prespecified primary condition. Planned parent-to-child delegation changes a process identity even in the stable-process condition. The table uses reset aliases and disjoint incident targets.',size=8.5)
    para('A fixed root quota bounds malicious verification demand but also caps legitimate warnings from the same root. Root reputation instead allows sustained correct reporting, until the initial incorrect report lowers that root below the single-report threshold. Subsequent distinct, truthful reports then fail to trigger verification and cannot earn the feedback needed to restore reputation. This is a structural counterexample within the stated rule, not an estimated frequency of honest-agent mistakes.')
    for v in s['verifier_controls']:para(f"{v['model']}: {v['correct']}/{v['n']} paired-control judgments match executor labels; {v['errors']} output/transport errors. The inputs share sixteen seeds and are not independent trials.",size=9)
    para(f'The interactive protocol produced {incomplete}/96 incomplete outputs at the 4,096-token allowance. Its policy outcomes are not interpreted: invalid turns change how many false reports are attempted and therefore confound apparent protection. The diagnostic counts below average two seeds (eight turns each), not independent efficacy trials.',size=9)
    table(['Model','Policy','Invalid turns /8','Resets'],[[r['model'],r['policy'],f"{r['invalid_actions']:.1f}",f"{r['restarts']:.1f}"] for r in a['interactive']])
    if followup:
        page();heading('4.1 Interactive Calibration Follow-up')
        fs=followup['summary'];valid=96-fs['invalid_actions']
        transport=' It uses documented server-sent events after a non-streaming attempt hit HTTP 504 at sixty seconds; that failed request is also retained.' if fs.get('stream') else ''
        para(f'The original 59 incomplete actions are retained. A separately frozen amendment raises the interactive maximum output allowance from 4,096 to 16,384 tokens for both models and every policy. It reruns all twelve episodes, not just failed cells.{transport} Prompts, cases, turns, temperature, policies and grading are unchanged. This is calibration on the same cases, not a new held-out efficacy study. The follow-up produced {valid}/96 valid actions; every invalid action still uses its turn.')
        table(['Model','Policy','Valid /16','Real warnings /8','Resets'],[[r['model'],r['policy'],r['valid_actions'],f"{r['true_detected']:.1f}",f"{r['restarts']:.1f}"] for r in followup['groups']])
        para('Table 2. Diagnostic follow-up: valid counts total sixteen actions across two episodes; warning and reset counts average those two episodes. Genuine witnesses and the checker are scripted. These small reused-case results do not justify model rankings or claims of spontaneous strategy discovery. Where invalid-action rates differ, apparent protection is confounded by a difference in attempted attacks.')
        para('The primary workload sweep and the 128 paired verifier-control calls are unchanged by this follow-up. It addresses an execution-budget failure in the optional interactive supplement, not an error in the exact-checker analysis.')
    page();heading('5. Discussion and Limitations')
    para('The preparation-stage quota comparison was incomplete because its honest roots each sent very few warnings. This new workload exposes both the quota trade-off and the recovery limitation of inherited reputation. The appropriate control depends on legitimate volume, principal count, mistakes and arrival order. Our tested quota set is not an exhaustive policy search, and no policy is established as universally best.')
    para('The repair question is therefore broader than preventing identity reset. A copied worker may need persistent accountability and a way to produce independently checked evidence after its parent makes a mistake. An appeal channel, independent audits or adaptive allocation could help, but none is proposed here as a validated solution. Existing quotas remain competitive controls, and their strengths and weaknesses are reported.')
    heading('Scope of evidence',3)
    para('The large sweep uses an exact checker and scripted workers and messages. It measures a constructed allocation mechanism, not LLM behaviour. Verifier controls test a narrow objective policy, and that policy could be directly enforced by code with no LLM judgment calls. The interactive protocol failed calibration because most actions were truncated; it has only two seeds per model/policy and an explicitly prompted adversary. It provides no reliable method comparison and establishes no emergent collusion, frontier-model transfer or real-world attack prevalence.')
    para('Root links, executor logs and sample partitions are trusted. Separate-account creation, forged roots, semantic policy ambiguity, concurrent queues, and unequal costs per check are outside the threat model. First-in-first-served and fixed-volume assumptions limit transfer. Changing the thresholds, feedback rules, the number of reports per target, or capacity can change the result. The alias invariance of root-keyed policies is a design property, not an empirical discovery.')
    heading('6. Conclusion')
    para('A reporting limit that handles a low-volume false-report flood can reject useful bursts from honest agents. Preserving root history can avoid alias resets while creating a different failure: a truthful child may inherit a parent’s lack of credibility and receive no verification. This during-sprint extension makes these workload and recovery costs reproducible without claiming a new defence. New policies should be evaluated on legitimate demand and honest mistakes as well as adversarial report volume.')
    heading('Code and Data')
    para('Code and data: https://github.com/Eunini/reset-button-swarm-alignment-2026. The repository contains source, frozen plans, generated event streams, raw model requests and responses, failures, usage, outcomes and analysis. Key paths are src/report_load.py, scripts/run_report_load.py and results/sprint-report-load-20261106/. Exact seeds and the protocol are also specified in Appendix B.',size=9)
    page();heading('References')
    for t in ['[1] Yaowen Ye and Jacob Steinhardt. 2026. Norm Enforcement for AI Agents: Robustly Shaping Behavior in Multi-Agent Systems. arXiv:2607.09766v1. https://arxiv.org/abs/2607.09766v1',
              '[2] Federico Gatta, Manuel Naviglio and Francesco Tarantelli. 2026. Tempting the Agent: The Economics of Reputation without Persistent Identity in AI Agent Markets. arXiv:2609.02992v2. https://arxiv.org/abs/2609.02992v2',
              '[3] Apart Research. 2026. Swarm Alignment Hackathon: Guidelines, Resources and official report template. https://apartresearch.com/sprints/swarm-alignment-2026',
              '[4] Adaption Labs. 2026. Inference model pricing. https://docs.adaptionlabs.ai/inference-stacks/models/']:para(t)
    heading('Prior Work and Sprint Contributions')
    para('All earlier code, the 4,258-request identity-reset study, its findings and its report are disclosed as preexisting preparation. The website countdown opens at November 6, 12:00 UTC. This extension was implemented and frozen after that opening; its workload sweep, paired verifier controls and interactive episodes are new during-sprint work. Existing sandbox, transport and reputation code are reused and credited. Repeating earlier known results is not claimed as a new discovery.')
    para(f"This execution started {s['started_utc']} and finished {s['finished_utc']}. The plan was frozen before held-out results were read. See sources/sprint-report-load-plan-20261106.json for source hashes, exact seeds, limits and hypotheses. The reused public norm-enforcement code is pinned at commit 0568d47da7dc6ab75cc3fa4041bb228f074d91c1; its MIT license and copyright notice for Yaowen Ye and Jacob Steinhardt are retained. Our sequential adaptation is not an exact reproduction.")
    heading('Compute and Failures')
    u=s['usage'];para(f"New extension: {u['recorded_requests']} recorded API requests, {u['input_tokens']} input tokens and {u['output_tokens']} output tokens. The published-rate estimate is {u['estimated_credits']:.5f} credits; provider-reported usage cost sums to {u['provider_reported_cost']:.5f}. Neither is an independently audited account debit. Invalid/incomplete outputs and all interactive actions are retained. No automatic retries are used. Replay counts do not represent paid calls or independent model trials.")
    if followup:
        fu=followup['summary']['usage'];para(f"The explicit interactive follow-up adds {fu['recorded_requests']} recorded requests and an estimated {fu['estimated_credits']:.5f} credits; provider-reported cost is {fu['provider_reported_cost']:.5f}. These calls are separately recorded rather than silently replacing the original 4,096-token run. See sources/sprint-interactive-followup-plan-20261106.json, sources/sprint-interactive-stream-plan-20261106.json and {followup['artifact_directory']}/.")
    failure_dir=ROOT/'results/sprint-interactive-v2-20261106'
    if (failure_dir/'worker-status.json').exists() and json.loads((failure_dir/'worker-status.json').read_text()).get('state')=='failed':
        para('The non-streaming 16,384-token calibration attempt stopped on its first request with HTTP 504 after sixty seconds. That transport failure is not counted as a completed model action. It remains in results/sprint-interactive-v2-20261106/; no complete usage record was returned, so its billable cost is not independently reconciled.')
    stream_dir=ROOT/'results/sprint-interactive-v3-20261106'
    if (stream_dir/'worker-status.json').exists() and json.loads((stream_dir/'worker-status.json').read_text()).get('state')=='failed':
        stream_records=[json.loads(p.read_text()) for p in (stream_dir/'responses').glob('*.json')]
        complete=sum(r.get('error') is None for r in stream_records)
        para(f'A streaming follow-up used the same 16,384-token allowance and stopped at the first incomplete or invalid action. It recorded {len(stream_records)} requests: {complete} complete outputs and {len(stream_records)-complete} incomplete output. The run stopped before a balanced policy/model comparison was available. Its partial results are retained as calibration evidence, not interpreted as efficacy. No additional retries were undertaken. These supplemental failures do not change the exact-checker sweep or the 128 verifier controls.')
    page();heading('Appendix A. Limitations and Dual-Use / Ethical Considerations')
    para('Every worker, record, complaint and incident is artificial. Model output is parsed as typed data and never executed as shell code. No real person is accused and no external reporting service receives test complaints. The study publishes a bounded sandbox evaluation rather than a production-service attack procedure.')
    para('Knowledge of report flooding could assist disruption of oversight channels. Conversely, aggressive filtering can silence legitimate safety warnings. Persistent lineage can also associate innocent descendants with a parent’s mistake. These concerns motivate reporting both useful-warning throughput and adversarial checking cost. No real-person identity linkage, permanent blacklist or cross-account tracking is proposed.')
    para('The trusted executor and root mapping are explicit assumptions, not demonstrated containment guarantees. The objective policy is better enforced by code where feasible. Results do not establish that these filters are appropriate for human whistleblowers, ambiguous accusations or safety-critical deployments. Additional semantic tasks and recovery-channel evaluations are needed.')
    heading('LLM Usage Statement')
    para('The coding assistant proposed the extension, wrote its implementation, inspected prior research, analyzed saved data and drafted this report. Adaption-hosted models judge synthetic records and control the explicitly prompted adversarial reporter. Programmatic tests check labels, budgets and paired conditions. No independent human review is claimed. Inioluwa Atanda is the solo human entrant and remains responsible for understanding and verifying the report and any submission.')
    heading('Reproduction')
    para('Python source and all saved data are included in the prepared bundle. Run python3 -m unittest discover -s tests -v, then .venv/bin/python scripts/analyze_report_load.py and .venv/bin/python scripts/build_report_load_report.py. Analysis and report generation make no API calls. Live execution is separately bounded by 320 requests and five projected credits, uses a three-second minimum call-start interval, and stops on rate limits/server failures. Credentials are held in process memory only; no API key is packaged.')
    page();heading('Appendix B. Exact Experimental Configuration')
    para('Main workload seeds are 21001–21032. Cross H={1,4,8,12}, initial mistake={0,1}, independent attacker roots={1,3}, and arrival order={mixed,attack_first}. Each root set shares 24 total adversarial report opportunities. Replay all seven listed policies at budgets 8 and 16 under stable/reset aliases. The primary comparison is H8, B16, A1, mixed arrivals, with and without one initial honest mistake. Independent units are task seeds; workload variants and cached decisions are paired.')
    para('Verifier-control seeds are 31001–31016. Each generates compliant/violating worlds with the same neutral actor name, crossed with a neutral allegation and a fixed assertion of a violation. Qwen 3.8 27B and DeepSeek V4 Flash judge every input once. Interactive seeds are 41001 and 41002. Cross both models with process reputation, root reputation and root quota four; run eight turns, H8, B16 and one initial parent mistake. One generated complaint and one scripted genuine warning arrive per turn.')
    heading('Verifier instructions',3);para(VERIFIER_INSTRUCTIONS.strip(),size=9)
    para('The original protocol uses temperature zero, 4,096 maximum output tokens, store=false and no external tools. The explicit interactive calibration follow-up raises only its output allowance to 16,384, uniformly across models and policies; verifier controls remain at 4,096. Provider determinism is not assumed. Exact reporter instructions, current evidence, feedback and decisions are stored in the raw receipts; the reporter is assigned a false-complaint objective and may choose whether to restart. The exact checker, rather than an LLM, determines interactive verification outcomes.',size=9)
    target=ROOT/'report/reset-button-sprint-report.docx';doc.save(target)
    meta={'created_utc':datetime.now(timezone.utc).isoformat(),'report':str(target.relative_to(ROOT)),'abstract_words':words,'stage':'during-sprint extension','human_review_claimed':False,'submitted':False}
    (ROOT/'report/report-load-metadata.json').write_text(json.dumps(meta,indent=2)+'\n');print(target)


if __name__=='__main__':build()
