"""API experiment: 6 groups × N runs (no drift control)."""
import argparse
import json
import os
import statistics

from tasks import TASKS
from omega import build_omega
from validator import ValidatorA, ValidatorB, ValidatorC
from common import (
    run_one, compute_metrics, average_metrics,
    measure_c, measure_beta, print_summary,
)


K_ROLLBACK = 3

GROUPS = [
    ("A",       lambda: ValidatorA(),                None, False),
    ("B",       lambda: ValidatorB(),                None, False),
    ("C-full",  lambda: ValidatorC("C-full", 1.00),  1.00, True),
    ("C-high",  lambda: ValidatorC("C-high", 0.75),  0.75, True),
    ("C-equal", lambda: ValidatorC("C-equal", 0.50), 0.50, True),
    ("C-low",   lambda: ValidatorC("C-low", 0.25),   0.25, True),
]


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="gpt-4o-mini")
    p.add_argument("--api-key", default=None)
    p.add_argument("--base-url", default=None)
    p.add_argument("--temperature", type=float, default=0.7)
    p.add_argument("--max-retries", type=int, default=3)
    p.add_argument("--min-interval", type=float, default=0.4)
    p.add_argument("--runs", type=int, default=3)
    p.add_argument("--output", default="results")
    return p.parse_args()


def main():
    args = parse_args()
    os.makedirs(args.output, exist_ok=True)

    from phi_api import APIPhi

    c_value = measure_c(TASKS)
    print(f"Measured c (A_B coverage) = {c_value:.4f}")
    print(f"Runs per group: {args.runs}")

    rows = []
    per_group = {}

    for label, v_factory, cov, needs_omega in GROUPS:
        print(f"\n=== {label} ===")
        per_group[label] = []

        run_metrics, run_betas = [], []

        for run_idx in range(args.runs):
            phi = APIPhi(
                model=args.model, api_key=args.api_key,
                base_url=args.base_url, temperature=args.temperature,
                max_retries=args.max_retries, min_interval=args.min_interval,
            )
            omega = build_omega(TASKS,
                                coverage=(cov if cov is not None else 1.0),
                                seed=1000 + run_idx)
            validator = v_factory()

            results = [
                run_one(t, phi, validator, omega, max_rollback=K_ROLLBACK)
                for t in TASKS
            ]
            m = compute_metrics(results)
            run_metrics.append(m)
            if needs_omega:
                run_betas.append(measure_beta(TASKS, omega))

            print(f"  run={run_idx + 1}/{args.runs} | "
                  f"VER={m['VER']:.3f} | "
                  f"Comp={m['completion']:.3f} | "
                  f"eps_Phi={m['epsilon_phi']:.3f}")

        m = average_metrics(run_metrics)
        beta = statistics.mean(run_betas) if run_betas else 0.0

        row = {
            "group": label, "drift": None,
            "VER": m["VER"], "std": m["std"]["VER"],
            "completion": m["completion"], "comp_std": m["std"]["completion"],
            "rollbacks": m["rollbacks"],
            "beta": beta, "c": c_value, "delta": None,
        }
        per_group[label] = row
        rows.append(row)

    # Delta = VER_B - VER_C
    print("\n=== Delta = VER_B - VER_C ===")
    ver_b = per_group["B"]["VER"]
    for c_label in ["C-full", "C-high", "C-equal", "C-low"]:
        d = ver_b - per_group[c_label]["VER"]
        per_group[c_label]["delta"] = d
        print(f"  {c_label}: Delta = {d:+.4f}")

    out = {"c": c_value, "rows": rows}
    with open(os.path.join(args.output, "metrics_api.json"), "w") as f:
        json.dump(out, f, indent=2)
    print_summary([r for r in rows if r["delta"] is not None
                   or r["group"] in ("A", "B")], backend="api")


if __name__ == "__main__":
    main()