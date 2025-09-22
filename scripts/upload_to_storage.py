#!/usr/bin/env python3
"""
Upload Knowledge Base documents from filesystem to Supabase Storage

This script uploads documents from the local knowledge_base directory
to the Supabase Storage bucket, then syncs to database tables.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.infrastructure.database.supabase_tracker import SupabaseTracker
from core.infrastructure.config.settings import get_settings


def upload_documents_to_storage():
    """Upload documents from filesystem to Supabase Storage."""
    print("📤 Uploading documents to Supabase Storage...")

    try:
        settings = get_settings()
        tracker = SupabaseTracker()
        client = tracker.client

        # Get local knowledge base directory
        kb_dir = Path(settings.knowledge_base_dir) / "siebert"
        if not kb_dir.exists():
            print(f"❌ Knowledge base directory not found: {kb_dir}")
            return False

        print(f"📁 Reading from: {kb_dir}")

        # Get all markdown files
        md_files = list(kb_dir.glob("*.md"))
        print(f"📄 Found {len(md_files)} markdown files")

        uploaded_count = 0
        for md_file in md_files:
            try:
                print(f"📤 Uploading {md_file.name}...")

                # Read file content
                with open(md_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Upload to storage
                storage_path = f"siebert/{md_file.name}"

                # Check if file already exists
                try:
                    existing = client.storage.from_("knowledge-base").download(
                        storage_path
                    )
                    print(f"⏭️ File {md_file.name} already exists, skipping...")
                    continue
                except:
                    # File doesn't exist, proceed with upload
                    pass

                # Upload file
                result = client.storage.from_("knowledge-base").upload(
                    storage_path,
                    content.encode("utf-8"),
                    file_options={"content-type": "text/markdown"},
                )

                if result:
                    uploaded_count += 1
                    print(f"✅ Uploaded {md_file.name}")
                else:
                    print(f"❌ Failed to upload {md_file.name}")

            except Exception as e:
                print(f"❌ Error uploading {md_file.name}: {e}")
                continue

        print(f"\n📤 Upload completed! Uploaded {uploaded_count} files")
        return uploaded_count > 0

    except Exception as e:
        print(f"❌ Error during upload: {e}")
        return False


def sync_to_database():
    """Sync uploaded files to database tables."""
    print("\n🔄 Syncing to database...")

    try:
        tracker = SupabaseTracker()
        client = tracker.client

        # Get Siebert client ID
        client_res = (
            client.table("clients")
            .select("id")
            .eq("name", "siebert")
            .single()
            .execute()
        )
        if not client_res.data:
            print("❌ Siebert client not found!")
            return False

        client_id = client_res.data["id"]

        # List files in storage
        files = client.storage.from_("knowledge-base").list("siebert")
        print(f"📄 Found {len(files)} files in storage")

        documents_created = 0
        for file_info in files:
            file_name = file_info["name"]
            if not file_name.endswith(".md"):
                continue

            try:
                # Download content
                file_path = f"siebert/{file_name}"
                response = client.storage.from_("knowledge-base").download(file_path)
                content = response.decode("utf-8")

                # Extract title
                title = file_name.replace(".md", "").replace("_", " ").title()
                lines = content.split("\n")
                for line in lines:
                    if line.startswith("# "):
                        title = line[2:].strip()
                        break

                # Check if already exists
                existing = (
                    client.table("documents")
                    .select("id")
                    .eq("client_id", client_id)
                    .eq("title", title)
                    .execute()
                )
                if existing.data:
                    print(f"⏭️ Document '{title}' already exists")
                    continue

                # Create document
                document_data = {
                    "client_id": client_id,
                    "title": title,
                    "content": content,
                    "description": content[:200]
                    + ("..." if len(content) > 200 else ""),
                    "category": "general",
                    "tags": [],
                    "file_path": file_path,
                    "file_size": len(content.encode("utf-8")),
                    "file_type": "markdown",
                }

                result = client.table("documents").insert(document_data).execute()
                if result.data:
                    documents_created += 1
                    print(f"✅ Created document: {title}")

            except Exception as e:
                print(f"❌ Error processing {file_name}: {e}")
                continue

        print(f"🎉 Created {documents_created} documents in database")
        return True

    except Exception as e:
        print(f"❌ Error syncing to database: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("📤 UPLOAD TO SUPABASE STORAGE & SYNC")
    print("=" * 60)

    # Step 1: Upload to storage
    upload_success = upload_documents_to_storage()

    # Step 2: Sync to database
    if upload_success:
        sync_success = sync_to_database()
    else:
        sync_success = False

    print("=" * 60)
    sys.exit(0 if (upload_success and sync_success) else 1)
