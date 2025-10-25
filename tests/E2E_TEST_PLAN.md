# Card Service V1 - End-to-End Test Plan

Complete end-to-end testing guide for the Card Service integration.

## Test Scenarios

### Scenario 1: Complete Onboarding → Card Creation → CGS Flow

**Objective**: Verify complete user flow from onboarding to content generation with cards.

**Steps**:
1. User completes onboarding
   - Fill company info
   - Fill audience info
   - Set goal
   - Submit

2. System creates cards automatically
   - 4 cards created (Product, Persona, Campaign, Topic)
   - Cards linked with relationships
   - Card IDs stored in session

3. Email sent with card link
   - Email contains link to card-frontend
   - Link includes tenant_id parameter

4. User opens card-frontend
   - Dashboard loads
   - 4 cards displayed
   - Card details visible

5. User goes to CGS
   - Requests content generation
   - CGS retrieves cards
   - Content generated with card context

**Expected Results**:
- ✅ All 4 cards created
- ✅ Cards visible in dashboard
- ✅ Content generated with card information
- ✅ No errors in logs

**Test Data**:
```
Company: "Tech Startup"
Audience: "Software Developers"
Goal: "Content Marketing"
```

---

### Scenario 2: Card Visualization and Interaction

**Objective**: Verify card-frontend UI functionality.

**Steps**:
1. Open card-frontend dashboard
2. View all cards in grid
3. Click on card to view details
4. Check card relationships
5. Edit card (if implemented)
6. Delete card (if implemented)

**Expected Results**:
- ✅ Dashboard loads without errors
- ✅ All 4 cards displayed
- ✅ Card details show correct information
- ✅ Relationships visible
- ✅ Edit/delete operations work

---

### Scenario 3: Card Context in Content Generation

**Objective**: Verify cards are used as RAG context in content generation.

**Steps**:
1. Create cards via onboarding
2. Request content generation in CGS
3. Provide topic related to card content
4. Generate content
5. Verify content uses card information

**Expected Results**:
- ✅ Content references card information
- ✅ Product details in content
- ✅ Persona insights in content
- ✅ Campaign objectives in content
- ✅ Topic coverage in content

**Example**:
- Card: Product = "AI Analytics Platform"
- Card: Persona = "Data Scientists"
- Generated Content: "AI Analytics Platform for Data Scientists..."

---

### Scenario 4: Error Handling

**Objective**: Verify system handles errors gracefully.

**Steps**:
1. Test with invalid tenant_id
2. Test with no cards
3. Test with card service unavailable
4. Test with database errors
5. Test with invalid requests

**Expected Results**:
- ✅ Graceful error messages
- ✅ No system crashes
- ✅ Fallback behavior works
- ✅ Logs contain error details

---

### Scenario 5: Multi-tenant Isolation

**Objective**: Verify tenant isolation works correctly.

**Steps**:
1. Create cards for tenant A
2. Create cards for tenant B
3. Verify tenant A only sees their cards
4. Verify tenant B only sees their cards
5. Verify no data leakage

**Expected Results**:
- ✅ Tenant A sees only their cards
- ✅ Tenant B sees only their cards
- ✅ No cross-tenant data access
- ✅ RLS policies enforced

---

## Manual Testing Checklist

### Backend Testing

- [ ] Card Service API endpoints respond correctly
- [ ] Onboarding creates cards automatically
- [ ] Cards stored in database
- [ ] RLS policies enforce tenant isolation
- [ ] Card relationships created correctly
- [ ] CGS retrieves cards for context
- [ ] Card context formatted correctly
- [ ] Error handling works
- [ ] Logging is comprehensive

### Frontend Testing

- [ ] Card-frontend loads without errors
- [ ] Dashboard displays all cards
- [ ] Card details page works
- [ ] Responsive design on mobile
- [ ] Error messages display correctly
- [ ] Loading states show
- [ ] Toast notifications work
- [ ] Navigation works
- [ ] Tenant ID parameter handled

### Integration Testing

- [ ] Onboarding → Cards flow works
- [ ] Cards → CGS flow works
- [ ] Email link opens card-frontend
- [ ] Content generation uses cards
- [ ] Multi-tenant isolation works
- [ ] Error scenarios handled

---

## Performance Testing

### Load Testing

**Objective**: Verify system handles multiple concurrent users.

**Test Cases**:
1. 10 concurrent users creating cards
2. 50 concurrent users viewing cards
3. 100 concurrent content generation requests

**Expected Results**:
- ✅ Response time < 2 seconds
- ✅ No database connection errors
- ✅ No memory leaks
- ✅ Graceful degradation

### Stress Testing

**Objective**: Verify system behavior under extreme load.

**Test Cases**:
1. 1000 cards per tenant
2. 10000 relationships
3. Large card content (> 10MB)

**Expected Results**:
- ✅ System remains responsive
- ✅ No data corruption
- ✅ Graceful error handling

---

## Security Testing

### Authorization Testing

- [ ] Verify RLS policies work
- [ ] Verify tenant isolation
- [ ] Verify API key validation
- [ ] Verify CORS headers

### Input Validation

- [ ] Test with invalid card types
- [ ] Test with malicious content
- [ ] Test with oversized payloads
- [ ] Test with special characters

---

## Browser Compatibility

### Desktop Browsers
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

### Mobile Browsers
- [ ] Chrome Mobile
- [ ] Safari iOS
- [ ] Firefox Mobile

---

## Accessibility Testing

- [ ] Keyboard navigation works
- [ ] Screen reader compatible
- [ ] Color contrast sufficient
- [ ] Font sizes readable

---

## Test Execution

### Local Testing
```bash
# Run all tests
./run_tests.sh all

# Run with coverage
./run_tests.sh all coverage

# Run specific test
pytest tests/integration/test_onboarding_card_creation.py -v
```

### CI/CD Testing
- Tests run automatically on PR
- Tests run on merge to main
- Coverage reports generated
- Failed tests block merge

---

## Test Results Template

```
Test Date: YYYY-MM-DD
Tester: [Name]
Environment: [Dev/Staging/Prod]

Scenario 1: ✅ PASSED
Scenario 2: ✅ PASSED
Scenario 3: ✅ PASSED
Scenario 4: ✅ PASSED
Scenario 5: ✅ PASSED

Issues Found: None
Performance: Good
Security: Good
Accessibility: Good

Sign-off: [Signature]
```

---

## Regression Testing

After each release, verify:
- [ ] All previous tests still pass
- [ ] No new bugs introduced
- [ ] Performance maintained
- [ ] Security maintained

---

## Known Issues

None currently.

---

## Future Enhancements

- [ ] Automated E2E tests with Cypress/Playwright
- [ ] Performance monitoring
- [ ] Security scanning
- [ ] Accessibility scanning

