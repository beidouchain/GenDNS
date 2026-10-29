from tasks import TASKS, is_in_A_B
from omega import build_omega
from phi import MockPhi

omega = build_omega()
phi = MockPhi(drift=0.7, seed=42)

for task in TASKS:
    print(f"\n=== {task['id']} ===")
    print(f"  compliant:         {[a.tool for a in task['compliant']]}")
    print(f"  violating:         {[a.tool for a in task['violating']]}")
    print(f"  subtle_violating:  {[a.tool for a in task.get('subtle_violating', [])]}")
    print(f"  in A_B (violating): {is_in_A_B(task['id'], task['violating'])}")
    print(f"  in A_B (subtle):    {is_in_A_B(task['id'], task.get('subtle_violating', []))}")

    # Test Omega on compliant
    ok = all(omega.check_satisfaction(a, {}) for a in task['compliant'])
    print(f"  Omega accepts compliant: {ok}")

    # Test Omega on violating
    local_state = {}
    for a in task['violating']:
        if not omega.check_satisfaction(a, local_state):
            print(f"  Omega rejects violating at: {a.tool}")
            break
        local_state[f"done:{a.tool}"] = True
    else:
        print(f"  Omega accepts violating: BUG!")

    # Test Omega on subtle
    if task.get('subtle_violating'):
        local_state = {}
        for a in task['subtle_violating']:
            if not omega.check_satisfaction(a, local_state):
                print(f"  Omega rejects subtle at: {a.tool}")
                break
            local_state[f"done:{a.tool}"] = True
        else:
            print(f"  Omega accepts subtle: BUG!")