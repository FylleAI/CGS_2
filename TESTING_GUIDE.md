# Card Service V1 - Complete Testing Guide

## 🚀 Quick Start

### Option 1: Automated Startup (Recommended)

**Linux/Mac:**
```bash
chmod +x START_ALL.sh
./START_ALL.sh
```

**Windows:**
```bash
START_ALL.bat
```

This will:
- ✅ Check prerequisites (Python, Node.js, npm)
- ✅ Create virtual environment
- ✅ Install dependencies
- ✅ Start Backend (FastAPI) on port 8000
- ✅ Start Card Frontend (React) on port 3001
- ✅ Wait for services to be ready
- ✅ Display URLs and instructions

### Option 2: Manual Startup

**Terminal 1 - Backend:**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt

# Start backend
uvicorn api.rest.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Card Frontend:**
```bash
cd card-frontend
npm install
npm run dev
```

---

## 📋 Complete End-to-End Testing Flow

### Step 1: Verify Backend is Running

Open browser and go to:
```
http://localhost:8000/docs
```

You should see:
- ✅ Swagger UI with all API endpoints
- ✅ Card Service endpoints under `/api/v1/cards/*`
- ✅ Integration endpoints under `/api/v1/cards/onboarding/*`

**Test Backend Health:**
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "ok"}
```

---

### Step 2: Complete Onboarding

1. Open **Onboarding Frontend** (usually on port 3000):
   ```
   http://localhost:3000
   ```

2. Fill in the form:
   - **Company Name**: "Tech Startup"
   - **Company Description**: "An AI-powered analytics platform"
   - **Target Audience**: "Data Scientists and ML Engineers"
   - **Marketing Goal**: "Increase brand awareness"
   - **Content Topics**: "AI, Machine Learning, Data Science"

3. Click **Submit**

4. Wait for onboarding to complete (you should see a success message)

**What happens behind the scenes:**
- ✅ CompanySnapshot created
- ✅ CGS workflow executed
- ✅ 4 cards created automatically (Product, Persona, Campaign, Topic)
- ✅ Cards stored in Supabase
- ✅ Email sent with card link (check logs)

---

### Step 3: Verify Cards Were Created

**Check Backend Logs:**
```bash
# In the backend terminal, look for:
# "Step 3: Creating atomic cards from snapshot..."
# "✨ Added 4 cards to session metadata"
```

**Check Database (Supabase):**
1. Go to Supabase dashboard
2. Navigate to `context_cards` table
3. Verify 4 cards exist with:
   - `card_type`: product, persona, campaign, topic
   - `tenant_id`: your email
   - `is_active`: true

---

### Step 4: Open Card Frontend

1. Open **Card Frontend**:
   ```
   http://localhost:3001?tenant_id=your-email@example.com
   ```

   Or if you completed onboarding, click the email link

2. You should see:
   - ✅ Dashboard with 4 tabs (Product, Persona, Campaign, Topic)
   - ✅ Cards displayed in grid
   - ✅ Card count showing 4 total

**Test Card Interactions:**
- Click on a card to view details
- Check card content is correct
- Try delete button (if implemented)

---

### Step 5: Verify Card Context in CGS

1. Go to **CGS** (Content Generation System)

2. Request content generation with topic related to your cards:
   - Example: "How to use AI for data analysis"

3. Generate content

4. **Verify content uses card context:**
   - Content should mention your company name
   - Content should reference your target audience
   - Content should align with your marketing goal
   - Content should cover your topics

**Check Backend Logs:**
```bash
# Look for:
# "✨ Added card context (XXXX chars) for tenant..."
# This confirms cards were retrieved and used
```

---

## 🧪 Automated Testing

### Run All Tests

```bash
# Using pytest
pytest tests/ -v

# Using helper script
./run_tests.sh all          # Linux/Mac
run_tests.bat all           # Windows
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/unit -v
./run_tests.sh unit

# Integration tests only
pytest tests/integration -v
./run_tests.sh integration

# With coverage report
pytest --cov=core --cov=onboarding --cov-report=html
./run_tests.sh all coverage
```

### Run Specific Test

```bash
pytest tests/unit/test_card_service_adapter.py::test_create_cards_from_snapshot_success -v
```

### Frontend Tests

```bash
cd card-frontend
npm test                    # Run all tests
npm test -- --coverage      # With coverage
npm test -- --watch         # Watch mode
```

---

## 📊 Monitoring and Debugging

### View Logs

**Backend Logs:**
```bash
# In backend terminal (Ctrl+C to stop)
# Or check /tmp/backend.log

tail -f /tmp/backend.log
```

**Card Frontend Logs:**
```bash
# In card-frontend terminal (Ctrl+C to stop)
# Or check /tmp/card-frontend.log

tail -f /tmp/card-frontend.log
```

### API Testing with curl

**List all cards:**
```bash
curl -X GET "http://localhost:8000/api/v1/cards?tenant_id=your-email@example.com" \
  -H "Content-Type: application/json"
```

**Get card by ID:**
```bash
curl -X GET "http://localhost:8000/api/v1/cards/{card_id}" \
  -H "Content-Type: application/json"
```

**Get RAG context:**
```bash
curl -X GET "http://localhost:8000/api/v1/cards/context/rag-text?tenant_id=your-email@example.com" \
  -H "Content-Type: application/json"
```

### Database Inspection

**Supabase SQL Editor:**
```sql
-- View all cards for a tenant
SELECT * FROM context_cards 
WHERE tenant_id = 'your-email@example.com' 
ORDER BY created_at DESC;

-- View card relationships
SELECT * FROM card_relationships 
WHERE source_card_id IN (
  SELECT id FROM context_cards 
  WHERE tenant_id = 'your-email@example.com'
);

-- Count cards by type
SELECT card_type, COUNT(*) as count 
FROM context_cards 
WHERE tenant_id = 'your-email@example.com' 
GROUP BY card_type;
```

---

## ✅ Testing Checklist

### Backend
- [ ] Backend starts without errors
- [ ] API docs available at /docs
- [ ] Health check endpoint works
- [ ] Card Service routes registered
- [ ] Integration routes registered

### Onboarding
- [ ] Onboarding form loads
- [ ] Form submission works
- [ ] Cards created automatically
- [ ] Card IDs stored in session
- [ ] Email sent (check logs)

### Card Frontend
- [ ] Card Frontend loads
- [ ] Dashboard displays 4 cards
- [ ] Card details page works
- [ ] Tenant isolation works
- [ ] No console errors

### CGS Integration
- [ ] CGS retrieves cards
- [ ] Card context added to prompt
- [ ] Content generated with card info
- [ ] No errors in logs

### Database
- [ ] 4 cards in context_cards table
- [ ] Relationships created
- [ ] RLS policies enforced
- [ ] Tenant isolation works

### Tests
- [ ] Unit tests pass (90%+ coverage)
- [ ] Integration tests pass (85%+ coverage)
- [ ] Frontend tests pass (80%+ coverage)
- [ ] No test failures

---

## 🐛 Troubleshooting

### Backend won't start

**Error: "Port 8000 already in use"**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9  # Linux/Mac
netstat -ano | findstr :8000   # Windows (find PID)
taskkill /PID <PID> /F         # Windows (kill process)
```

**Error: "Module not found"**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Card Frontend won't start

**Error: "Port 3001 already in use"**
```bash
# Kill process on port 3001
lsof -ti:3001 | xargs kill -9  # Linux/Mac
```

**Error: "npm dependencies missing"**
```bash
cd card-frontend
rm -rf node_modules package-lock.json
npm install
```

### Cards not created

**Check logs:**
```bash
# Look for errors in backend logs
tail -f /tmp/backend.log | grep -i "card\|error"
```

**Verify Card Service is configured:**
```bash
# Check .env file
grep CARD_SERVICE .env
```

**Check database:**
```bash
# Verify cards table exists
# Go to Supabase dashboard → Tables → context_cards
```

### Cards not showing in frontend

**Check tenant_id parameter:**
```
http://localhost:3001?tenant_id=your-email@example.com
```

**Check browser console:**
- Open DevTools (F12)
- Check Console tab for errors
- Check Network tab for API calls

**Check API response:**
```bash
curl "http://localhost:8000/api/v1/cards?tenant_id=your-email@example.com"
```

### Content not using card context

**Check CGS logs:**
```bash
# Look for "Added card context" message
```

**Verify card retrieval:**
```bash
curl "http://localhost:8000/api/v1/cards/context/rag-text?tenant_id=your-email@example.com"
```

---

## 📞 Support

If you encounter issues:

1. **Check logs** - Most issues are visible in logs
2. **Run tests** - Tests verify all components work
3. **Check database** - Verify data is stored correctly
4. **Check API** - Use curl to test endpoints directly
5. **Check browser console** - Frontend errors visible there

---

## 🎯 Success Criteria

You've successfully tested the complete flow when:

✅ Onboarding completes without errors
✅ 4 cards created automatically
✅ Cards visible in Card Frontend
✅ Card Frontend displays correct data
✅ CGS generates content with card context
✅ All tests pass
✅ No errors in logs

---

## 📚 Additional Resources

- Backend API Docs: http://localhost:8000/docs
- Card Frontend: http://localhost:3001
- Supabase Dashboard: https://app.supabase.com
- Test Documentation: tests/README.md
- E2E Test Plan: tests/E2E_TEST_PLAN.md

---

**Happy Testing! 🚀**

