"""MockPhi: deterministic mock with drift = epsilon_Phi."""
import random


class MockPhi:
    def __init__(self, drift, seed):
        self.drift = drift
        self.rng = random.Random(seed)

    def plan(self, task, phi_hint=None):
        # Omega gave a concrete correction → return compliant
        if phi_hint and phi_hint.startswith("violated:"):
            return list(task["compliant"])

        # First attempt or blind retry → use drift
        r = self.rng.random()
        if r < self.drift * 0.5:
            return list(task["violating"])
        elif r < self.drift:
            return list(task["subtle_violating"])
        return list(task["compliant"])