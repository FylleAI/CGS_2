#!/usr/bin/env python3
"""
Database migration script for Cards API.

This script:
1. Creates the database if it doesn't exist (local only)
2. Applies the schema.sql migration
3. Verifies tables and RLS policies

Usage:
    python scripts/migrate_cards_db.py --local    # Migrate local PostgreSQL
    python scripts/migrate_cards_db.py --supabase # Migrate Supabase
"""

import asyncio
import asyncpg
import argparse
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

load_dotenv()


async def create_database_if_not_exists(connection_string: str, db_name: str):
    """
    Create database if it doesn't exist (local only).
    
    Args:
        connection_string: PostgreSQL connection string (without database name)
        db_name: Database name to create
    """
    try:
        # Connect to postgres database to create new database
        conn = await asyncpg.connect(connection_string)
        
        # Check if database exists
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1",
            db_name
        )
        
        if not exists:
            print(f"📦 Creating database: {db_name}")
            await conn.execute(f'CREATE DATABASE "{db_name}"')
            print(f"✅ Database created: {db_name}")
        else:
            print(f"✅ Database already exists: {db_name}")
        
        await conn.close()
    except Exception as e:
        print(f"⚠️ Could not create database (may already exist): {e}")


async def apply_migration(connection_string: str, schema_path: str):
    """
    Apply schema migration.
    
    Args:
        connection_string: PostgreSQL connection string
        schema_path: Path to schema.sql file
    """
    print(f"📜 Reading schema from: {schema_path}")
    
    with open(schema_path, "r") as f:
        schema_sql = f.read()
    
    print(f"🔌 Connecting to database...")
    conn = await asyncpg.connect(connection_string)
    
    try:
        print(f"🚀 Applying migration...")
        await conn.execute(schema_sql)
        print(f"✅ Migration applied successfully!")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        await conn.close()


async def verify_migration(connection_string: str):
    """
    Verify that migration was successful.
    
    Args:
        connection_string: PostgreSQL connection string
    """
    print(f"🔍 Verifying migration...")
    
    conn = await asyncpg.connect(connection_string)
    
    try:
        # Check tables
        tables = await conn.fetch("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        
        table_names = [row["table_name"] for row in tables]
        print(f"📊 Tables found: {', '.join(table_names)}")
        
        expected_tables = ["cards", "idempotency_store", "card_usage"]
        for table in expected_tables:
            if table in table_names:
                print(f"  ✅ {table}")
            else:
                print(f"  ❌ {table} (MISSING)")
        
        # Check RLS policies
        policies = await conn.fetch("""
            SELECT tablename, policyname
            FROM pg_policies
            WHERE schemaname = 'public'
            ORDER BY tablename, policyname
        """)
        
        print(f"\n🔒 RLS Policies:")
        for policy in policies:
            print(f"  ✅ {policy['tablename']}.{policy['policyname']}")
        
        # Check indexes
        indexes = await conn.fetch("""
            SELECT tablename, indexname
            FROM pg_indexes
            WHERE schemaname = 'public'
            AND indexname NOT LIKE '%_pkey'
            ORDER BY tablename, indexname
        """)
        
        print(f"\n📇 Indexes:")
        for index in indexes:
            print(f"  ✅ {index['tablename']}.{index['indexname']}")
        
        print(f"\n✅ Migration verification complete!")
        
    finally:
        await conn.close()


async def main():
    """Main migration function."""
    parser = argparse.ArgumentParser(description="Migrate Cards API database")
    parser.add_argument(
        "--local",
        action="store_true",
        help="Migrate local PostgreSQL database"
    )
    parser.add_argument(
        "--supabase",
        action="store_true",
        help="Migrate Supabase database"
    )
    
    args = parser.parse_args()
    
    if not args.local and not args.supabase:
        print("❌ Please specify --local or --supabase")
        sys.exit(1)
    
    # Get schema path
    schema_path = project_root / "cards" / "infrastructure" / "database" / "schema.sql"
    
    if not schema_path.exists():
        print(f"❌ Schema file not found: {schema_path}")
        sys.exit(1)
    
    if args.local:
        print("=" * 80)
        print("🏠 MIGRATING LOCAL DATABASE")
        print("=" * 80)
        
        # Get local database URL
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("❌ DATABASE_URL not set in .env")
            sys.exit(1)
        
        # Convert SQLAlchemy URL to asyncpg format
        if database_url.startswith("postgresql+asyncpg://"):
            database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        
        print(f"📍 Database URL: {database_url}")
        
        # Extract database name for creation
        # Format: postgresql://user:pass@host:port/dbname
        if "/" in database_url.split("://")[1]:
            db_name = database_url.split("/")[-1]
            base_url = database_url.rsplit("/", 1)[0] + "/postgres"
            
            # Create database if needed
            await create_database_if_not_exists(base_url, db_name)
        
        # Apply migration
        await apply_migration(database_url, str(schema_path))
        
        # Verify migration
        await verify_migration(database_url)
    
    if args.supabase:
        print("=" * 80)
        print("☁️  MIGRATING SUPABASE DATABASE")
        print("=" * 80)
        
        # Get Supabase database URL
        database_url = os.getenv("SUPABASE_DATABASE_URL")
        if not database_url:
            print("❌ SUPABASE_DATABASE_URL not set in .env")
            print("💡 Get it from: Supabase Dashboard -> Project Settings -> Database")
            print("💡 Format: postgresql://postgres:[PASSWORD]@db.xxx.supabase.co:5432/postgres")
            sys.exit(1)
        
        # Convert SQLAlchemy URL to asyncpg format
        if database_url.startswith("postgresql+asyncpg://"):
            database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        
        # Mask password for display
        masked_url = database_url
        if "@" in masked_url:
            parts = masked_url.split("@")
            if ":" in parts[0]:
                user_pass = parts[0].split("://")[1]
                user = user_pass.split(":")[0]
                masked_url = masked_url.replace(user_pass, f"{user}:***")
        
        print(f"📍 Database URL: {masked_url}")
        
        # Apply migration
        await apply_migration(database_url, str(schema_path))
        
        # Verify migration
        await verify_migration(database_url)
    
    print("\n" + "=" * 80)
    print("🎉 MIGRATION COMPLETE!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

