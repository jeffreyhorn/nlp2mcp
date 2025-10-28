"""Public surface for the IR package.

Only re-export the pieces that downstream passes are expected to rely on.
Keep everything else internal so we can iterate on the parser freely.
"""

from .model_ir import ModelIR, ObjectiveIR
from .normalize import NormalizedEquation, normalize_equation, normalize_model
from .symbols import ObjSense, Rel

__all__ = [
    "ModelIR",
    "ObjectiveIR",
    "NormalizedEquation",
    "normalize_equation",
    "normalize_model",
    "Rel",
    "ObjSense",
]
