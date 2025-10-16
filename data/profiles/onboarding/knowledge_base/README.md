# Onboarding Profile - Knowledge Base

This directory contains the knowledge base for the generic **onboarding** client profile.

## Purpose

The onboarding profile is a generic, neutral client profile used by the onboarding flow to generate content for new brands without requiring a dedicated client profile.

## Structure

```
knowledge_base/
├── README.md           ← This file
├── brand_guidelines/   ← (Optional) Generic brand guidelines
├── templates/          ← (Optional) Content templates
└── examples/           ← (Optional) Example content
```

## Usage

When the onboarding flow creates content, the RAG specialist agent can retrieve documents from this knowledge base to enhance content creation.

### Adding Documents

To add documents to this knowledge base:

1. Place markdown files in this directory or subdirectories
2. Documents will be automatically indexed by the RAG system
3. Use clear, descriptive filenames (e.g., `content_writing_guidelines.md`)

### Document Format

Documents should be in markdown format with clear structure:

```markdown
# Document Title

## Section 1

Content here...

## Section 2

More content...
```

## Notes

- This knowledge base is intentionally minimal for the generic onboarding profile
- For specific clients (e.g., Siebert, Reopla), create dedicated profiles with comprehensive knowledge bases
- Documents here should be generic and applicable to any brand/industry

