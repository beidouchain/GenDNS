"""Mock experiment: 6 groups × 5 drifts × 10 seeds."""
import json
import os
import statistics

from tasks import TASKS
from omega import build_omega
from phi import MockPhi
from validator import ValidatorA, ValidatorB, ValidatorC
from common import (
    run_one, compute_metrics, average_metrics,
    measure_c, measure_beta, print_summary,
)


DRIFTS = [0.15, 0.20, 0.35, 0.50, 0.75]
SEEDS  = [42, 43, 44, 45, 46, 47, 48, 49, 50, 51]
K_ROLLBACK = 3

# (label, validator_factory, coverage, needs_omega)
GROUPS = [
    ("A",      lambda: ValidatorA(),            None,  False),
    ("B",      lambda: ValidatorB(),            None,  False),
    ("C-full", lambda: ValidatorC("C-full", 1.00), 1.00, True),
    ("C-high", lambda: ValidatorC("C-high", 0.75), 0.75, True),
    ("C-equal",lambda: ValidatorC("C-equal", 0.50), 0.50, True),
    ("C-low",  lambda: ValidatorC("C-low", 0.25), 0.25, True),
]


def main():
    os.makedirs("results", exist_ok=True)

    c_value = measure_c(TASKS)
    print(f"Measured c (A_B coverage) = {c_value:.4f}")

    rows = []
    per_group_drift = {}   # {label: {drift: metrics}}

    for label, v_factory, cov, needs_omega in GROUPS:
        print(f"\n=== {label} ===")
        per_group_drift[label] = {}

        for drift in DRIFTS:
            seed_metrics = []
            seed_betas = []

            for seed in SEEDS:
                omega = build_omega(TASKS, coverage=(cov if cov is not None else 1.0),
                                    seed=seed+1000)
                phi = MockPhi(drift=drift, seed=seed)
                validator = v_factory()

                results = [
                    run_one(t, phi, validator, omega, max_rollback=K_ROLLBACK)
                    for t in TASKS
                ]
                seed_metrics.append(compute_metrics(results))

                if needs_omega:
                    seed_betas.append(measure_beta(TASKS, omega))

            m = average_metrics(seed_metrics)
            beta = statistics.mean(seed_betas) if seed_betas else 0.0

            row = {
                "group": label,
                "drift": drift,
                "VER": m["VER"],
                "std": m["std"]["VER"],
                "completion": m["completion"],
                "comp_std": m["std"]["completion"],
                "rollbacks": m["rollbacks"],
                "beta": beta,
                "c": c_value,
                "delta": None,     # filled below
            }
            per_group_drift[label][drift] = row
            rows.append(row)

            print(
                f"  drift={drift:.2f} | VER={row['VER']:.3f}±{row['std']:.3f}"
                f" | Comp={row['completion']:.3f}±{row['comp_std']:.3f}"
                f" | RB={row['rollbacks']:.2f}"
                f" | beta={beta:.3f}"
            )

    # Compute Delta = VER_B - VER_C for each C group
    print("\n=== Delta = VER_B - VER_C ===")
    for drift in DRIFTS:
        ver_b = per_group_drift["B"][drift]["VER"]
        for c_label in ["C-full", "C-high", "C-equal", "C-low"]:
            delta = ver_b - per_group_drift[c_label][drift]["VER"]
            per_group_drift[c_label][drift]["delta"] = delta
            print(f"  drift={drift:.2f} | {c_label}: Delta={delta:+.4f}")

    # Persist
    out = {"c": c_value, "rows": rows}
    with open("results/metrics_mock.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved results/metrics_mock.json")

    # Final summary
    print_summary([r for r in rows if r["delta"] is not None
                   or r["group"] in ("A", "B")], backend="mock")


if __name__ == "__main__":
    main()