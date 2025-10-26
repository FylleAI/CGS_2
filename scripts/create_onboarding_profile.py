"""Script to create onboarding generic profile in Supabase."""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.content_workflow.infrastructure.database.supabase_tracker import SupabaseTracker
from datetime import datetime

def create_onboarding_profile():
    """Create onboarding profile in Supabase clients table."""
    
    print("🔧 Creating onboarding profile in Supabase...")
    
    try:
        tracker = SupabaseTracker()
        client = tracker.client
        
        # Check if profile already exists
        existing = client.table('clients').select('*').eq('name', 'onboarding').execute()
        
        if existing.data:
            print(f"⚠️  Profile 'onboarding' already exists!")
            print(f"   ID: {existing.data[0]['id']}")
            print(f"   Display Name: {existing.data[0]['display_name']}")
            
            # Ask if user wants to update
            response = input("\n   Update existing profile? (y/n): ")
            if response.lower() == 'y':
                # Update existing profile
                result = client.table('clients').update({
                    'display_name': 'Onboarding Generic Profile',
                    'description': 'Generic client profile for onboarding flow with neutral, adaptable agents for all workflows',
                    'brand_voice': 'Professional, clear, and adaptable to any brand voice',
                    'target_audience': 'General audience across all industries',
                    'industry': 'Multi-industry',
                    'rag_enabled': True,
                    'knowledge_base_path': 'data/profiles/onboarding/knowledge_base',
                    'updated_at': datetime.utcnow().isoformat()
                }).eq('name', 'onboarding').execute()
                
                print("\n✅ Onboarding profile updated in Supabase!")
                print(f"   Profile ID: {result.data[0]['id']}")
                print(f"   Profile Name: {result.data[0]['name']}")
                print(f"   Display Name: {result.data[0]['display_name']}")
                return True
            else:
                print("   Skipping update.")
                return False
        
        # Insert new profile
        result = client.table('clients').insert({
            'name': 'onboarding',
            'display_name': 'Onboarding Generic Profile',
            'description': 'Generic client profile for onboarding flow with neutral, adaptable agents for all workflows',
            'brand_voice': 'Professional, clear, and adaptable to any brand voice',
            'target_audience': 'General audience across all industries',
            'industry': 'Multi-industry',
            'rag_enabled': True,
            'knowledge_base_path': 'data/profiles/onboarding/knowledge_base',
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }).execute()
        
        print("\n✅ Onboarding profile created in Supabase!")
        print(f"   Profile ID: {result.data[0]['id']}")
        print(f"   Profile Name: {result.data[0]['name']}")
        print(f"   Display Name: {result.data[0]['display_name']}")
        print(f"   Industry: {result.data[0]['industry']}")
        print(f"   RAG Enabled: {result.data[0]['rag_enabled']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error creating profile: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_onboarding_profile()
    sys.exit(0 if success else 1)

