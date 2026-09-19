"""
Unit tests for dispute domain models.
"""

import pytest
from src.models.dispute import (
    DisputeIntent,
    DisputeIntentDetailed,
    IntentType,
    Severity,
)


class TestDisputeIntent:
    """Test suite for DisputeIntent model."""
    
    def test_create_valid_dispute_intent(self):
        """Test creating a valid DisputeIntent."""
        intent = DisputeIntent(
            intent_type=IntentType.OVERCHARGE,
            severity=Severity.HIGH,
            raw_text="I was charged $5000 for API usage this month, but I never made any API calls.",
            confidence_score=0.96
        )
        
        assert intent.intent_type == IntentType.OVERCHARGE
        assert intent.severity == Severity.HIGH
        assert intent.confidence_score == 0.96
        assert "never made any API calls" in intent.raw_text
    
    def test_dispute_intent_json_serialization(self):
        """Test JSON serialization of DisputeIntent."""
        intent = DisputeIntent(
            intent_type=IntentType.OVERCHARGE,
            severity=Severity.HIGH,
            raw_text="I was charged $5000 for API usage this month, but I never made any API calls.",
            confidence_score=0.96
        )
        
        json_str = intent.model_dump_json()
        assert "OVERCHARGE" in json_str
        assert "0.96" in json_str
    
    def test_confidence_score_validation_too_high(self):
        """Test that confidence_score > 1.0 raises validation error."""
        with pytest.raises(ValueError):
            DisputeIntent(
                intent_type=IntentType.OVERCHARGE,
                severity=Severity.HIGH,
                raw_text="Test dispute",
                confidence_score=1.5
            )
    
    def test_confidence_score_validation_negative(self):
        """Test that negative confidence_score raises validation error."""
        with pytest.raises(ValueError):
            DisputeIntent(
                intent_type=IntentType.OVERCHARGE,
                severity=Severity.HIGH,
                raw_text="Test dispute",
                confidence_score=-0.1
            )
    
    def test_raw_text_required(self):
        """Test that raw_text is required and non-empty."""
        with pytest.raises(ValueError):
            DisputeIntent(
                intent_type=IntentType.OVERCHARGE,
                severity=Severity.HIGH,
                raw_text="",
                confidence_score=0.95
            )
    
    def test_all_intent_types(self):
        """Test that all IntentType enum values are valid."""
        intent_types = [
            IntentType.OVERCHARGE,
            IntentType.WRONG_PLAN,
            IntentType.MISSING_CREDIT,
            IntentType.DUPLICATE_CHARGE,
            IntentType.TAX_ERROR,
            IntentType.REFUND_REQUEST,
            IntentType.SERVICE_QUALITY,
            IntentType.OTHER,
        ]
        
        for intent_type in intent_types:
            intent = DisputeIntent(
                intent_type=intent_type,
                severity=Severity.HIGH,
                raw_text="Test",
                confidence_score=0.95
            )
            assert intent.intent_type == intent_type


class TestDisputeIntentDetailed:
    """Test suite for DisputeIntentDetailed model."""
    
    def test_create_detailed_intent(self):
        """Test creating a DisputeIntentDetailed with metadata."""
        intent = DisputeIntentDetailed(
            intent_type=IntentType.OVERCHARGE,
            severity=Severity.HIGH,
            raw_text="I was charged $5000 for API usage this month, but I never made any API calls.",
            confidence_score=0.96,
            root_cause_candidates=["Incorrect usage calculation", "Rate mismatch"],
            key_phrases=["never made any API calls", "$5000", "this month"],
            extracted_amount=5000.00,
            extracted_time_period="this month"
        )
        
        assert intent.intent_type == IntentType.OVERCHARGE
        assert len(intent.root_cause_candidates) == 2
        assert 5000.00 == intent.extracted_amount
        assert intent.extracted_time_period == "this month"
    
    def test_detailed_intent_json_serialization(self):
        """Test JSON serialization of DisputeIntentDetailed."""
        intent = DisputeIntentDetailed(
            intent_type=IntentType.OVERCHARGE,
            severity=Severity.HIGH,
            raw_text="I was charged $5000 for API usage this month, but I never made any API calls.",
            confidence_score=0.96,
            root_cause_candidates=["Incorrect usage calculation"],
            key_phrases=["$5000"],
            extracted_amount=5000.00,
            extracted_time_period="this month"
        )
        
        json_str = intent.model_dump_json()
        assert "root_cause_candidates" in json_str
        assert "key_phrases" in json_str
        assert "extracted_amount" in json_str
    
    def test_detailed_intent_optional_fields(self):
        """Test that metadata fields are optional."""
        intent = DisputeIntentDetailed(
            intent_type=IntentType.OVERCHARGE,
            severity=Severity.HIGH,
            raw_text="Test dispute",
            confidence_score=0.95
        )
        
        assert intent.root_cause_candidates is None
        assert intent.key_phrases is None
        assert intent.extracted_amount is None
        assert intent.extracted_time_period is None


class TestSeverityEnum:
    """Test suite for Severity enum."""
    
    def test_all_severity_levels(self):
        """Test that all Severity enum values are available."""
        assert Severity.CRITICAL.value == "CRITICAL"
        assert Severity.HIGH.value == "HIGH"
        assert Severity.MEDIUM.value == "MEDIUM"
        assert Severity.LOW.value == "LOW"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
