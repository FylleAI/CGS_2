# 🧭 Frontend Onboarding - Quick Navigation

## 📍 Dove Sei

Sei nella **root del progetto CGS_2**. Il nuovo frontend onboarding è in:

```
📁 C:\Users\david\Desktop\onboarding\onboarding-frontend\
```

---

## 🚀 Start Here

### Per Iniziare SUBITO:

```bash
cd onboarding-frontend
```

Poi leggi: **`QUICK_START.md`** (5 minuti per avviare tutto)

---

## 📚 Documentazione Disponibile

### 🎯 Root Project (`C:\Users\david\Desktop\onboarding\`)

| File | Descrizione | Quando Usarlo |
|------|-------------|---------------|
| `FRONTEND_IMPLEMENTATION_SUMMARY.md` | ✅ **Riepilogo completo implementazione** | Overview generale progetto |
| `FRONTEND_QUICK_NAVIGATION.md` | 📍 **Questa guida** | Orientarsi nel progetto |

### 🎨 Frontend (`onboarding-frontend/`)

| File | Descrizione | Quando Usarlo |
|------|-------------|---------------|
| `QUICK_START.md` | ⚡ **Avvio rapido (5 min)** | Prima volta che avvii |
| `SETUP_INSTRUCTIONS.md` | 📖 **Setup dettagliato** | Problemi o configurazione avanzata |
| `TEST_SCENARIOS.md` | 🧪 **Test completi** | Testare tutte le funzionalità |
| `IMPLEMENTATION_GUIDE.md` | 🔧 **Dettagli tecnici** | Sviluppo e customizzazione |
| `README.md` | 📘 **Documentazione progetto** | Overview architettura |

---

## 🎯 Workflow Consigliato

### 1️⃣ Prima Volta (Setup)

```bash
# 1. Vai nella cartella frontend
cd onboarding-frontend

# 2. Leggi quick start
cat QUICK_START.md

# 3. Installa Node.js (se necessario)
# Vai su: https://nodejs.org/

# 4. Installa dipendenze
npm install

# 5. Avvia backend (terminale separato)
cd ..
python -m onboarding.api.main

# 6. Avvia frontend (torna al terminale frontend)
cd onboarding-frontend
npm run dev
```

### 2️⃣ Sviluppo Quotidiano

```bash
# Terminale 1: Backend
python -m onboarding.api.main

# Terminale 2: Frontend
cd onboarding-frontend
npm run dev
```

### 3️⃣ Testing

```bash
# Leggi scenari di test
cat onboarding-frontend/TEST_SCENARIOS.md

# Esegui test manuali seguendo la guida
```

### 4️⃣ Customizzazione

```bash
# Modifica theme
code onboarding-frontend/src/config/theme.ts

# Modifica step components
code onboarding-frontend/src/components/steps/

# Modifica configurazione
code onboarding-frontend/.env
```

---

## 📁 Struttura Progetto

```
C:\Users\david\Desktop\onboarding\
│
├── 📁 onboarding-frontend\          ← NUOVO FRONTEND
│   ├── QUICK_START.md               ← ⚡ INIZIA QUI
│   ├── SETUP_INSTRUCTIONS.md        ← Setup dettagliato
│   ├── TEST_SCENARIOS.md            ← Test completi
│   ├── IMPLEMENTATION_GUIDE.md      ← Dettagli tecnici
│   ├── README.md                    ← Documentazione
│   ├── package.json                 ← Dipendenze
│   ├── .env                         ← Configurazione
│   └── src\                         ← Codice sorgente
│       ├── components\              ← Componenti React
│       ├── services\                ← API services
│       ├── store\                   ← State management
│       ├── types\                   ← TypeScript types
│       ├── hooks\                   ← Custom hooks
│       ├── config\                  ← Configuration
│       ├── pages\                   ← Pages
│       └── assets\                  ← Loghi, immagini
│
├── 📁 onboarding\                   ← BACKEND ONBOARDING
│   ├── api\                         ← FastAPI endpoints
│   ├── application\                 ← Business logic
│   ├── domain\                      ← Domain models
│   └── infrastructure\              ← Adapters (Gemini, Perplexity, CGS)
│
├── 📁 web\react-app\                ← FRONTEND CGS ESISTENTE
│   └── ...                          ← (Non modificato)
│
├── FRONTEND_IMPLEMENTATION_SUMMARY.md  ← Riepilogo completo
└── FRONTEND_QUICK_NAVIGATION.md        ← Questa guida
```

---

## 🔗 Link Utili

### Applicazioni

| Servizio | URL | Porta |
|----------|-----|-------|
| **Frontend Onboarding** | http://localhost:3001 | 3001 |
| **Backend Onboarding** | http://localhost:8001 | 8001 |
| **Backend CGS** | http://localhost:8000 | 8000 |
| **Frontend CGS** | http://localhost:3000 | 3000 |

### API Docs

| Servizio | URL |
|----------|-----|
| **Onboarding API Docs** | http://localhost:8001/docs |
| **CGS API Docs** | http://localhost:8000/docs |

### Health Checks

```bash
# Onboarding Backend
curl http://localhost:8001/health

# CGS Backend
curl http://localhost:8000/health
```

---

## 🎨 Features Implementate

### ✅ UI Components
- [x] Header con logo Fylle
- [x] Loading spinner
- [x] Typing indicator (3 dots animati)
- [x] Conversational container
- [x] Suggestion chips
- [x] Progress stepper

### ✅ Step Components (6 Step)
- [x] Step 1: Company Input (form + validation)
- [x] Step 2: Research Progress (animated)
- [x] Step 3: Snapshot Review (dettagliato)
- [x] Step 4: Questions Form (dinamico)
- [x] Step 5: Execution Progress (animated)
- [x] Step 6: Results (copy/download)

### ✅ Core Features
- [x] State management (Zustand)
- [x] API integration (React Query + Axios)
- [x] Form validation (React Hook Form + Yup)
- [x] Error handling
- [x] Toast notifications
- [x] TypeScript types
- [x] Responsive design
- [x] Glassmorphism UI

---

## 🐛 Troubleshooting Rapido

### ❌ Frontend non si avvia

```bash
# Verifica Node.js
node --version  # Deve essere v18+

# Reinstalla dipendenze
cd onboarding-frontend
rm -rf node_modules
npm install
```

### ❌ Backend non risponde

```bash
# Verifica backend attivo
curl http://localhost:8001/health

# Se non attivo, avvia
python -m onboarding.api.main
```

### ❌ Errori CORS

Verifica che backend abbia CORS abilitato per `http://localhost:3001`

### ❌ Porta già in uso

Cambia porta in `onboarding-frontend/vite.config.ts`:
```typescript
server: { port: 3002 }
```

---

## 📊 Status Progetto

| Componente | Status | Note |
|------------|--------|------|
| **Frontend Setup** | ✅ Completo | Vite + React + TS |
| **UI Components** | ✅ Completo | 15+ componenti |
| **Step Components** | ✅ Completo | 6 step implementati |
| **State Management** | ✅ Completo | Zustand stores |
| **API Integration** | ✅ Completo | React Query + Axios |
| **Form Validation** | ✅ Completo | React Hook Form + Yup |
| **Theme & Design** | ✅ Completo | MUI + Fylle branding |
| **Documentation** | ✅ Completo | 5 file MD |
| **Testing** | ⏳ Pending | Richiede Node.js |

**Overall**: 🟢 **90% Complete** - Ready for testing

---

## 🎯 Next Steps

### Immediati
1. ✅ Installa Node.js (se non già fatto)
2. ✅ `cd onboarding-frontend`
3. ✅ `npm install`
4. ✅ `npm run dev`
5. ✅ Testa flow completo

### Opzionali
- [ ] Customizza theme/colori
- [ ] Aggiungi unit tests
- [ ] Implementa polling automatico
- [ ] Aggiungi dashboard sessioni
- [ ] Deploy in produzione

---

## 💡 Tips

### Hot Reload
Modifica file in `src/` e vedi cambiamenti istantanei nel browser.

### Debug Mode
Abilita in `.env`:
```bash
VITE_ENABLE_DEBUG_MODE=true
```

### DevTools
- **React DevTools**: Per debug componenti
- **Redux DevTools**: Per debug Zustand store
- **Network Tab**: Per debug API calls

### Performance
Build ottimizzato:
```bash
npm run build
npm run preview
```

---

## 📞 Supporto

### Documentazione
1. `onboarding-frontend/QUICK_START.md` - Avvio rapido
2. `onboarding-frontend/SETUP_INSTRUCTIONS.md` - Setup dettagliato
3. `onboarding-frontend/TEST_SCENARIOS.md` - Test completi
4. `FRONTEND_IMPLEMENTATION_SUMMARY.md` - Riepilogo completo

### Debug
- **Console browser** (F12) - Frontend logs
- **Network tab** (F12) - API calls
- **Terminale backend** - Backend logs

### Configurazione
- `.env` - Environment variables
- `vite.config.ts` - Vite config
- `tsconfig.json` - TypeScript config
- `src/config/` - App configuration

---

## 🎉 Ready to Start!

### Quick Command:

```bash
cd onboarding-frontend && cat QUICK_START.md
```

---

**Developed with ❤️ for Fylle AI**  
**Version**: 1.0.0  
**Status**: 🟢 **READY FOR TESTING**

