"""Structured Action Primitive (SAP) - the unified action representation."""
from dataclasses import dataclass, field
import json


@dataclass
class SAP:
    tool: str
    params: dict = field(default_factory=dict)
    target: str = ""

    def to_dict(self):
        return {"tool": self.tool, "params": self.params, "target": self.target}

    def canonical(self):
        return json.dumps(self.to_dict(), sort_keys=True)

    def __repr__(self):
        return f"SAP({self.tool}->{self.target})"


def sap(tool, target="", **params):
    """Helper to quickly build a SAP."""
    return SAP(tool=tool, params=params, target=target)