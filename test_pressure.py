"""Test whether KPI pressure induces violation with the real LLM."""
# test_pressure.py
import os
from tasks import TASKS
from phi_api import APIPhi

#os.environ.setdefault("OPENAI_API_KEY", "sk-6a752253634b4dd892d09a0f2ba8eecc")
#os.environ.setdefault("OPENAI_BASE_URL", "https://api.deepseek.com/v1")

#os.environ.setdefault("OPENAI_API_KEY", "sk-aergsimyhplyaomjyjgbwkavyrtstlcrxchgwupguoyidgqu")
#os.environ.setdefault("OPENAI_BASE_URL", "https://api.siliconflow.cn/v1")

#phi = APIPhi(model="deepseek-flash", min_interval=0.4)
phi = APIPhi(model="Qwen/Qwen3.5-4B", min_interval=0.4)

n_violations = 0
for task in TASKS[:6]:   # test on 6 tasks
    actions = phi.plan(task, phi_hint=None)
    is_violating = task["checker"](actions)
    n_violations += is_violating
    print(f"{task['id']}: {'VIOLATION' if is_violating else 'compliant'}"
          f" — {[a.tool for a in actions]}")

print(f"\nViolation rate on first attempt: {n_violations}/{6}")