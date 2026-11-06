"""Saved-data analysis of the during-sprint extension; no API calls."""
from collections import defaultdict
from datetime import datetime,timezone
import json
from pathlib import Path
import statistics

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/sprint-report-load-20261106'


def analyze():
    summary=json.loads((OUT/'summary.json').read_text())
    rows=json.loads((OUT/'oracle-results.json').read_text())
    episodes=json.loads((OUT/'interactive-episodes.json').read_text())
    groups=defaultdict(list)
    for r in rows:
        key=tuple(r[k] for k in ('honest_load','initial_mistake','attackers','ordering','policy','budget','identity'))
        groups[key].append(r)
    aggregate=[]
    fields=('honest_load','initial_mistake','attackers','ordering','policy','budget','identity')
    for key,items in groups.items():
        aggregate.append(dict(zip(fields,key))|{'seeds':len(items),**{k:statistics.mean(r[k] for r in items)
                         for k in ('detected','detection_fraction','calls','false_stops','false_report_checks','capacity_normalized')}})
    primary=[r for r in aggregate if r['honest_load']==8 and r['attackers']==1 and r['ordering']=='mixed'
             and r['budget']==16 and r['identity']=='reset' and r['policy'] in ('identity_rep','root_rep','quota:4','quota:8')]
    interactive=[]
    for model in ('qwen3.8-27b','deepseek-v4-flash'):
        for policy in ('identity_rep','root_rep','quota:4'):
            items=[e for e in episodes if e['model']==model and e['policy']==policy]
            interactive.append({'model':model,'policy':policy,'n':len(items),**{k:statistics.mean(e[k] for e in items)
                               for k in ('true_detected','false_report_checks','restarts','invalid_actions')}})
    checks={'all_replays_within_budget':all(r['calls']<=r['budget'] for r in rows),
            'no_false_stops_with_exact_checker':all(r['false_stops']==0 for r in rows),
            'normalization_bounded':all(0<=r['capacity_normalized']<=1 for r in rows),
            'expected_seed_count':len({r['seed'] for r in rows})==32,
            'expected_replay_count':len(rows)==28672,
            'primary_32_seeds':all(r['seeds']==32 for r in primary)}
    result={'created_utc':datetime.now(timezone.utc).isoformat(),'stage':'during-sprint extension','primary':primary,
            'interactive':interactive,'aggregate':aggregate,'checks':checks,'passed':all(checks.values()),
            'interpretation_limits':['Exact-checker replays measure a constructed mechanism, not LLM worker behaviour.',
                                     'Only the supplemental reporter makes turn-by-turn LLM decisions; it is assigned an adversarial objective.',
                                     'Verifier control prompts share 16 paired seeds; 128 calls are not 128 independent scenarios.',
                                     'Interactive comparisons have two seeds per model/policy and support no model ranking.',
                                     'No new algorithm or autonomous-discovery claim.']}
    followup=ROOT/'results/sprint-interactive-v3-20261106'
    if not (followup/'summary.json').exists():followup=ROOT/'results/sprint-interactive-v2-20261106'
    if (followup/'summary.json').exists():
        result['interactive_followup']={'summary':json.loads((followup/'summary.json').read_text()),'artifact_directory':str(followup.relative_to(ROOT)),'groups':[]}
        eps=json.loads((followup/'interactive-episodes.json').read_text())
        for model in ('qwen3.8-27b','deepseek-v4-flash'):
            for policy in ('identity_rep','root_rep','quota:4'):
                items=[e for e in eps if e['model']==model and e['policy']==policy]
                result['interactive_followup']['groups'].append({'model':model,'policy':policy,'n':len(items),
                    'valid_actions':sum(8-e['invalid_actions'] for e in items),
                    **{k:statistics.mean(e[k] for e in items) for k in ('true_detected','false_report_checks','restarts','invalid_actions')}})
    (OUT/'analysis.json').write_text(json.dumps(result,indent=2)+'\n')
    figs=OUT/'figures';figs.mkdir(exist_ok=True)
    labels={'checked':'Check all','identity_rep':'Process reputation','root_rep':'Root reputation','quota:1':'Root quota 1','quota:2':'Root quota 2','quota:4':'Root quota 4','quota:8':'Root quota 8'}
    fig,axes=plt.subplots(1,2,figsize=(8,2.8),sharey=True)
    for ax,mistake in zip(axes,(0,1)):
        for policy,color,ls in [('root_rep','#28786b','-'),('quota:4','#bd6731','--'),('quota:8','#4d72a5',':'),('identity_rep','#8a6a9f','-.')]:
            items=sorted([r for r in aggregate if r['initial_mistake']==mistake and r['attackers']==1 and r['ordering']=='mixed'
                          and r['budget']==16 and r['identity']=='reset' and r['policy']==policy],key=lambda r:r['honest_load'])
            ax.plot([r['honest_load'] for r in items],[r['detection_fraction'] for r in items],label=labels[policy],color=color,linestyle=ls,marker='o',markersize=4)
        ax.set_title('One initial honest mistake' if mistake else 'No initial honest mistake',fontsize=10)
        ax.set_xlabel('Genuine warnings from one trusted root',fontsize=9);ax.set_xticks([1,4,8,12]);ax.set_ylim(-.04,1.04)
        ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.15)
    axes[0].set_ylabel('Genuine incident detection fraction',fontsize=9)
    h,l=axes[0].get_legend_handles_labels();fig.legend(h,l,loc='lower center',bbox_to_anchor=(.5,-.04),ncol=4,frameon=False,fontsize=8)
    fig.suptitle('Exact-checker replay: B=16, one attacker root, mixed arrivals, alias resets',fontsize=9,y=1.02)
    fig.tight_layout(rect=(0,.08,1,1));fig.savefig(figs/'honest-load.png',dpi=180,bbox_inches='tight');fig.savefig(figs/'honest-load.svg',bbox_inches='tight');plt.close(fig)
    print(json.dumps({'analysis_passed':result['passed'],'primary':primary,'validation':summary['verifier_controls'],'interactive':interactive},indent=2))
    if not result['passed']:raise SystemExit(1)
    return result


if __name__=='__main__':analyze()
