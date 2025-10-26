"""
Tests for Fylle Shared Enums
"""

import pytest

from fylle_shared.enums import CardType, WorkflowType


class TestCardType:
    """Tests for CardType enum"""
    
    def test_card_type_values(self):
        """Test that CardType has correct v1 values"""
        assert CardType.COMPANY.value == "company"
        assert CardType.AUDIENCE.value == "audience"
        assert CardType.VOICE.value == "voice"
        assert CardType.INSIGHT.value == "insight"
    
    def test_card_type_count(self):
        """Test that only 4 card types exist in v1"""
        assert len(CardType) == 4
    
    def test_card_type_from_string(self):
        """Test creating CardType from string"""
        assert CardType("company") == CardType.COMPANY
        assert CardType("audience") == CardType.AUDIENCE
    
    def test_card_type_invalid(self):
        """Test that invalid card type raises error"""
        with pytest.raises(ValueError):
            CardType("invalid")


class TestWorkflowType:
    """Tests for WorkflowType enum"""
    
    def test_workflow_type_values(self):
        """Test that WorkflowType has correct values"""
        assert WorkflowType.PREMIUM_NEWSLETTER.value == "premium_newsletter"
        assert WorkflowType.ONBOARDING_CONTENT.value == "onboarding_content"
    
    def test_workflow_type_from_string(self):
        """Test creating WorkflowType from string"""
        assert WorkflowType("premium_newsletter") == WorkflowType.PREMIUM_NEWSLETTER
    
    def test_workflow_type_invalid(self):
        """Test that invalid workflow type raises error"""
        with pytest.raises(ValueError):
            WorkflowType("invalid")

