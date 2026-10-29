"""Track Omega: constraint maintainer with configurable coverage."""
import random


class Constraint:
    def __init__(self, trigger_tool, requires_prior):
        self.trigger_tool = trigger_tool
        self.requires_prior = requires_prior

    def satisfied_by(self, action, state):
        if action.tool == self.trigger_tool:
            for pre in self.requires_prior:
                if not state.get(f"done:{pre}", False):
                    return False
        return True


class OmegaTrack:
    def __init__(self, constraints):
        self.constraints = constraints

    def check_satisfaction(self, action, state):
        for c in self.constraints:
            if not c.satisfied_by(action, state):
                return False
        return True

    def first_violation(self, action, state):
        for c in self.constraints:
            if not c.satisfied_by(action, state):
                return c
        return None


def build_omega(tasks, coverage=1.0, seed=42):
    """Each task's constraint is independently implemented with
    probability `coverage`. When omitted, the constraint is not part
    of Omega's knowledge, so it cannot be violated from Omega's view.

    Beta = coverage.
    """
    rng = random.Random(seed)
    constraints = []
    for task in tasks:
        if rng.random() < coverage:
            constraints.append(Constraint(
                trigger_tool=task["trigger_tool"],
                requires_prior=[task["precondition_tool"]],
            ))
    return OmegaTrack(constraints)