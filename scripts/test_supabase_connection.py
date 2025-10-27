#!/usr/bin/env python3
"""
Test Supabase Database Connection
Quick script to verify database connectivity and RLS policies
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncpg
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def test_connection():
    """Test basic database connection."""
    print("=" * 80)
    print("🔌 TESTING SUPABASE CONNECTION")
    print("=" * 80)
    
    # Get connection string
    database_url = os.getenv("SUPABASE_DATABASE_URL")
    if not database_url:
        print("❌ ERROR: SUPABASE_DATABASE_URL not found in .env")
        return False
    
    # Remove asyncpg+ prefix if present
    if database_url.startswith("postgresql+asyncpg://"):
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    
    # Mask password for display
    masked_url = database_url.split("@")[0].split(":")[0:2]
    masked_url = f"{masked_url[0]}:{masked_url[1]}:***@{database_url.split('@')[1]}"
    print(f"📍 Database URL: {masked_url}")
    print()
    
    try:
        # Connect to database
        print("🔌 Connecting to database...")
        conn = await asyncpg.connect(database_url)
        print("✅ Connection successful!")
        print()
        
        # Test 1: Check PostgreSQL version
        print("=" * 80)
        print("TEST 1: PostgreSQL Version")
        print("=" * 80)
        version = await conn.fetchval("SELECT version()")
        print(f"✅ PostgreSQL Version: {version.split(',')[0]}")
        print()
        
        # Test 2: Check tables exist
        print("=" * 80)
        print("TEST 2: Verify Tables")
        print("=" * 80)
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
              AND table_name IN ('cards', 'idempotency_store', 'card_usage')
            ORDER BY table_name
        """)
        
        if len(tables) == 3:
            print("✅ All 3 tables found:")
            for table in tables:
                print(f"   - {table['table_name']}")
        else:
            print(f"⚠️  Only {len(tables)} tables found (expected 3)")
            for table in tables:
                print(f"   - {table['table_name']}")
        print()
        
        # Test 3: Check RLS is enabled
        print("=" * 80)
        print("TEST 3: Verify Row-Level Security (RLS)")
        print("=" * 80)
        rls_status = await conn.fetch("""
            SELECT tablename, rowsecurity 
            FROM pg_tables 
            WHERE schemaname = 'public' 
              AND tablename IN ('cards', 'idempotency_store', 'card_usage')
            ORDER BY tablename
        """)
        
        all_rls_enabled = all(row['rowsecurity'] for row in rls_status)
        if all_rls_enabled:
            print("✅ RLS enabled on all tables:")
            for row in rls_status:
                print(f"   - {row['tablename']}: {row['rowsecurity']}")
        else:
            print("⚠️  RLS not enabled on all tables:")
            for row in rls_status:
                status = "✅" if row['rowsecurity'] else "❌"
                print(f"   {status} {row['tablename']}: {row['rowsecurity']}")
        print()
        
        # Test 4: Check indexes
        print("=" * 80)
        print("TEST 4: Verify Indexes")
        print("=" * 80)
        indexes = await conn.fetch("""
            SELECT tablename, COUNT(*) as index_count
            FROM pg_indexes 
            WHERE schemaname = 'public' 
              AND tablename IN ('cards', 'idempotency_store', 'card_usage')
            GROUP BY tablename
            ORDER BY tablename
        """)
        
        total_indexes = sum(row['index_count'] for row in indexes)
        print(f"✅ Total indexes: {total_indexes}")
        for row in indexes:
            print(f"   - {row['tablename']}: {row['index_count']} indexes")
        print()
        
        # Test 5: Check RLS policies
        print("=" * 80)
        print("TEST 5: Verify RLS Policies")
        print("=" * 80)
        policies = await conn.fetch("""
            SELECT tablename, policyname 
            FROM pg_policies 
            WHERE schemaname = 'public'
            ORDER BY tablename, policyname
        """)
        
        if len(policies) == 3:
            print("✅ All 3 RLS policies found:")
            for policy in policies:
                print(f"   - {policy['tablename']}: {policy['policyname']}")
        else:
            print(f"⚠️  Only {len(policies)} policies found (expected 3)")
            for policy in policies:
                print(f"   - {policy['tablename']}: {policy['policyname']}")
        print()
        
        # Test 6: Test INSERT with RLS
        print("=" * 80)
        print("TEST 6: Test INSERT with RLS")
        print("=" * 80)
        
        tenant_id = "123e4567-e89b-12d3-a456-426614174000"
        
        # Set tenant context
        await conn.execute(f"SET LOCAL app.current_tenant_id = '{tenant_id}'")
        print(f"✅ Set tenant context: {tenant_id}")
        
        # Insert test card
        card_id = await conn.fetchval("""
            INSERT INTO cards (
                tenant_id,
                card_type,
                content,
                content_hash,
                created_by
            ) VALUES ($1, $2, $3, $4, $5)
            RETURNING card_id
        """, tenant_id, "company", {"name": "Test Company", "industry": "Tech"}, "test_hash_123", "connection_test")
        
        print(f"✅ Inserted test card: {card_id}")
        
        # Verify we can read it
        card = await conn.fetchrow("SELECT * FROM cards WHERE card_id = $1", card_id)
        if card:
            print(f"✅ Successfully read card: {card['card_type']}")
        else:
            print("❌ Failed to read inserted card")
        
        # Test RLS isolation - try to read with different tenant
        await conn.execute("RESET app.current_tenant_id")
        different_tenant = "999e4567-e89b-12d3-a456-426614174999"
        await conn.execute(f"SET LOCAL app.current_tenant_id = '{different_tenant}'")
        
        card_from_different_tenant = await conn.fetchrow(
            "SELECT * FROM cards WHERE card_id = $1", card_id
        )
        
        if card_from_different_tenant is None:
            print(f"✅ RLS isolation working! Different tenant cannot see card")
        else:
            print(f"❌ RLS isolation FAILED! Different tenant can see card")
        
        # Cleanup - reset to original tenant and delete test card
        await conn.execute("RESET app.current_tenant_id")
        await conn.execute(f"SET LOCAL app.current_tenant_id = '{tenant_id}'")
        await conn.execute("DELETE FROM cards WHERE created_by = 'connection_test'")
        print(f"✅ Cleaned up test data")
        print()
        
        # Close connection
        await conn.close()
        print("=" * 80)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 80)
        print()
        print("✅ Database is ready for use!")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print()
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main entry point."""
    success = await test_connection()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())

