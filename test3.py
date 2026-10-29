# diagnose_rollback.py
from tasks import TASKS
from phi import MockPhi
from omega import build_omega
from validator import ValidatorA, ValidatorB, ValidatorC

task = TASKS[0]  # 选一个任务
omega = build_omega()

print(f"Task: {task['id']}")
print(f"Compliant: {[a.tool for a in task['compliant']]}")
print(f"Subtle violating: {[a.tool for a in task.get('subtle_violating', [])]}")

for V in [ValidatorA, ValidatorB, ValidatorC]:
    validator = V()
    print(f"\n=== {validator.name} ===")

    # First attempt: force violation
    phi = MockPhi(drift=1.0, seed=42)
    actions = phi.plan(task, None)
    print(f"  First attempt: {[a.tool for a in actions]}")

    ok, reason, hint = validator.validate(task, actions, {}, omega)
    print(f"  Validation: ok={ok}, reason={reason}, hint={hint}")

    # Second attempt with hint
    phi2 = MockPhi(drift=1.0, seed=42)
    actions2 = phi2.plan(task, hint)
    print(f"  Second attempt: {[a.tool for a in actions2]}")