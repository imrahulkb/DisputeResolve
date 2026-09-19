"""
Domain models for BillResolve dispute resolution system.
"""

from .dispute import (
    DisputeIntent,
    DisputeIntentDetailed,
    IntentType,
    Severity,
)

from .resolution import (
    ResolutionStep,
    ResolutionPlan,
    StepExecutionResult,
    StepType,
    StepStatus,
)

__all__ = [
    # Dispute models
    "DisputeIntent",
    "DisputeIntentDetailed",
    "IntentType",
    "Severity",
    # Resolution models
    "ResolutionStep",
    "ResolutionPlan",
    "StepExecutionResult",
    "StepType",
    "StepStatus",
]
