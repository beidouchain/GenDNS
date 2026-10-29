from tasks import TASKS, is_in_A_B
from omega import build_omega

omega = build_omega()
for task in TASKS:
    subtle = task.get("subtle_violating", [])
    if not subtle:
        print(f"{task['id']}: NO subtle_violating")
        continue

    in_ab = is_in_A_B(task["id"], subtle)
    local_state = {}
    omega_rejects = False
    for a in subtle:
        if not omega.check_satisfaction(a, local_state):
            omega_rejects = True
            break
        local_state[f"done:{a.tool}"] = True
        local_state["last_tool"] = a.tool

    status = "✓" if (not in_ab and omega_rejects) else "✗"
    print(f"{status} {task['id']}: in_A_B={in_ab}, omega_rejects={omega_rejects}")