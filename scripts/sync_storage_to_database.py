#!/usr/bin/env python3
"""
Sync Knowledge Base from Supabase Storage to Database Tables

This script reads documents from the existing Supabase Storage bucket
and populates the documents table we just created.
"""

import sys
from pathlib import Path
import json
from datetime import datetime

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.infrastructure.database.supabase_tracker import SupabaseTracker

def sync_storage_to_database():
    """Sync documents from Storage bucket to database tables."""
    print("🔄 Syncing Knowledge Base from Storage to Database...")
    
    try:
        tracker = SupabaseTracker()
        client = tracker.client
        
        # Get Siebert client ID
        print("👤 Getting Siebert client...")
        client_res = client.table("clients").select("id").eq("name", "siebert").single().execute()
        if not client_res.data:
            print("❌ Siebert client not found!")
            return False
            
        client_id = client_res.data["id"]
        print(f"✅ Found Siebert client: {client_id}")
        
        # List files in the knowledge-base bucket
        print("📁 Listing files in knowledge-base bucket...")
        try:
            files = client.storage.from_("knowledge-base").list("siebert")
            print(f"📄 Found {len(files)} files in bucket")
            
            for file_info in files:
                print(f"  - {file_info['name']} ({file_info.get('metadata', {}).get('size', 'unknown')} bytes)")
        except Exception as e:
            print(f"❌ Error listing bucket files: {e}")
            return False
        
        # Process each file
        documents_created = 0
        for file_info in files:
            file_name = file_info["name"]
            if not file_name.endswith('.md'):
                print(f"⏭️ Skipping non-markdown file: {file_name}")
                continue
                
            try:
                print(f"📖 Processing {file_name}...")
                
                # Download file content
                file_path = f"siebert/{file_name}"
                response = client.storage.from_("knowledge-base").download(file_path)
                content = response.decode('utf-8')
                
                # Extract title from content or filename
                title = file_name.replace('.md', '').replace('_', ' ').title()
                lines = content.split('\n')
                for line in lines:
                    if line.startswith('# '):
                        title = line[2:].strip()
                        break
                
                # Create description (first 200 chars)
                description = content[:200] + ("..." if len(content) > 200 else "")
                
                # Determine category and tags
                category = "general"
                tags = []
                
                filename_lower = file_name.lower()
                if any(term in filename_lower for term in ["company", "profile", "about"]):
                    category = "company"
                    tags.extend(["company", "profile"])
                elif any(term in filename_lower for term in ["guideline", "guide", "style"]):
                    category = "guidelines"
                    tags.extend(["guidelines", "style"])
                elif any(term in filename_lower for term in ["content", "template"]):
                    category = "content"
                    tags.append("content")
                
                # Check if document already exists
                existing = client.table("documents").select("id").eq("client_id", client_id).eq("title", title).execute()
                if existing.data:
                    print(f"⏭️ Document '{title}' already exists, skipping...")
                    continue
                
                # Insert document
                document_data = {
                    "client_id": client_id,
                    "title": title,
                    "content": content,
                    "description": description,
                    "category": category,
                    "tags": tags,
                    "file_path": file_path,
                    "file_size": len(content.encode('utf-8')),
                    "file_type": "markdown",
                    "metadata": {
                        "source": "supabase_storage",
                        "bucket": "knowledge-base",
                        "original_filename": file_name
                    }
                }
                
                result = client.table("documents").insert(document_data).execute()
                if result.data:
                    documents_created += 1
                    print(f"✅ Created document: {title}")
                else:
                    print(f"❌ Failed to create document: {title}")
                    
            except Exception as e:
                print(f"❌ Error processing {file_name}: {e}")
                continue
        
        print(f"\n🎉 Sync completed! Created {documents_created} documents")
        return True
        
    except Exception as e:
        print(f"❌ Error during sync: {e}")
        return False

def verify_sync():
    """Verify that the sync worked correctly."""
    print("\n🧪 Verifying sync results...")
    
    try:
        tracker = SupabaseTracker()
        client = tracker.client
        
        # Count documents
        docs_result = client.table("documents").select("*").execute()
        documents = docs_result.data or []
        
        print(f"📊 Total documents in database: {len(documents)}")
        
        if documents:
            print("\n📋 Documents summary:")
            categories = {}
            for doc in documents:
                category = doc.get("category", "unknown")
                categories[category] = categories.get(category, 0) + 1
                print(f"  - {doc['title']} ({doc['category']}) - {len(doc['content'])} chars")
            
            print(f"\n📈 By category:")
            for category, count in categories.items():
                print(f"  - {category}: {count} documents")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔄 SUPABASE STORAGE TO DATABASE SYNC")
    print("=" * 60)
    
    success = sync_storage_to_database()
    if success:
        verify_sync()
    
    print("=" * 60)
    sys.exit(0 if success else 1)
