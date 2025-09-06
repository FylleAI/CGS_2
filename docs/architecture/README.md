# CGSRef Architecture Guide

## Overview

CGSRef implements Clean Architecture principles with Domain-Driven Design (DDD) to create a maintainable, scalable, and testable content generation system.

## Architecture Layers

### 1. Domain Layer (`core/domain/`)

The innermost layer containing pure business logic, independent of any external frameworks or technologies.

#### Entities
- **Agent**: AI agents with specific roles and capabilities
- **Workflow**: Orchestrated sequences of tasks
- **Task**: Individual units of work
- **Content**: Generated content with metadata

#### Value Objects
- **ProviderConfig**: Immutable LLM provider configuration
- **ClientProfile**: Client-specific branding and preferences
- **GenerationParams**: Content generation parameters

#### Repository Interfaces
- Abstract contracts for data access
- No implementation details, only business contracts

### 2. Application Layer (`core/application/`)

Contains application-specific business rules and orchestrates domain entities.

#### Use Cases
- **GenerateContentUseCase**: Main content generation orchestration
- **ManageWorkflowsUseCase**: Workflow management operations
- **ConfigureAgentsUseCase**: Agent configuration management

#### DTOs (Data Transfer Objects)
- **ContentGenerationRequest/Response**: API communication objects
- **WorkflowConfigRequest/Response**: Workflow configuration objects

#### Interfaces
- **LLMProviderInterface**: Contract for AI providers
- **RAGInterface**: Contract for knowledge retrieval
- **NotificationInterface**: Contract for notifications

### 3. Infrastructure Layer (`core/infrastructure/`)

Contains implementations of external services and data persistence.

#### Repository Implementations
- **FileContentRepository**: File-based content storage
- **YamlAgentRepository**: YAML-based agent configuration
- **FileWorkflowRepository**: File-based workflow storage

#### External Service Adapters
- **OpenAIAdapter**: OpenAI API integration
- **AnthropicAdapter**: Anthropic API integration
- **DeepSeekAdapter**: DeepSeek API integration

#### Configuration
- **Settings**: Environment-based configuration management
- **ProviderSettings**: AI provider configurations

#### Research Tools
- **Serper** (`web_search`, `web_search_financial`): basic web search for quick, general lookups.
- **PerplexityResearchTool** (`perplexity_search`): minimal wrapper over the Perplexity API, returning raw results.
- **Research Agent** (`research_agent`): autonomous planner that orchestrates complex Perplexity searches and supplies citation-rich findings. Compliance agents call this agent to validate claims.

### 4. Interface Layer (`api/`)

External interfaces for system interaction.

#### REST API (`api/rest/`)
- FastAPI-based HTTP endpoints
- OpenAPI documentation
- CORS and middleware support

#### CLI (`api/cli/`)
- Typer-based command line interface
- Rich console output
- Interactive content generation

#### WebSocket (`api/websocket/`)
- Real-time communication
- Progress updates
- Live content streaming

## Design Principles

### 1. Dependency Inversion
- High-level modules don't depend on low-level modules
- Both depend on abstractions (interfaces)
- Abstractions don't depend on details

### 2. Single Responsibility
- Each class has one reason to change
- Clear separation of concerns
- Focused, cohesive modules

### 3. Open/Closed Principle
- Open for extension, closed for modification
- New providers can be added without changing existing code
- Plugin-based architecture for workflows and tools

### 4. Interface Segregation
- Small, focused interfaces
- Clients depend only on methods they use
- No fat interfaces

### 5. Liskov Substitution
- Derived classes must be substitutable for base classes
- Consistent behavior across implementations
- Proper inheritance hierarchies

## Data Flow

```
1. Request → API Layer (REST/CLI)
2. API Layer → Application Layer (Use Cases)
3. Use Cases → Domain Services
4. Domain Services → Repository Interfaces
5. Repository Interfaces → Infrastructure Implementations
6. Infrastructure → External Services (AI Providers, Storage)
```

## Key Benefits

### 1. Testability
- Pure domain logic can be tested in isolation
- Mock implementations for external dependencies
- Fast unit tests without external services

### 2. Maintainability
- Clear separation of concerns
- Changes in one layer don't affect others
- Easy to understand and modify

### 3. Scalability
- New providers can be added easily
- Horizontal scaling through stateless design
- Microservice-ready architecture

### 4. Flexibility
- Multiple interfaces (REST, CLI, WebSocket)
- Pluggable storage backends
- Configurable AI providers

## Extension Points

### Adding New AI Providers
1. Implement `LLMProviderInterface`
2. Add provider configuration
3. Register in dependency injection
4. Update settings and validation

### Adding New Content Types
1. Extend `ContentType` enum
2. Add type-specific validation
3. Update generation parameters
4. Add format converters if needed

### Adding New Workflows
1. Create workflow definition
2. Define required agents and tasks
3. Implement workflow logic
4. Add to workflow factory

### Adding New Storage Backends
1. Implement repository interfaces
2. Add configuration options
3. Update dependency injection
4. Add migration tools if needed

## Security Considerations

### 1. API Security
- JWT-based authentication
- Rate limiting
- Input validation
- CORS configuration

### 2. Data Protection
- Secure API key storage
- Encrypted sensitive data
- Audit logging
- Access controls

### 3. Content Security
- Input sanitization
- Output validation
- Content filtering
- Privacy compliance

## Performance Optimization

### 1. Caching
- LLM response caching
- Configuration caching
- Content metadata caching

### 2. Async Processing
- Non-blocking I/O operations
- Background task processing
- Streaming responses

### 3. Resource Management
- Connection pooling
- Memory optimization
- Graceful degradation

## Monitoring and Observability

### 1. Logging
- Structured logging
- Log levels and filtering
- Centralized log aggregation

### 2. Metrics
- Performance metrics
- Business metrics
- System health metrics

### 3. Tracing
- Request tracing
- Dependency tracking
- Error tracking

## Deployment Strategies

### 1. Development
- Local development with hot reload
- Docker Compose for dependencies
- Environment-based configuration

### 2. Production
- Container-based deployment
- Load balancing
- Health checks
- Rolling updates

### 3. Scaling
- Horizontal pod autoscaling
- Database read replicas
- CDN for static content
- Microservice decomposition
