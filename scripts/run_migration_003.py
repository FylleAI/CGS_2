#!/usr/bin/env python3
"""
Migration Script 003: Create company_contexts table

This script creates the company_contexts table for the RAG system.

Usage:
    python scripts/run_migration_003.py [--dry-run]

Options:
    --dry-run    Print SQL without executing
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env")
    sys.exit(1)


def read_migration_file() -> str:
    """Read the migration SQL file."""
    migration_path = Path(__file__).parent.parent / "onboarding" / "infrastructure" / "database" / "migrations" / "003_create_company_contexts.sql"
    
    if not migration_path.exists():
        print(f"❌ Error: Migration file not found at {migration_path}")
        sys.exit(1)
    
    with open(migration_path, "r", encoding="utf-8") as f:
        return f.read()


def check_table_exists(supabase) -> bool:
    """Check if company_contexts table already exists."""
    try:
        result = supabase.table("company_contexts").select("context_id").limit(1).execute()
        return True
    except Exception:
        return False


def check_column_exists(supabase) -> bool:
    """Check if company_context_id column exists in onboarding_sessions."""
    try:
        result = supabase.table("onboarding_sessions").select("company_context_id").limit(1).execute()
        return True
    except Exception:
        return False


def run_migration(dry_run: bool = False):
    """Run the migration."""
    print("=" * 80)
    print("Migration 003: Create company_contexts table")
    print("=" * 80)
    print()
    
    # Read SQL
    sql = read_migration_file()
    
    if dry_run:
        print("🔍 DRY RUN MODE - SQL to be executed:")
        print("-" * 80)
        print(sql)
        print("-" * 80)
        print()
        print("✅ Dry run complete. No changes made.")
        return
    
    # Connect to Supabase
    print("🔌 Connecting to Supabase...")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Connected")
    print()
    
    # Check if already migrated
    print("🔍 Checking if migration already applied...")
    table_exists = check_table_exists(supabase)
    column_exists = check_column_exists(supabase)
    
    if table_exists and column_exists:
        print("⚠️  Migration already applied!")
        print("   - company_contexts table exists")
        print("   - company_context_id column exists in onboarding_sessions")
        print()
        
        response = input("Do you want to re-run the migration? (yes/no): ")
        if response.lower() not in ["yes", "y"]:
            print("❌ Migration cancelled")
            return
    
    # Execute migration
    print("🚀 Executing migration...")
    print()
    
    try:
        # Note: Supabase Python client doesn't support raw SQL execution directly
        # We need to use the REST API or execute via Supabase dashboard
        print("⚠️  IMPORTANT: Supabase Python client doesn't support raw SQL execution.")
        print()
        print("Please execute the migration manually:")
        print()
        print("1. Go to Supabase Dashboard → SQL Editor")
        print("2. Copy the SQL from: onboarding/infrastructure/database/migrations/003_create_company_contexts.sql")
        print("3. Paste and execute")
        print()
        print("Or use the Supabase CLI:")
        print("   supabase db execute -f onboarding/infrastructure/database/migrations/003_create_company_contexts.sql")
        print()
        
        # Save SQL to a temporary file for easy copy
        temp_sql_path = Path(__file__).parent.parent / "migration_003_to_execute.sql"
        with open(temp_sql_path, "w", encoding="utf-8") as f:
            f.write(sql)
        
        print(f"📄 SQL saved to: {temp_sql_path}")
        print("   You can copy this file content to Supabase SQL Editor")
        print()
        
    except Exception as e:
        print(f"❌ Error executing migration: {e}")
        sys.exit(1)


def verify_migration():
    """Verify the migration was successful."""
    print("=" * 80)
    print("Verifying Migration 003")
    print("=" * 80)
    print()
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Check table exists
    print("🔍 Checking company_contexts table...")
    table_exists = check_table_exists(supabase)
    
    if table_exists:
        print("✅ company_contexts table exists")
        
        # Try to get count
        try:
            result = supabase.table("company_contexts").select("context_id", count="exact").execute()
            count = result.count if hasattr(result, 'count') else 0
            print(f"   Current records: {count}")
        except Exception as e:
            print(f"   ⚠️  Could not get count: {e}")
    else:
        print("❌ company_contexts table NOT found")
    
    print()
    
    # Check column exists
    print("🔍 Checking company_context_id column in onboarding_sessions...")
    column_exists = check_column_exists(supabase)
    
    if column_exists:
        print("✅ company_context_id column exists")
    else:
        print("❌ company_context_id column NOT found")
    
    print()
    
    if table_exists and column_exists:
        print("🎉 Migration verified successfully!")
    else:
        print("⚠️  Migration incomplete. Please check Supabase dashboard.")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run migration 003")
    parser.add_argument("--dry-run", action="store_true", help="Print SQL without executing")
    parser.add_argument("--verify", action="store_true", help="Verify migration was applied")
    
    args = parser.parse_args()
    
    if args.verify:
        verify_migration()
    else:
        run_migration(dry_run=args.dry_run)

