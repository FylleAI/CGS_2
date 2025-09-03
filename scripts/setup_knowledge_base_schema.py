#!/usr/bin/env python3
"""
Setup Knowledge Base Schema in Supabase

This script creates the clients and documents tables required for PR #4
knowledge base operations using Supabase.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.infrastructure.config.settings import get_settings
from core.infrastructure.database.supabase_tracker import SupabaseTracker

def create_knowledge_base_tables():
    """Create the knowledge base tables in Supabase."""
    print("🚀 Setting up Knowledge Base schema in Supabase...")
    
    try:
        settings = get_settings()
        if not (settings.supabase_url and settings.supabase_anon_key):
            print("❌ Supabase credentials not configured")
            return False
            
        tracker = SupabaseTracker()
        client = tracker.client
        
        # Create clients table
        print("📋 Creating clients table...")
        clients_sql = """
        CREATE TABLE IF NOT EXISTS clients (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            name VARCHAR(100) UNIQUE NOT NULL,
            display_name VARCHAR(200) NOT NULL,
            description TEXT,
            brand_voice TEXT,
            target_audience TEXT,
            industry VARCHAR(100),
            rag_enabled BOOLEAN DEFAULT true,
            knowledge_base_path TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        # Create documents table
        print("📄 Creating documents table...")
        documents_sql = """
        CREATE TABLE IF NOT EXISTS documents (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
            title VARCHAR(500) NOT NULL,
            content TEXT NOT NULL,
            description TEXT,
            category VARCHAR(100),
            tags TEXT[] DEFAULT '{}',
            file_path TEXT,
            file_size INTEGER,
            file_type VARCHAR(50),
            metadata JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        # Create indexes
        print("🔍 Creating indexes...")
        indexes_sql = """
        CREATE INDEX IF NOT EXISTS idx_documents_client_id ON documents(client_id);
        CREATE INDEX IF NOT EXISTS idx_documents_category ON documents(category);
        CREATE INDEX IF NOT EXISTS idx_documents_tags ON documents USING GIN(tags);
        CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at DESC);
        """
        
        # Execute SQL commands
        client.rpc('exec_sql', {'sql': clients_sql}).execute()
        client.rpc('exec_sql', {'sql': documents_sql}).execute()
        client.rpc('exec_sql', {'sql': indexes_sql}).execute()
        
        print("✅ Knowledge Base schema created successfully!")
        
        # Insert default client (Siebert)
        print("👤 Creating default client (Siebert)...")
        siebert_data = {
            "name": "siebert",
            "display_name": "Siebert Financial",
            "description": "Financial services company focused on empowering individual investors",
            "brand_voice": "Professional yet accessible, empowering, educational, trustworthy",
            "target_audience": "Gen Z and young professionals interested in financial literacy",
            "industry": "Financial Services",
            "rag_enabled": True
        }
        
        # Check if client already exists
        existing = client.table("clients").select("id").eq("name", "siebert").execute()
        if not existing.data:
            client.table("clients").insert(siebert_data).execute()
            print("✅ Siebert client created!")
        else:
            print("ℹ️ Siebert client already exists")
            
        return True
        
    except Exception as e:
        print(f"❌ Error setting up schema: {e}")
        return False

if __name__ == "__main__":
    success = create_knowledge_base_tables()
    sys.exit(0 if success else 1)
