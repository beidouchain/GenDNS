"""6 validator modes."""
from tasks import A_B_TUPLE


class ValidatorA:
    name = "A_single_track"
    def validate(self, task, action, state, omega):
        return True, "no_validation", None


class ValidatorB:
    name = "B_single_track_A_B"
    def validate(self, task, action, state, omega):
        key = (task["id"], tuple(a.tool for a in action))
        if key in A_B_TUPLE:
            return False, "in_A_B", "blind_retry"
        return True, "passed", None


class ValidatorC:
    """Dual track. `coverage` controls Omega's constraint implementation."""
    def __init__(self, label, coverage):
        self.name = label
        self.coverage = coverage

    def validate(self, task, action, state, omega):
        local_state = dict(state)
        for a in action:
            v = omega.first_violation(a, local_state)
            if v is not None:
                hint = f"violated:{a.tool}"
                return False, hint, hint
            local_state[f"done:{a.tool}"] = True
            local_state["last_tool"] = a.tool
        return True, "passed", None