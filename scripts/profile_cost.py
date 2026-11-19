import json
import statistics
import httpx
import tiktoken
from app.prompts import SYSTEM_PROMPT

API = "http://localhost:8000/v1/extract"
ENC = tiktoken.get_encoding("o200k_base")

# USD per 1M tokens: (input, cached_input, output).
PRICING = {
    "gpt-5-nano": (0.05, 0.005, 0.40),
    "gpt-5-mini": (0.25, 0.025, 2.00),
    "gpt-5":      (1.25, 0.125, 10.00),
}

# Assumptions
REASONING_OVERHEAD = 1.0   # multiply output tokens
CACHE_HIT_RATE = 0.30      # share of requests answered by the response cache
GPU_WATTS = 200            # average draw while generating
USD_PER_KWH = 0.20         # electricity price
MIN_CACHEABLE = 1024       # OpenAI caches prefixes of 1024+ tokens only

SAMPLES = [
    "Invoice #A-102 from Tanaka Parts, 2026-10-12. 3 x bolts at 120 JPY. Total 360 JPY",
    "Invoice #C-9 from Suzuki Tools, 2026-11-02. 5 x drill bits at 300 JPY. Total 1500 JPY",
    "Invoice #D-31 from Sato Metal, 2026-09-18. 10 x washers at 15 JPY, 2 x nuts at 40 JPY. Total 230 JPY",
    "Invoice #E-77 from Kobayashi Electric, 2026-10-30. 4 x relays at 850 JPY. Total 3400 JPY",
    "Invoice #F-12 from Yamada Plastics, 2026-08-05. 20 x caps at 35 JPY. Total 700 JPY",
    "Invoice #G-208 from Ito Fasteners, 2026-11-10. 100 x screws at 8 JPY. Total 800 JPY",
    "Invoice #H-4 from Nakamura Steel, 2026-07-22. 2 x plates at 5200 JPY. Total 10400 JPY",
    "Invoice #J-55 from Kato Rubber, 2026-10-01. 8 x gaskets at 220 JPY. Total 1760 JPY",
    "Invoice #K-90 from Watanabe Cables, 2026-09-09. 6 x cables at 480 JPY. Total 2880 JPY",
    "Invoice #L-17 from Takahashi Paints, 2026-11-14. 3 x cans at 1200 JPY. Total 3600 JPY",
]


def tok(s: str) -> int:
    return len(ENC.encode(s))


def per_request(model, in_tok, out_tok, static_tok, use_cache):
    p_in, p_cached, p_out = PRICING[model]
    if use_cache and static_tok >= MIN_CACHEABLE:
        billed_in = (in_tok - static_tok) * p_in + static_tok * p_cached
    else:
        billed_in = in_tok * p_in
    return (billed_in + out_tok * REASONING_OVERHEAD * p_out) / 1_000_000


def main():
    static_tok = tok(SYSTEM_PROMPT)
    rows, cached_hits = [], 0

    with httpx.Client(timeout=300) as client:
        for text in SAMPLES:
            r = client.post(API, json={"text": text})
            r.raise_for_status()
            body = r.json()
            if body.get("cached"):
                cached_hits += 1
            rows.append({
                "in": static_tok + tok(text),
                "out": tok(json.dumps(body["data"])),
                "ms": None if body.get("cached") else body["latency_ms"],
            })

    avg_in = statistics.mean(r["in"] for r in rows)
    avg_out = statistics.mean(r["out"] for r in rows)
    latencies = [r["ms"] for r in rows if r["ms"] is not None]
    avg_s = (statistics.mean(latencies) / 1000) if latencies else 0

    print(f"\nRequests profiled : {len(rows)}")
    print(f"Static prompt     : {static_tok} tokens (cacheable: {static_tok >= MIN_CACHEABLE})")
    print(f"Avg input tokens  : {avg_in:.0f}")
    print(f"Avg output tokens : {avg_out:.0f}")
    print(f"Avg latency       : {avg_s:.1f} s (local Ollama)")
    if cached_hits:
        print(f"NOTE: {cached_hits} requests came from the response cache; restart uvicorn and rerun for clean numbers.")
    if static_tok < MIN_CACHEABLE:
        print("NOTE: static prompt is under 1024 tokens, so prompt caching saves nothing. Lengthen it.")

    report = {"avg_input_tokens": avg_in, "avg_output_tokens": avg_out,
              "static_tokens": static_tok, "scenarios": {}}

    print(f"\n{'Model':<12}{'No cache':>14}{'Prompt cache':>16}{'+ Resp cache':>16}   (USD per 1000 requests)")
    for model in PRICING:
        base = per_request(model, avg_in, avg_out, static_tok, False) * 1000
        pc = per_request(model, avg_in, avg_out, static_tok, True) * 1000
        both = pc * (1 - CACHE_HIT_RATE)
        report["scenarios"][model] = {"no_cache": base, "prompt_cache": pc, "plus_response_cache": both}
        print(f"{model:<12}{base:>14.4f}{pc:>16.4f}{both:>16.4f}")

    kwh = GPU_WATTS * avg_s / 3600 / 1000
    local = kwh * USD_PER_KWH * 1000
    report["local_electricity_per_1000"] = local
    print(f"\nLocal Ollama      : ~${local:.4f} per 1000 requests (electricity only, "
          f"{GPU_WATTS} W at ${USD_PER_KWH}/kWh, excludes hardware)")
    print(f"Response-cache hit rate assumed: {CACHE_HIT_RATE:.0%}")

    with open("cost_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("\nSaved cost_report.json")


if __name__ == "__main__":
    main()