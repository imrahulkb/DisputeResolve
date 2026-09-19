"""
Pydantic models for dispute domain entities.
"""

from enum import Enum
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict


class IntentType(str, Enum):
    """Enumeration of dispute intent types."""
    OVERCHARGE = "OVERCHARGE"
    WRONG_PLAN = "WRONG_PLAN"
    MISSING_CREDIT = "MISSING_CREDIT"
    DUPLICATE_CHARGE = "DUPLICATE_CHARGE"
    TAX_ERROR = "TAX_ERROR"
    REFUND_REQUEST = "REFUND_REQUEST"
    SERVICE_QUALITY = "SERVICE_QUALITY"
    OTHER = "OTHER"


class Severity(str, Enum):
    """Enumeration of dispute severity levels."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class DisputeIntent(BaseModel):
    """
    Pydantic model representing structured intent extracted from a dispute description.
    
    This is the output of Layer 1 (Intent Detection), where the LLM parses natural 
    language input and produces a structured classification.
    """
    
    intent_type: IntentType = Field(
        ...,
        description="Categorized type of dispute (overcharge, wrong plan, etc.)"
    )
    
    severity: Severity = Field(
        ...,
        description="Severity level of the dispute"
    )
    
    raw_text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Original natural language dispute description from customer"
    )
    
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="LLM confidence score for the intent classification (0.0 to 1.0)"
    )
    
    model_config = ConfigDict(
        use_enum_values=False,
        json_schema_extra={
            "example": {
                "intent_type": "OVERCHARGE",
                "severity": "HIGH",
                "raw_text": "I was charged $5000 for API usage this month, but I never made any API calls.",
                "confidence_score": 0.96
            }
        }
    )
    
    @field_validator("confidence_score")
    @classmethod
    def validate_confidence_score(cls, v: float) -> float:
        """Ensure confidence score is valid probability."""
        if not (0.0 <= v <= 1.0):
            raise ValueError("confidence_score must be between 0.0 and 1.0")
        return v


class DisputeIntentDetailed(DisputeIntent):
    """Extended DisputeIntent model with additional analysis metadata."""
    
    root_cause_candidates: Optional[List[str]] = Field(
        default=None,
        description="List of potential root causes identified by the LLM"
    )
    
    key_phrases: Optional[List[str]] = Field(
        default=None,
        description="Important phrases extracted from raw_text"
    )
    
    extracted_amount: Optional[float] = Field(
        default=None,
        description="Dollar amount mentioned in the dispute (if any)"
    )
    
    extracted_time_period: Optional[str] = Field(
        default=None,
        description="Time period referenced (e.g., 'this month', 'April 2026')"
    )
