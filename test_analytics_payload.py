#!/usr/bin/env python3
"""Test analytics payload building."""

import sys
from uuid import uuid4
from datetime import datetime

sys.path.insert(0, '/c/Users/david/Desktop/onboarding')

from services.onboarding.application.builders.payload_builder import PayloadBuilder
from services.onboarding.domain.models import (
    OnboardingGoal,
    CompanySnapshot,
    CompanyInfo,
    AudienceInfo,
    VoiceInfo,
    InsightsInfo,
    ClarifyingQuestion
)

def test_analytics_payload():
    """Test building analytics payload."""
    
    # Create minimal snapshot
    snapshot = CompanySnapshot(
        version='1.0',
        snapshot_id=uuid4(),
        generated_at=datetime.utcnow(),
        trace_id='test-trace',
        company=CompanyInfo(
            name='Test Company',
            description='A test company for analytics',
            industry='Technology',
            key_offerings=['Product A', 'Service B'],
            differentiators=['Innovation', 'Quality'],
            evidence=[]
        ),
        audience=AudienceInfo(
            primary='Business professionals',
            pain_points=['Challenge 1', 'Challenge 2']
        ),
        voice=VoiceInfo(
            tone='professional',
            style_guidelines=['Clear', 'Concise']
        ),
        insights=InsightsInfo(),
        clarifying_questions=[
            ClarifyingQuestion(
                id='q1',
                question='What is your primary business objective?',
                reason='Understanding your goals helps us provide better insights',
                expected_response_type='text'
            ),
            ClarifyingQuestion(
                id='q2',
                question='What is your target market?',
                reason='Knowing your market helps us analyze opportunities',
                expected_response_type='text'
            ),
            ClarifyingQuestion(
                id='q3',
                question='What is your biggest challenge?',
                reason='Understanding challenges helps us identify quick wins',
                expected_response_type='text'
            )
        ],
        clarifying_answers={
            'q1': 'Increase market share',
            'q2': 'Enterprise customers',
            'q3': 'Competition'
        }
    )
    
    # Create payload builder
    builder = PayloadBuilder()
    
    # Try to build analytics payload
    try:
        print('🔧 Building analytics payload...')
        print(f'   Goal: {OnboardingGoal.COMPANY_ANALYTICS}')
        print(f'   Company: {snapshot.company.name}')
        print(f'   Questions: {len(snapshot.clarifying_questions)}')
        print(f'   Answers: {len(snapshot.clarifying_answers)}')
        print()
        
        payload = builder.build_payload(
            session_id=uuid4(),
            trace_id='test-trace-123',
            snapshot=snapshot,
            goal=OnboardingGoal.COMPANY_ANALYTICS,
            dry_run=True,
            requested_provider='gemini'
        )
        
        print('✅ Payload built successfully!')
        print(f'   Type: {type(payload).__name__}')
        print(f'   Workflow: {payload.workflow}')
        print(f'   Goal: {payload.goal}')
        print(f'   Session ID: {payload.session_id}')
        print(f'   Trace ID: {payload.trace_id}')
        print(f'   Has company_snapshot: {payload.company_snapshot is not None}')
        print(f'   Has clarifying_answers: {len(payload.clarifying_answers)} answers')
        print(f'   Has input: {payload.input is not None}')
        print(f'   Input content_type: {payload.input.content_type}')
        print(f'   Has metadata: {payload.metadata is not None}')
        print(f'   Metadata provider: {payload.metadata.requested_provider}')
        print()
        
        # Try to serialize
        print('🔧 Serializing payload to dict...')
        payload_dict = payload.model_dump(mode='json')
        print(f'✅ Serialized successfully!')
        print(f'   Keys: {list(payload_dict.keys())}')
        print(f'   Workflow: {payload_dict.get("workflow")}')
        print(f'   Goal: {payload_dict.get("goal")}')
        print()
        
        print('🎉 ALL TESTS PASSED!')
        return True
        
    except Exception as e:
        print(f'❌ ERROR: {e}')
        print()
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_analytics_payload()
    sys.exit(0 if success else 1)

