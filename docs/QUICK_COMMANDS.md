# ⚡ Quick Commands Reference

**Progetto**: CGS_2  
**Last Updated**: 2025-10-25

---

## 🚀 Avvio Rapido

### **Setup Iniziale (Solo Prima Volta)**

```bash
# 1. Clone repository
git clone https://github.com/FylleAI/CGS_2.git
cd CGS_2

# 2. Setup environment
cp .env.example .env
# Poi edita .env con le tue API keys

# 3. Setup Python
python -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt

# 4. Setup Frontend
cd onboarding-frontend
npm install
cd ..

# 5. Verifica setup
python -c "from onboarding.config.settings import get_settings; print('✅ Setup OK')"
```

---

## 🏃 Comandi Quotidiani

### **Avviare Tutti i Servizi**

```bash
# Terminal 1: Backend CGS
source venv/bin/activate
python start_backend.py

# Terminal 2: Backend Onboarding
source venv/bin/activate
cd onboarding
uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload

# Terminal 3: Frontend
cd onboarding-frontend
npm run dev
```

### **Avviare con Docker (Alternativa)**

```bash
# Avvia tutti i servizi con Docker Compose
docker-compose up -d

# Verifica status
docker-compose ps

# Vedi logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## 🧪 Testing

### **Test Backend**

```bash
# Attiva venv
source venv/bin/activate

# Run all tests
pytest

# Run specific test file
pytest tests/test_research_agent.py

# Run with coverage
pytest --cov=onboarding --cov-report=html

# Run specific test
pytest tests/test_research_agent.py::test_research_agent_basic -v
```

### **Test Frontend**

```bash
cd onboarding-frontend

# Run tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage
```

### **Test API Endpoints**

```bash
# Health check CGS
curl http://localhost:8000/health

# Health check Onboarding
curl http://localhost:8001/health

# Start onboarding session
curl -X POST http://localhost:8001/api/v1/onboarding/start \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Fylle AI",
    "website": "https://fylle.ai",
    "user_email": "test@fylle.ai"
  }'

# Get session status
curl http://localhost:8001/api/v1/onboarding/sessions/{session_id}
```

---

## 🗄️ Database

### **Supabase Migrations**

```bash
# Run migration
python scripts/run_migration_003.py

# Test company context repository
python scripts/test_company_context_repository.py

# Sync storage to database
python scripts/sync_storage_to_database.py
```

### **Local Database**

```bash
# View SQLite database (if using local)
sqlite3 cgsref.db

# List tables
.tables

# Query example
SELECT * FROM company_contexts LIMIT 5;

# Exit
.quit
```

---

## 📦 Dependency Management

### **Python**

```bash
# Install new package
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt

# Install from requirements
pip install -r requirements.txt

# Update all packages
pip list --outdated
pip install --upgrade package-name
```

### **Node/npm**

```bash
cd onboarding-frontend

# Install new package
npm install package-name

# Install dev dependency
npm install --save-dev package-name

# Update package
npm update package-name

# Check outdated packages
npm outdated

# Update all packages
npm update
```

---

## 🔍 Debugging

### **Backend Logs**

```bash
# Tail logs
tail -f logs/app.log

# Search logs
grep "ERROR" logs/app.log

# View last 100 lines
tail -n 100 logs/app.log
```

### **Python Debugger**

```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use built-in breakpoint() (Python 3.7+)
breakpoint()

# Common pdb commands:
# n - next line
# s - step into function
# c - continue
# l - list code
# p variable - print variable
# q - quit
```

### **Frontend Debugging**

```bash
# Open browser console (Chrome/Firefox)
# F12 or Cmd+Option+I (Mac) / Ctrl+Shift+I (Windows)

# View React DevTools
# Install extension: https://react.dev/learn/react-developer-tools

# View network requests
# Browser DevTools → Network tab
```

---

## 🔄 Git Workflow

### **Daily Workflow**

```bash
# Pull latest changes
git pull origin main

# Create feature branch
git checkout -b feature/card-implementation

# Check status
git status

# Add changes
git add .

# Commit
git commit -m "feat: implement card creation service"

# Push to remote
git push origin feature/card-implementation

# Create PR on GitHub
# Go to: https://github.com/FylleAI/CGS_2/pulls
```

### **Commit Message Convention**

```bash
# Format: <type>: <description>

# Types:
feat:     # New feature
fix:      # Bug fix
docs:     # Documentation only
style:    # Formatting, missing semicolons, etc.
refactor: # Code change that neither fixes a bug nor adds a feature
test:     # Adding tests
chore:    # Updating build tasks, package manager configs, etc.

# Examples:
git commit -m "feat: add card creation from snapshot"
git commit -m "fix: resolve Supabase connection timeout"
git commit -m "docs: update setup guide for new PC"
git commit -m "refactor: extract card repository to separate file"
```

---

## 🧹 Cleanup

### **Clean Python Cache**

```bash
# Remove __pycache__ directories
find . -type d -name "__pycache__" -exec rm -rf {} +

# Remove .pyc files
find . -type f -name "*.pyc" -delete

# Remove pytest cache
rm -rf .pytest_cache

# Remove coverage files
rm -rf htmlcov .coverage coverage.xml
```

### **Clean Node Modules**

```bash
cd onboarding-frontend

# Remove node_modules
rm -rf node_modules

# Remove package-lock.json
rm package-lock.json

# Reinstall
npm install
```

### **Clean Data Directories**

```bash
# ⚠️ WARNING: This deletes generated data!

# Clean cache
rm -rf data/cache/*

# Clean output
rm -rf data/output/*

# Clean ChromaDB
rm -rf data/chroma/*

# Clean logs
rm -rf logs/*.log
```

---

## 📊 Monitoring

### **Check Service Status**

```bash
# Check if services are running
lsof -i :8000  # CGS
lsof -i :8001  # Onboarding
lsof -i :5173  # Frontend

# Kill process on port
kill -9 $(lsof -t -i:8000)
```

### **System Resources**

```bash
# Check Python process memory
ps aux | grep python

# Check disk usage
du -sh data/*

# Check available disk space
df -h
```

---

## 🔐 Security

### **Check for Secrets in Code**

```bash
# Search for potential API keys
grep -r "sk-" . --exclude-dir={venv,node_modules,.git}

# Search for hardcoded passwords
grep -r "password.*=" . --exclude-dir={venv,node_modules,.git}

# Verify .env is gitignored
git check-ignore .env
# Should output: .env
```

### **Rotate API Keys**

```bash
# 1. Update .env with new keys
nano .env

# 2. Restart services
# Kill all terminals and restart

# 3. Test with new keys
curl http://localhost:8001/health
```

---

## 📚 Documentation

### **Generate API Docs**

```bash
# Backend API docs (FastAPI auto-generated)
# Open: http://localhost:8000/docs (Swagger UI)
# Open: http://localhost:8000/redoc (ReDoc)

# Onboarding API docs
# Open: http://localhost:8001/docs
```

### **View Documentation**

```bash
# Open main README
open README.md  # macOS
xdg-open README.md  # Linux

# View specific docs
open docs/CARD_IMPLEMENTATION_STRATEGY.md
open docs/SETUP_NEW_PC_GUIDE.md
open docs/FEATURE_OVERVIEW_ESSENTIALS.md
```

---

## 🆘 Emergency Commands

### **Service Won't Start**

```bash
# 1. Check if port is already in use
lsof -i :8000
lsof -i :8001

# 2. Kill existing process
kill -9 $(lsof -t -i:8000)

# 3. Check environment
source venv/bin/activate
python -c "from onboarding.config.settings import get_settings; print(get_settings())"

# 4. Check logs
tail -f logs/app.log
```

### **Database Connection Failed**

```bash
# 1. Verify Supabase credentials
cat .env | grep SUPABASE

# 2. Test connection
python scripts/test_company_context_repository.py

# 3. Check Supabase status
# Go to: https://status.supabase.com/
```

### **Frontend Build Failed**

```bash
cd onboarding-frontend

# 1. Clear cache
rm -rf node_modules package-lock.json

# 2. Reinstall
npm install

# 3. Try build
npm run build

# 4. Check for TypeScript errors
npm run type-check
```

---

## 🎯 Shortcuts

### **Aliases (Add to ~/.bashrc or ~/.zshrc)**

```bash
# CGS_2 shortcuts
alias cgs='cd ~/Desktop/CGS_2'
alias cgs-activate='source ~/Desktop/CGS_2/venv/bin/activate'
alias cgs-backend='cd ~/Desktop/CGS_2 && source venv/bin/activate && python start_backend.py'
alias cgs-onboarding='cd ~/Desktop/CGS_2/onboarding && source ../venv/bin/activate && uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload'
alias cgs-frontend='cd ~/Desktop/CGS_2/onboarding-frontend && npm run dev'
alias cgs-test='cd ~/Desktop/CGS_2 && source venv/bin/activate && pytest'
alias cgs-logs='tail -f ~/Desktop/CGS_2/logs/app.log'

# Reload shell config
source ~/.bashrc  # or source ~/.zshrc
```

---

**Prepared by**: Fylle AI Team  
**Last Updated**: 2025-10-25  
**Status**: ✅ Ready to Use

