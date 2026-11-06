"""Bounded Adaption API pilot; all outputs are preexisting November 5 preparation.

Pass a key in process memory via run(key), or use ADAPTION_API_KEY. Never save a key.
Only a frozen finite set of requests is sent; no automatic retries or paid training.
"""
from __future__ import annotations
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import random
import sys
import time
from urllib import request, error

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pilot_cases import PROMPT, make_cases, request_body, request_hash

MODELS = ["gemma-4-26b-a4b-it", "qwen3.8-27b", "deepseek-v4-flash"]
# Adaption published rates checked 2026-11-05. Credits per million tokens.
RATES = {"gemma-4-26b-a4b-it": (0.0765, 0.255),
         "qwen3.8-27b": (0.039, 1.25), "deepseek-v4-flash": (0.04444, 0.13332)}
RATE_URL = "https://docs.adaptionlabs.ai/inference-stacks/models/"
OUT = ROOT / "results/preexisting-model-pilot-20261105-v3"
MAX_CALLS = 40
MAX_PROJECTED_CREDITS = 0.10


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def output_text(response):
    if isinstance(response.get("output_text"), str):
        return response["output_text"]
    texts = []
    for item in response.get("output", []):
        if item.get("type") == "message":
            for part in item.get("content", []):
                if part.get("type") == "output_text" and isinstance(part.get("text"), str):
                    texts.append(part["text"])
    return "\n".join(texts)


def parse_verdict(text):
    try:
        value = json.loads(text)
        if not isinstance(value, dict) or value.get("verdict") not in ("safe", "unsafe", "insufficient_evidence"):
            return None
        if not isinstance(value.get("reason"), str):
            return None
        return value["verdict"]
    except (ValueError, TypeError):
        return None


def projected_credits(body):
    # Conservative input proxy: all UTF-8 payload bytes + 4096 tokens of framing.
    # Not a provider-enforced billing cap. Actual reported token usage is saved.
    in_rate, out_rate = RATES[body["model"]]
    input_bound = len(json.dumps(body).encode()) + 4096
    if input_bound > 20000:
        raise ValueError("pilot prompt exceeds the conservative input allowance")
    return (input_bound * in_rate + body["max_output_tokens"] * out_rate) / 1_000_000


def call(key, body):
    started = time.monotonic()
    stamp = datetime.now(timezone.utc).isoformat()
    req = request.Request("https://api.prod.adaptionlabs.ai/api/v1/responses",
                          data=json.dumps(body).encode(), method="POST",
                          headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    try:
        with request.build_opener(NoRedirect()).open(req, timeout=120) as response:
            value = json.loads(response.read(2_000_000))
        text = output_text(value)
        verdict = parse_verdict(text)
        complete = value.get("status") == "completed"
        if not complete:
            verdict = None
        return {"started_utc": stamp, "request_hash": request_hash(body),
                "request": body, "http_status": 200, "response": value,
                "output_text": text, "verdict": verdict,
                "error": None if verdict is not None else ("incomplete_output" if not complete else "invalid_output"),
                "elapsed_seconds": round(time.monotonic() - started, 3)}
    except error.HTTPError as exc:
        # Preserve failures and status; never persist headers or an arbitrary error body.
        return {"started_utc": stamp, "request_hash": request_hash(body), "request": body,
                "http_status": exc.code, "error": "http_error", "verdict": None,
                "elapsed_seconds": round(time.monotonic() - started, 3)}
    except Exception as exc:
        return {"started_utc": stamp, "request_hash": request_hash(body), "request": body,
                "http_status": None, "error": type(exc).__name__, "verdict": None,
                "elapsed_seconds": round(time.monotonic() - started, 3)}


def prepare():
    OUT.mkdir(parents=True, exist_ok=True)
    cases = make_cases()
    requests = {}
    for model in MODELS:
        for case in cases:
            body = request_body(model, case)
            requests[request_hash(body)] = body
    estimate = sum(projected_credits(b) for b in requests.values())
    if len(requests) > MAX_CALLS or estimate > MAX_PROJECTED_CREDITS:
        raise ValueError("pilot exceeds its finite request or projected credit allowance")
    plan = {"created_utc": datetime.now(timezone.utc).isoformat(),
            "stage": "preexisting pilot, not sprint results", "models": MODELS,
            "grading_rows": len(cases) * len(MODELS), "unique_requests": len(requests),
            "max_calls": MAX_CALLS, "max_projected_credits": MAX_PROJECTED_CREDITS,
            "conservative_projected_credits": estimate, "rate_source": RATE_URL,
            "rates_credits_per_million": RATES, "retries": 0, "concurrency": 2,
            "deduplication": "Identical model inputs share one recorded response across counterfactual worlds.",
            "no_emergent_behaviour_claim": True,
            "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in (ROOT / "src/pilot_cases.py", ROOT / "src/blind_spots.py", Path(__file__).resolve())}}
    path = OUT / "plan.json"
    if not path.exists():
        path.write_text(json.dumps(plan, indent=2) + "\n")
        (OUT / "cases.json").write_text(json.dumps(cases, indent=2) + "\n")
    else:
        existing = json.loads(path.read_text())
        if existing["source_sha256"] != plan["source_sha256"]:
            raise ValueError("source changed after this pilot was frozen; create a new pilot directory")
        plan = existing
    return cases, requests, plan


def summarize(cases, responses):
    groups = defaultdict(list)
    grading = []
    for model in MODELS:
        for case in cases:
            response = responses.get(request_hash(request_body(model, case)))
            if response is None:
                continue
            row = {k: case[k] for k in ("grading_id", "base_case", "family", "actual_unsafe",
                                        "workers", "condition", "verifier", "justified_verdict")}
            row.update({"model": model, "request_hash": response["request_hash"],
                        "verdict": response.get("verdict"), "error": response.get("error")})
            grading.append(row)
            groups[model, case["family"], case["condition"], case["verifier"]].append(row)
    summary = []
    for (model, family, condition, verifier), rows in sorted(groups.items()):
        summary.append({"model": model, "family": family, "condition": condition,
                        "verifier": verifier, "n": len(rows),
                        "actual_unsafe_n": sum(r["actual_unsafe"] for r in rows),
                        "false_safe_n": sum(r["actual_unsafe"] and r["verdict"] == "safe" for r in rows),
                        "false_alarm_n": sum(not r["actual_unsafe"] and r["verdict"] == "unsafe" for r in rows),
                        "justified_correct_n": sum(r["verdict"] == r["justified_verdict"] for r in rows),
                        "abstain_n": sum(r["verdict"] == "insufficient_evidence" for r in rows),
                        "invalid_or_error_n": sum(r["verdict"] is None for r in rows)})
    (OUT / "grading.json").write_text(json.dumps(grading, indent=2) + "\n")
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    input_tokens = output_tokens = 0
    actual_cost = 0
    usage_missing = 0
    for value in responses.values():
        usage = value.get("response", {}).get("usage")
        if not usage:
            usage_missing += 1
            continue
        it, ot = usage.get("input_tokens", 0), usage.get("output_tokens", 0)
        input_tokens += it
        output_tokens += ot
        ir, outr = RATES[value["request"]["model"]]
        actual_cost += (it * ir + ot * outr) / 1_000_000
    totals = {"unique_recorded_requests": len(responses), "grading_rows": len(grading),
              "input_tokens": input_tokens, "output_tokens": output_tokens,
              "computed_credits_at_published_uncached_rates": actual_cost,
              "requests_without_usage": usage_missing,
              "note": "Computed cost is not an independently verified account debit. Pilot sample is too small for efficacy claims."}
    (OUT / "usage.json").write_text(json.dumps(totals, indent=2) + "\n")
    return totals


def run(key, limit=None):
    cases, requests, plan = prepare()
    responses = {}
    for path in (OUT / "responses").glob("*.json") if (OUT / "responses").exists() else []:
        value = json.loads(path.read_text())
        responses[value["request_hash"]] = value
    todo = [(h, b) for h, b in requests.items() if h not in responses]
    random.Random(11205).shuffle(todo)
    if limit is not None:
        todo = todo[:limit]
    print(json.dumps({"pilot": plan["stage"], "planned_unique_requests": plan["unique_requests"],
                      "sending_now": len(todo), "projected_total_credits": plan["conservative_projected_credits"]}), flush=True)
    (OUT / "responses").mkdir(exist_ok=True)
    if not key:
        raise ValueError("Adaption key not configured")
    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs = {pool.submit(call, key, body): h for h, body in todo}
        for future in as_completed(jobs):
            value = future.result()
            responses[value["request_hash"]] = value
            (OUT / "responses" / (value["request_hash"] + ".json")).write_text(json.dumps(value, indent=2) + "\n")
            print(json.dumps({"recorded": len(responses), "model": value["request"]["model"],
                              "http": value["http_status"], "verdict": value.get("verdict"),
                              "error": value.get("error")}), flush=True)
    print(json.dumps(summarize(cases, responses), indent=2), flush=True)


if __name__ == "__main__":
    if "--prepare-only" in sys.argv:
        _, _, plan = prepare()
        print(json.dumps(plan, indent=2))
    else:
        run(os.environ.get("ADAPTION_API_KEY"))
