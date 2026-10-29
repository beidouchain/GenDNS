# diagnose_extended.py
from tasks import TASKS, is_in_A_B
from omega import build_omega


def run_diagnosis():
    omega = build_omega()
    total = len(TASKS)
    passed = 0
    issues = []

    for task in TASKS:
        subtle = task.get("subtle_violating", [])
        if not subtle:
            issues.append(f"{task['id']}: NO subtle_violating")
            continue

        # Condition 1: subtle NOT in A_B
        in_ab = is_in_A_B(task["id"], subtle)

        # Condition 2: Omega rejects subtle
        local_state = {}
        omega_rejects = False
        for a in subtle:
            if not omega.check_satisfaction(a, local_state):
                omega_rejects = True
                break
            local_state[f"done:{a.tool}"] = True
            local_state["last_tool"] = a.tool

        # Condition 3: checker flags subtle as violation
        checker_flags = task["checker"](subtle)

        # Condition 4: checker accepts compliant
        checker_accepts_compliant = not task["checker"](task["compliant"])

        # Condition 5: checker flags violating
        checker_flags_violating = task["checker"](task["violating"])

        ok = (not in_ab) and omega_rejects and checker_flags \
             and checker_accepts_compliant and checker_flags_violating

        status = "✓" if ok else "✗"
        print(f"{status} {task['id']}: "
              f"A_B={in_ab}, Ω_reject={omega_rejects}, "
              f"checker_subtle={checker_flags}, "
              f"checker_compliant={checker_accepts_compliant}, "
              f"checker_violating={checker_flags_violating}")

        if ok:
            passed += 1
        else:
            issues.append(task["id"])

    print(f"\n{passed}/{total} tasks pass all conditions")
    if issues:
        print(f"Issues: {issues}")


if __name__ == "__main__":
    run_diagnosis()