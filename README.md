# CGSRef - Clean Content Generation System

A refactored, clean architecture implementation of the Content Generation System following Domain-Driven Design principles.

## ✨ **Key Features**

### 🤖 **Multi-Agent Workflows**
- **Enhanced Article**: Research-driven content with RAG integration
- **Premium Newsletter**: Advanced newsletter generation with source analysis
- **Extensible Framework**: Easy addition of new workflow types

### 💰 **Real-Time Analytics**
- **Cost Tracking**: Accurate LLM cost calculation from API responses
- **Performance Metrics**: Token usage, duration, success rates
- **Agent Analytics**: Individual agent performance tracking
- **Workflow Insights**: Complete execution analytics

### 🏗️ **Clean Architecture**
- **Domain-Driven Design**: Pure business logic separation
- **Dependency Inversion**: Framework-agnostic core
- **Extensible Design**: Easy provider and workflow addition
- **Test-Driven**: Comprehensive testing suite

### 🌐 **Modern Frontend**
- **React Interface**: Modern, responsive UI
- **Real-Time Updates**: Live workflow metrics
- **Knowledge Base Integration**: Document management
- **Multi-Provider Support**: OpenAI, Anthropic, DeepSeek

## Architecture Overview

This project implements Clean Architecture with clear separation of concerns:

```
📁 core/                    # Business Logic (Domain + Application + Infrastructure)
├── 📁 domain/             # Pure business logic, framework-agnostic
├── 📁 application/        # Use cases and application services
└── 📁 infrastructure/     # External services and data persistence

📁 api/                    # Interface Adapters
├── 📁 rest/              # REST API endpoints
├── 📁 cli/               # Command line interface
└── 📁 websocket/         # Real-time communication

📁 web/                    # User Interfaces
├── 📁 react-app/         # Modern React frontend
└── 📁 streamlit-legacy/  # Legacy Streamlit interface

📁 data/                   # Data storage
📁 tests/                  # Testing suite
📁 scripts/               # Utility scripts
📁 docs/                  # Documentation
```

## Key Principles

1. **Dependency Inversion**: Core business logic depends only on abstractions
2. **Single Responsibility**: Each module has one clear purpose
3. **Open/Closed**: Extensible without modifying existing code
4. **Interface Segregation**: Small, focused interfaces
5. **Clean Separation**: UI, business logic, and data access are completely separated

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+ (for React frontend)
- Docker (optional, for containerized deployment)

### Installation
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd web/react-app && npm install
```

### Running the System
```bash
# Start API server
python -m api.rest.main

# Start React frontend
cd web/react-app && npm start

# Use CLI interface
python -m api.cli.main generate --topic "AI in Finance" --workflow siebert
```

## Development

### Adding New Features
1. Start with domain entities and business rules
2. Create use cases in the application layer
3. Implement infrastructure adapters
4. Add API endpoints
5. Update frontend components

### Testing
```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
```

## Documentation

### 📚 **Core Documentation**
- [Architecture Guide](docs/architecture/README.md) - Clean Architecture implementation
- [Enhanced Logging System](ENHANCED_LOGGING_SYSTEM.md) - Real-time analytics and cost tracking
- [Workflow Implementation Index](WORKFLOW_IMPLEMENTATION_INDEX.md) - Complete workflow guide

### 🚀 **Development Guides**
- [New Workflow Checklist](NUOVO_WORKFLOW_CHECKLIST.md) - Step-by-step workflow creation
- [Premium Newsletter Guide](PREMIUM_NEWSLETTER_IMPLEMENTATION_GUIDE.md) - Advanced workflow example
- [Frontend Integration Guide](frontend_integration_guide.md) - React frontend integration

### 🔧 **Setup & Configuration**
- [Supabase Setup Guide](supabase_setup_guide.md) - Database configuration
- [Migration Guide](MIGRATION_GUIDE.md) - Legacy system migration
- [Error Recovery Guide](ERROR_RECOVERY_GUIDE.md) - Troubleshooting

### 📊 **System Status**
- [System Status Report](SYSTEM_STATUS_REPORT.md) - Current implementation status
- [Debugging Checkpoint](DEBUGGING_CHECKPOINT.md) - Latest debugging session
- [Quick Reference](QUICK_REFERENCE.md) - Commands and shortcuts

## Migration from Legacy System

This system is designed to gradually replace the existing FylleCGS implementation while maintaining compatibility. The legacy system serves as reference during development.
