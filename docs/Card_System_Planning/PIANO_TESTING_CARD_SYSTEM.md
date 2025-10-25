# 🧪 Piano Testing - Card System V1

**Data**: 2025-10-25  
**Scope**: Testing strategy per MVP  
**Target Coverage**: >80%

---

## 🎯 TESTING STRATEGY

### Livelli di Testing
1. **Unit Tests** - Logica isolata
2. **Integration Tests** - Componenti insieme
3. **E2E Tests** - Flusso completo
4. **Performance Tests** - Velocità + scalabilità

---

## 🧪 UNIT TESTS

### Domain Layer Tests

#### `test_card_entity.py`
```python
def test_product_card_creation():
    card = ProductCard(
        id=uuid4(),
        tenant_id=uuid4(),
        title="Enterprise CRM",
        content=ProductContent(...)
    )
    assert card.card_type == CardType.PRODUCT
    assert card.version == 1

def test_card_validation():
    # Test invalid content
    with pytest.raises(ValidationError):
        ProductCard(
            id=uuid4(),
            tenant_id=uuid4(),
            title="",  # Too short
            content=ProductContent(...)
        )

def test_card_relationships():
    source = ProductCard(...)
    target = PersonaCard(...)
    rel = CardRelationship(
        source_card_id=source.id,
        target_card_id=target.id,
        relationship_type=RelationshipType.TARGETS
    )
    assert rel.strength == 1.0
```

### Application Layer Tests

#### `test_create_card_use_case.py`
```python
@pytest.mark.asyncio
async def test_create_product_card():
    use_case = CreateCardUseCase(repository=mock_repo)
    
    request = CreateCardRequest(
        card_type=CardType.PRODUCT,
        title="Enterprise CRM",
        content={...}
    )
    
    result = await use_case.execute(request, tenant_id)
    
    assert result.id is not None
    assert result.card_type == CardType.PRODUCT
    mock_repo.create.assert_called_once()

@pytest.mark.asyncio
async def test_create_cards_from_snapshot():
    use_case = CreateCardsFromSnapshotUseCase(repository=mock_repo)
    
    snapshot = CompanySnapshot(...)
    cards = await use_case.execute(snapshot, tenant_id)
    
    assert len(cards) == 4
    assert any(c.card_type == CardType.PRODUCT for c in cards)
    assert any(c.card_type == CardType.PERSONA for c in cards)
    assert any(c.card_type == CardType.CAMPAIGN for c in cards)
    assert any(c.card_type == CardType.TOPIC for c in cards)
```

### Repository Tests

#### `test_card_repository.py`
```python
@pytest.mark.asyncio
async def test_create_card():
    repo = CardRepository(db=mock_db)
    card = ProductCard(...)
    
    result = await repo.create(card)
    
    assert result.id == card.id
    mock_db.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_card_by_id():
    repo = CardRepository(db=mock_db)
    
    result = await repo.get(card_id, tenant_id)
    
    assert result.id == card_id
    assert result.tenant_id == tenant_id

@pytest.mark.asyncio
async def test_list_cards_with_filters():
    repo = CardRepository(db=mock_db)
    
    results = await repo.list(
        tenant_id=tenant_id,
        card_type=CardType.PRODUCT,
        limit=10
    )
    
    assert len(results) <= 10
    assert all(c.card_type == CardType.PRODUCT for c in results)

@pytest.mark.asyncio
async def test_update_card():
    repo = CardRepository(db=mock_db)
    
    updates = {"title": "New Title"}
    result = await repo.update(card_id, updates)
    
    assert result.title == "New Title"
    assert result.version == 2

@pytest.mark.asyncio
async def test_delete_card():
    repo = CardRepository(db=mock_db)
    
    await repo.delete(card_id)
    
    mock_db.execute.assert_called_once()
```

---

## 🔗 INTEGRATION TESTS

### API Integration Tests

#### `test_card_api.py`
```python
@pytest.mark.asyncio
async def test_create_card_endpoint(client):
    response = await client.post(
        "/api/v1/cards",
        json={
            "card_type": "product",
            "title": "Enterprise CRM",
            "content": {...}
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 201
    assert response.json()["id"] is not None

@pytest.mark.asyncio
async def test_get_card_endpoint(client):
    response = await client.get(
        f"/api/v1/cards/{card_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["id"] == card_id

@pytest.mark.asyncio
async def test_list_cards_endpoint(client):
    response = await client.get(
        "/api/v1/cards?card_type=product&limit=10",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert "items" in response.json()
    assert "total" in response.json()

@pytest.mark.asyncio
async def test_update_card_endpoint(client):
    response = await client.patch(
        f"/api/v1/cards/{card_id}",
        json={"title": "New Title"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"

@pytest.mark.asyncio
async def test_link_cards_endpoint(client):
    response = await client.post(
        f"/api/v1/cards/{source_id}/relationships",
        json={
            "target_card_id": target_id,
            "relationship_type": "targets"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 201
```

### Onboarding Integration Tests

#### `test_onboarding_card_integration.py`
```python
@pytest.mark.asyncio
async def test_onboarding_creates_cards():
    # Setup
    session = OnboardingSession(...)
    session.company_snapshot = CompanySnapshot(...)
    
    # Execute
    result = await execute_onboarding(session)
    
    # Verify
    assert len(result.card_ids) == 4
    
    # Verify cards in database
    cards = await card_repo.list(tenant_id=session.tenant_id)
    assert len(cards) == 4
    assert any(c.card_type == CardType.PRODUCT for c in cards)
```

### CGS Integration Tests

#### `test_cgs_card_integration.py`
```python
@pytest.mark.asyncio
async def test_cgs_reads_cards_as_rag():
    # Setup
    cards = await create_test_cards(tenant_id)
    
    # Execute
    context = await get_cards_for_context(tenant_id)
    
    # Verify
    assert len(context) == 4
    assert context[0].card_type == CardType.PRODUCT
    
    # Execute workflow
    result = await cgs_workflow.execute(context)
    
    # Verify content generated
    assert result.content is not None
```

---

## 🌐 E2E TESTS

### Frontend E2E Tests

#### `test_card_editor_e2e.py`
```typescript
describe('Card Editor E2E', () => {
  it('should create a product card', async () => {
    // Navigate to card creation
    await page.goto('http://localhost:3001/cards/create');
    
    // Fill form
    await page.fill('[name="title"]', 'Enterprise CRM');
    await page.fill('[name="value_proposition"]', 'Best CRM solution');
    await page.fill('[name="features"]', 'Feature 1, Feature 2');
    
    // Submit
    await page.click('button[type="submit"]');
    
    // Verify
    await page.waitForNavigation();
    expect(page.url()).toContain('/cards/');
  });

  it('should link two cards', async () => {
    // Navigate to card
    await page.goto(`http://localhost:3001/cards/${productCardId}`);
    
    // Click link button
    await page.click('button[aria-label="Link card"]');
    
    // Select target card
    await page.click(`[data-card-id="${personaCardId}"]`);
    
    // Select relationship type
    await page.selectOption('[name="relationship_type"]', 'targets');
    
    // Submit
    await page.click('button[type="submit"]');
    
    // Verify
    expect(await page.textContent('.relationships')).toContain('targets');
  });
});
```

### Complete Flow E2E Test

#### `test_complete_flow_e2e.py`
```python
@pytest.mark.asyncio
async def test_complete_onboarding_to_cgs_flow():
    # 1. User starts onboarding
    session = await start_onboarding_session(user_id)
    
    # 2. User inputs company data
    await input_company_data(session, {
        "name": "Acme Corp",
        "description": "Leading SaaS provider"
    })
    
    # 3. Onboarding creates snapshot
    snapshot = await create_snapshot(session)
    assert snapshot is not None
    
    # 4. Card Service creates 4 cards
    cards = await create_cards_from_snapshot(snapshot)
    assert len(cards) == 4
    
    # 5. Verify cards in database
    db_cards = await card_repo.list(tenant_id=session.tenant_id)
    assert len(db_cards) == 4
    
    # 6. CGS reads cards as RAG
    context = await get_cards_for_context(session.tenant_id)
    assert len(context) == 4
    
    # 7. CGS generates content
    result = await cgs_workflow.execute(context)
    assert result.content is not None
    
    # 8. Frontend displays results
    response = await client.get(f"/api/v1/sessions/{session.id}")
    assert response.status_code == 200
    assert response.json()["card_ids"] == [c.id for c in cards]
```

---

## ⚡ PERFORMANCE TESTS

### Query Performance

#### `test_card_performance.py`
```python
@pytest.mark.asyncio
async def test_list_cards_performance():
    # Create 1000 cards
    for i in range(1000):
        await card_repo.create(ProductCard(...))
    
    # Measure query time
    start = time.time()
    cards = await card_repo.list(tenant_id, limit=100)
    duration = time.time() - start
    
    # Assert <500ms
    assert duration < 0.5
    assert len(cards) == 100

@pytest.mark.asyncio
async def test_get_card_with_relationships_performance():
    # Create card with 50 relationships
    card = await card_repo.create(ProductCard(...))
    for i in range(50):
        await relationship_repo.create(CardRelationship(...))
    
    # Measure query time
    start = time.time()
    result = await card_repo.get_with_relationships(card.id)
    duration = time.time() - start
    
    # Assert <200ms
    assert duration < 0.2
    assert len(result.relationships) == 50
```

---

## 📊 COVERAGE TARGETS

| Component | Target | Priority |
|-----------|--------|----------|
| Domain | 95% | P0 |
| Application | 90% | P0 |
| Infrastructure | 85% | P1 |
| API | 80% | P1 |
| Frontend | 75% | P2 |

---

## ✅ TEST CHECKLIST

### Week 1
- [ ] Unit tests per domain layer
- [ ] Unit tests per application layer
- [ ] Unit tests per repository

### Week 2
- [ ] Integration tests per API
- [ ] Integration tests per Onboarding
- [ ] Integration tests per CGS

### Week 3
- [ ] E2E tests per frontend
- [ ] E2E tests per complete flow
- [ ] Performance tests
- [ ] Coverage report >80%

---

## 🚀 CI/CD INTEGRATION

### GitHub Actions
```yaml
name: Card System Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: pytest --cov=core/card_service --cov-report=xml
      - uses: codecov/codecov-action@v2
```


