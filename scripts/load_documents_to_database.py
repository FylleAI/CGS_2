#!/usr/bin/env python3
"""
Load Knowledge Base documents directly from filesystem to Supabase Database

This script reads documents from the local knowledge_base directory
and inserts them directly into the documents table.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.infrastructure.database.supabase_tracker import SupabaseTracker
from core.infrastructure.config.settings import get_settings

def load_documents_to_database():
    """Load documents from filesystem directly to database."""
    print("📚 Loading documents to Supabase Database...")
    
    try:
        settings = get_settings()
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
        
        # Get local knowledge base directory
        kb_dir = Path(settings.knowledge_base_dir) / "siebert"
        if not kb_dir.exists():
            print(f"❌ Knowledge base directory not found: {kb_dir}")
            return False
        
        print(f"📁 Reading from: {kb_dir}")
        
        # Get all markdown files
        md_files = list(kb_dir.glob("*.md"))
        print(f"📄 Found {len(md_files)} markdown files")
        
        documents_created = 0
        for md_file in md_files:
            try:
                print(f"📖 Processing {md_file.name}...")
                
                # Read file content
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract title from content or filename
                title = md_file.name.replace('.md', '').replace('_', ' ').title()
                lines = content.split('\n')
                for line in lines:
                    if line.startswith('# '):
                        title = line[2:].strip()
                        break
                
                # Create description (first 300 chars)
                description = content[:300] + ("..." if len(content) > 300 else "")
                
                # Determine category and tags based on filename
                category = "general"
                tags = []
                
                filename_lower = md_file.name.lower()
                if any(term in filename_lower for term in ["company", "profile", "brand"]):
                    category = "company"
                    tags.extend(["company", "profile", "brand"])
                elif any(term in filename_lower for term in ["guideline", "guide", "production"]):
                    category = "guidelines"
                    tags.extend(["guidelines", "production"])
                elif any(term in filename_lower for term in ["content", "quality"]):
                    category = "content"
                    tags.extend(["content", "quality"])
                elif any(term in filename_lower for term in ["voice", "examples", "cultural"]):
                    category = "voice"
                    tags.extend(["voice", "examples", "cultural"])
                
                # Check if document already exists
                existing = client.table("documents").select("id").eq("client_id", client_id).eq("title", title).execute()
                if existing.data:
                    print(f"⏭️ Document '{title}' already exists, skipping...")
                    continue
                
                # Create document data
                document_data = {
                    "client_id": client_id,
                    "title": title,
                    "content": content,
                    "description": description,
                    "category": category,
                    "tags": tags,
                    "file_path": f"filesystem/{md_file.name}",
                    "file_size": len(content.encode('utf-8')),
                    "file_type": "markdown",
                    "metadata": {
                        "source": "filesystem",
                        "original_filename": md_file.name,
                        "loaded_at": "2025-09-03T20:55:00Z"
                    }
                }
                
                # Insert document
                result = client.table("documents").insert(document_data).execute()
                if result.data:
                    documents_created += 1
                    print(f"✅ Created document: {title}")
                    print(f"   Category: {category}")
                    print(f"   Tags: {tags}")
                    print(f"   Size: {len(content)} characters")
                else:
                    print(f"❌ Failed to create document: {title}")
                    
            except Exception as e:
                print(f"❌ Error processing {md_file.name}: {e}")
                continue
        
        print(f"\n🎉 Loading completed! Created {documents_created} documents")
        return documents_created > 0
        
    except Exception as e:
        print(f"❌ Error during loading: {e}")
        return False

def verify_documents():
    """Verify that documents were loaded correctly."""
    print("\n🧪 Verifying loaded documents...")
    
    try:
        tracker = SupabaseTracker()
        client = tracker.client
        
        # Get all documents
        docs_result = client.table("documents").select("*").execute()
        documents = docs_result.data or []
        
        print(f"📊 Total documents in database: {len(documents)}")
        
        if documents:
            print("\n📋 Documents summary:")
            categories = {}
            total_size = 0
            
            for doc in documents:
                category = doc.get("category", "unknown")
                categories[category] = categories.get(category, 0) + 1
                total_size += doc.get("file_size", 0)
                
                print(f"  📄 {doc['title']}")
                print(f"     Category: {doc['category']} | Tags: {doc.get('tags', [])}")
                print(f"     Size: {doc.get('file_size', 0)} bytes | Content: {len(doc['content'])} chars")
                print()
            
            print(f"📈 Summary by category:")
            for category, count in categories.items():
                print(f"  - {category}: {count} documents")
            
            print(f"📏 Total content size: {total_size} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("📚 LOAD DOCUMENTS TO SUPABASE DATABASE")
    print("=" * 60)
    
    success = load_documents_to_database()
    if success:
        verify_documents()
    
    print("=" * 60)
    sys.exit(0 if success else 1)
