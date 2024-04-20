"""OODA reasoner."""


from dataclasses import dataclass

from openssa.l2.reasoning.base import BaseReasoner


@dataclass
class OodaReasoner(BaseReasoner):
    """OODA reasoner."""

    max_depth: int = 3

    # TODO: full OODA reasoning
