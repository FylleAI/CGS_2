# 🚀 CGSRef Setup Prompt for Replit Agent

## 📋 **MISSION OVERVIEW**
You need to set up and run the **CGSRef (Content Generation System Reference)** application in Replit. This is a complete AI-powered content generation system with multi-agent workflows, Perplexity AI integration, and a React frontend.

## 🎯 **WHAT YOU'RE SETTING UP**
- **Backend**: FastAPI server with multi-agent orchestration
- **Frontend**: React application with workflow management
- **AI Integration**: OpenAI, Anthropic, DeepSeek, and Perplexity AI
- **Workflows**: Enhanced Article, Premium Newsletter, Siebert Premium Newsletter
- **Features**: Knowledge base, RAG search, premium research capabilities

## 📁 **REPOSITORY INFORMATION**
- **GitHub URL**: https://github.com/FylleAI/CGS_1.git
- **Branch**: main
- **Language**: Python (Backend) + JavaScript/React (Frontend)
- **Architecture**: Microservices with proxy configuration

## 🔧 **STEP-BY-STEP SETUP INSTRUCTIONS**

### **1. CLONE THE REPOSITORY**
```bash
git clone https://github.com/FylleAI/CGS_1.git
cd CGS_1
```

### **2. ENVIRONMENT CONFIGURATION**
Create a `.env` file in the root directory with these **REQUIRED** API keys:

```bash
# REQUIRED: OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# REQUIRED: Perplexity AI API Key (for premium research)
PERPLEXITY_API_KEY=your_perplexity_api_key_here

# OPTIONAL: Additional AI Providers
ANTHROPIC_API_KEY=your_anthropic_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# OPTIONAL: Web Search (for enhanced research)
SERPER_API_KEY=your_serper_api_key_here

# System Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO
WORKFLOW_TIMEOUT_SECONDS=600
MAX_RETRIES=3
```

### **3. BACKEND SETUP (Python/FastAPI)**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the backend server
python start_backend.py
```
**Expected**: Backend should start on port 8001 with message "Server started successfully"

### **4. FRONTEND SETUP (React)**
```bash
# Navigate to React app directory
cd web/react-app

# Install Node.js dependencies
npm install

# Start the React development server
npm start
```
**Expected**: Frontend should start on port 3000 and open in browser

### **5. VERIFY SETUP**
- **Backend Health**: Visit `http://localhost:8001/health` - should return `{"status": "healthy"}`
- **Frontend**: Visit `http://localhost:3000` - should show CGSRef interface
- **API Connection**: Frontend should connect to backend via proxy

## 🤖 **AI PROVIDERS CONFIGURATION**

### **REQUIRED PROVIDERS:**
1. **OpenAI**: For general content generation (GPT-4o, GPT-3.5-turbo)
2. **Perplexity**: For premium research and real-time information

### **OPTIONAL PROVIDERS:**
3. **Anthropic**: For Claude models (enhanced reasoning)
4. **DeepSeek**: For cost-effective generation
5. **Serper**: For web search capabilities

## 🔍 **TESTING THE APPLICATION**

### **1. Basic Content Generation**
- Select "Enhanced Article" workflow
- Enter a topic (e.g., "AI trends 2024")
- Click "Generate Content"
- **Expected**: Article generated in 30-60 seconds

### **2. Premium Newsletter (Perplexity)**
- Select "Siebert Premium Newsletter" 
- Enter financial topic (e.g., "Bitcoin market analysis")
- Click "Generate Content"
- **Expected**: 8-section newsletter in 3-6 minutes with real-time research

### **3. Verify AI Providers**
- Check backend logs for successful API connections
- Test different workflows to verify all providers work
- Monitor costs and token usage in logs

## 🚨 **COMMON ISSUES & SOLUTIONS**

### **Issue 1: Backend Won't Start**
```bash
# Check Python version (requires 3.8+)
python --version

# Install missing dependencies
pip install fastapi uvicorn python-dotenv

# Check port availability
lsof -i :8001
```

### **Issue 2: Frontend Won't Connect**
```bash
# Check Node.js version (requires 14+)
node --version

# Clear npm cache and reinstall
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### **Issue 3: API Keys Not Working**
- Verify `.env` file is in root directory
- Check API key format (no quotes, no spaces)
- Test API keys individually with curl commands
- Check API provider status pages

### **Issue 4: Timeout Errors**
- Complex workflows (Siebert) take 3-6 minutes
- Check timeout configurations in logs
- Verify Perplexity API key for research workflows

## 📊 **EXPECTED PERFORMANCE**

### **Workflow Timing:**
- **Enhanced Article**: 30-60 seconds
- **Premium Newsletter**: 1-2 minutes
- **Siebert Premium Newsletter**: 3-6 minutes (multi-agent + Perplexity)

### **Resource Usage:**
- **Memory**: ~500MB for backend, ~200MB for frontend
- **CPU**: Moderate during generation, low at idle
- **Network**: API calls to AI providers

### **Cost Estimates:**
- **Enhanced Article**: ~$0.001-0.005 per generation
- **Premium Newsletter**: ~$0.005-0.015 per generation
- **Siebert Premium**: ~$0.01-0.03 per generation (includes Perplexity)

## 🎯 **SUCCESS CRITERIA**

### **✅ SETUP COMPLETE WHEN:**
1. Backend starts successfully on port 8001
2. Frontend loads on port 3000 with CGSRef interface
3. Health check returns `{"status": "healthy"}`
4. At least one workflow generates content successfully
5. Logs show successful AI provider connections

### **✅ ADVANCED FEATURES WORKING:**
1. Perplexity research integration active
2. Multi-agent workflows (4 agents) orchestrating properly
3. Knowledge base RAG search functional
4. All 3 workflow types generating quality content
5. Timeout handling working for complex workflows

## 🔧 **REPLIT-SPECIFIC CONSIDERATIONS**

### **Port Configuration:**
- Backend: Use port 8001 (configured in start_backend.py)
- Frontend: Use port 3000 (React default)
- Ensure both ports are exposed in Replit

### **Environment Variables:**
- Use Replit's Secrets tab for API keys
- Map secrets to .env file or environment variables
- Never commit API keys to repository

### **File Permissions:**
- Ensure execute permissions on start_backend.py
- Check write permissions for data/output directory
- Verify log file creation permissions

### **Memory Management:**
- Monitor Replit memory usage during complex workflows
- Consider upgrading Replit plan for heavy usage
- Implement cleanup for temporary files

## 📞 **SUPPORT & TROUBLESHOOTING**

### **Debug Commands:**
```bash
# Check backend logs
tail -f logs/app.log

# Test API endpoints
curl http://localhost:8001/health
curl http://localhost:8001/api/v1/providers

# Check frontend build
cd web/react-app && npm run build
```

### **Log Locations:**
- Backend logs: `logs/app.log`
- Frontend logs: Browser console
- Workflow logs: `data/output/logs/`

### **Key Files to Monitor:**
- `start_backend.py` - Backend startup
- `web/react-app/package.json` - Frontend dependencies
- `core/infrastructure/config/settings.py` - System configuration
- `.env` - Environment variables

## 🎉 **FINAL VERIFICATION**

Once setup is complete, test this complete workflow:

1. **Open CGSRef**: http://localhost:3000
2. **Select**: "Siebert Premium Newsletter"
3. **Topic**: "Tesla stock analysis Q4 2024"
4. **Generate**: Click generate and wait 3-6 minutes
5. **Verify**: 8-section newsletter with real-time research data

**If this works, your CGSRef setup is 100% complete and production-ready!** 🚀

---

## 📋 **QUICK CHECKLIST**
- [ ] Repository cloned
- [ ] .env file created with API keys
- [ ] Backend dependencies installed
- [ ] Backend started on port 8001
- [ ] Frontend dependencies installed  
- [ ] Frontend started on port 3000
- [ ] Health check passes
- [ ] Basic workflow tested
- [ ] Perplexity integration verified
- [ ] All 3 workflow types functional

**Good luck with your CGSRef setup!** 🎯

---

## 🔥 **REPLIT AGENT SPECIFIC INSTRUCTIONS**

### **IMMEDIATE ACTIONS FOR REPLIT AGENT:**

1. **Fork/Import Repository:**
   ```bash
   # In Replit, create new Python Repl and import from GitHub
   # URL: https://github.com/FylleAI/CGS_1.git
   ```

2. **Configure Replit Environment:**
   - Go to Replit Secrets tab
   - Add these secrets:
     - `OPENAI_API_KEY` = (your OpenAI key)
     - `PERPLEXITY_API_KEY` = (your Perplexity key)
     - `ANTHROPIC_API_KEY` = (optional)
     - `DEEPSEEK_API_KEY` = (optional)

3. **Create .replit Configuration:**
   ```toml
   # .replit file
   run = "python start_backend.py"
   language = "python3"

   [nix]
   channel = "stable-22_11"

   [deployment]
   run = ["sh", "-c", "python start_backend.py"]
   ```

4. **Install Dependencies Automatically:**
   ```bash
   # This should run automatically in Replit
   pip install -r requirements.txt
   ```

5. **Start Backend First:**
   ```bash
   # Run this in Replit shell
   python start_backend.py
   ```

6. **Start Frontend in New Tab:**
   ```bash
   # Open new shell tab in Replit
   cd web/react-app
   npm install
   npm start
   ```

### **REPLIT-SPECIFIC CONFIGURATIONS:**

#### **Port Exposure:**
- Backend will run on port 8001
- Frontend will run on port 3000
- Both should be automatically exposed by Replit

#### **Environment Variables:**
```python
# Replit automatically loads secrets as environment variables
# No need to create .env file manually
```

#### **File Structure Verification:**
```
CGS_1/
├── start_backend.py          # Main backend starter
├── requirements.txt          # Python dependencies
├── core/                     # Backend core logic
├── web/react-app/           # Frontend React app
├── data/                    # Knowledge base & output
├── logs/                    # Application logs
└── .env.example            # Environment template
```

### **TESTING IN REPLIT:**

1. **Backend Health Check:**
   - Open Replit webview for port 8001
   - Navigate to `/health`
   - Should see: `{"status": "healthy"}`

2. **Frontend Access:**
   - Open Replit webview for port 3000
   - Should see CGSRef interface

3. **Full Workflow Test:**
   - Select "Enhanced Article"
   - Topic: "AI in 2024"
   - Generate content
   - Should complete in 30-60 seconds

### **REPLIT TROUBLESHOOTING:**

#### **If Backend Fails:**
```bash
# Check Python version
python --version  # Should be 3.8+

# Manual dependency install
pip install fastapi uvicorn python-dotenv pydantic

# Check port
netstat -tulpn | grep 8001
```

#### **If Frontend Fails:**
```bash
# Check Node version
node --version  # Should be 14+

# Clear and reinstall
cd web/react-app
rm -rf node_modules
npm cache clean --force
npm install
```

#### **If API Keys Don't Work:**
- Verify secrets are set in Replit Secrets tab
- Restart the Repl to reload environment variables
- Check logs for API connection errors

### **REPLIT PERFORMANCE OPTIMIZATION:**

1. **Memory Management:**
   - Complex workflows use ~700MB total
   - Consider Replit Hacker plan for better performance

2. **Startup Time:**
   - First startup: 2-3 minutes (dependency installation)
   - Subsequent startups: 30-60 seconds

3. **Concurrent Users:**
   - Single Repl supports 1-5 concurrent users
   - For production, consider Replit Deployments

### **SUCCESS INDICATORS IN REPLIT:**

✅ **Setup Successful When:**
- Both ports (8001, 3000) show green in Replit
- Webview shows CGSRef interface
- Console shows "Server started successfully"
- No error messages in logs

✅ **Advanced Features Working:**
- Perplexity research generates real-time data
- Siebert workflow completes in 3-6 minutes
- All 4 AI providers connect successfully
- Knowledge base RAG search returns results

### **REPLIT DEPLOYMENT READY:**
Once working in development, you can deploy to Replit Deployments for production use with custom domain and better performance.

**Your CGSRef system will be fully operational in Replit!** 🚀
