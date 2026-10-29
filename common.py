"""Shared logic for mock and API experiments."""
import statistics
from tasks import A_B_TUPLE


def simulate_execution(actions, state):
    for a in actions:
        state[f"done:{a.tool}"] = True
        state["last_tool"] = a.tool
    return state


def run_one(task, phi, validator, omega, max_rollback):
    state = {}
    executed_actions = []
    rollback_count = 0
    phi_hint = None
    first_attempt_violating = False

    for attempt in range(max_rollback + 1):
        actions = phi.plan(task, phi_hint)
        if attempt == 0:
            first_attempt_violating = task["checker"](actions)

        ok, reason, new_hint = validator.validate(task, actions, state, omega)
        if ok:
            executed_actions = actions
            simulate_execution(actions, state)
            break
        else:
            rollback_count += 1
            phi_hint = new_hint

    violated = bool(executed_actions) and task["checker"](executed_actions)
    return {
        "task_id": task["id"],
        "executed": len(executed_actions) > 0,
        "violated": violated,
        "rollback_count": rollback_count,
        "first_attempt_violating": first_attempt_violating,
    }


def compute_metrics(results):
    n = len(results)
    return {
        "VER":                sum(r["violated"] for r in results) / n,
        "completion":         sum(r["executed"] for r in results) / n,
        "rollbacks":          sum(r["rollback_count"] for r in results) / n,
        "epsilon_phi":        sum(r["first_attempt_violating"] for r in results) / n,
    }


def average_metrics(metric_list):
    keys = metric_list[0].keys()
    avg, std = {}, {}
    for k in keys:
        vals = [m[k] for m in metric_list]
        avg[k] = statistics.mean(vals)
        std[k] = statistics.pstdev(vals) if len(vals) > 1 else 0.0
    avg["std"] = std
    return avg


def measure_c(tasks):
    """Fraction of true violations covered by A_B."""
    total = covered = 0
    for task in tasks:
        for key in ("violating", "subtle_violating"):
            plan = task[key]
            if not task["checker"](plan):
                continue
            total += 1
            if (task["id"], tuple(a.tool for a in plan)) in A_B_TUPLE:
                covered += 1
    return covered / total if total else 0.0


def measure_beta(tasks, omega):
    """Fraction of true violations that Omega rejects."""
    total = rejected = 0
    for task in tasks:
        for key in ("violating", "subtle_violating"):
            plan = task[key]
            if not task["checker"](plan):
                continue
            total += 1
            local = {}
            for a in plan:
                if not omega.check_satisfaction(a, local):
                    rejected += 1
                    break
                local[f"done:{a.tool}"] = True
    return rejected / total if total else 0.0


def print_summary(rows, backend):
    """rows: list of dict with keys group, drift, VER, std, completion,
    comp_std, rollbacks, beta, c, delta. Any of drift / delta may be None."""
    print("\n=== Summary ===")
    header = (f"{'Group':<12}{'Drift':<7}{'VER':<18}"
              f"{'Completion':<18}{'Rollbacks':<11}"
              f"{'beta':<7}{'c':<7}{'Delta':<9}")
    print(header)
    print("-" * len(header))

    for r in rows:
        drift_str = f"{r['drift']:<7.2f}" if r.get("drift") is not None else f"{'—':<7}"
        delta_str = f"{r['delta']:<9.4f}" if r.get("delta") is not None else f"{'—':<9}"
        print(
            f"{r['group']:<12}{drift_str}"
            f"{r['VER']:.3f}±{r['std']:<10.3f}"
            f"{r['completion']:.3f}±{r['comp_std']:<10.3f}"
            f"{r['rollbacks']:<11.2f}"
            f"{r['beta']:<7.3f}"
            f"{r['c']:<7.3f}"
            f"{delta_str}"
        )