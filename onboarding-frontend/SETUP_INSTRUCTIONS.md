# 🚀 Setup Instructions - Fylle AI Onboarding Frontend

## ✅ Stato Implementazione

**Frontend**: ✅ **COMPLETO** - Pronto per testing  
**Backend**: ✅ Attivo su porta 8001  
**Prossimo Step**: Installare Node.js e testare

---

## 📋 Prerequisiti

### 1. Node.js e npm

**Windows**:
1. Scarica Node.js LTS da: https://nodejs.org/
2. Esegui l'installer
3. Verifica installazione:
   ```bash
   node --version  # Dovrebbe mostrare v18.x.x o superiore
   npm --version   # Dovrebbe mostrare v9.x.x o superiore
   ```

### 2. Backend Onboarding Attivo

Assicurati che il backend sia in esecuzione:
```bash
# In un terminale separato
python -m onboarding.api.main
```

Verifica: http://localhost:8001/health

---

## 🔧 Installazione

### Step 1: Naviga nella cartella frontend

```bash
cd onboarding-frontend
```

### Step 2: Installa le dipendenze

```bash
npm install
```

Questo installerà:
- React 18.2
- TypeScript 5.3
- Material-UI 5.15
- Zustand 4.4
- React Query (TanStack Query) 5.14
- React Hook Form 7.48
- Axios 1.6
- Framer Motion 10.16
- E altre dipendenze...

**Tempo stimato**: 2-3 minuti

### Step 3: Verifica configurazione

Controlla che il file `.env` esista e contenga:

```bash
VITE_ONBOARDING_API_URL=http://localhost:8001
VITE_CGS_API_URL=http://localhost:8000
VITE_ENABLE_DASHBOARD=true
VITE_ENABLE_DEBUG_MODE=true
VITE_POLLING_INTERVAL=3000
VITE_MAX_POLLING_ATTEMPTS=40
VITE_ENV=development
```

---

## 🚀 Avvio

### Development Mode

```bash
npm run dev
```

Il frontend sarà disponibile su: **http://localhost:3001**

Il browser si aprirà automaticamente.

### Build per Produzione

```bash
npm run build
```

I file ottimizzati saranno in `dist/`

### Preview Build di Produzione

```bash
npm run preview
```

---

## 🧪 Testing del Flow Completo

### 1. Verifica Backend

Apri http://localhost:8001/health

Dovresti vedere:
```json
{
  "status": "healthy"
}
```

### 2. Apri Frontend

Apri http://localhost:3001

### 3. Test Flow Onboarding

#### Step 1: Company Input
1. Inserisci nome azienda (es: "Acme Corp")
2. (Opzionale) Inserisci website
3. Seleziona goal (es: "LinkedIn Post")
4. (Opzionale) Inserisci email
5. Clicca "Start Research"

#### Step 2: Research Progress
- Vedrai animazione di ricerca
- Progress bar che avanza
- Typing indicators

#### Step 3: Snapshot Review
- Review delle informazioni azienda
- Company info, audience, voice
- Clicca "Continue to Questions"

#### Step 4: Questions
- Rispondi alle domande chiarificatrici
- Form dinamico basato su tipo domanda
- Clicca "Generate Content"

#### Step 5: Execution Progress
- Animazione generazione contenuto
- Progress bar con step dettagliati

#### Step 6: Results
- Visualizzazione contenuto generato
- Opzioni: Copy, Download
- "Start New Onboarding" per ricominciare

---

## 🐛 Troubleshooting

### Problema: `npm: command not found`

**Soluzione**: Node.js non è installato o non è nel PATH
1. Installa Node.js da https://nodejs.org/
2. Riavvia il terminale
3. Verifica con `node --version`

### Problema: Errore durante `npm install`

**Soluzione**:
```bash
# Pulisci cache npm
npm cache clean --force

# Rimuovi node_modules se esiste
rm -rf node_modules

# Reinstalla
npm install
```

### Problema: Frontend non si connette al backend

**Soluzione**:
1. Verifica che backend sia attivo: `curl http://localhost:8001/health`
2. Controlla `.env` che `VITE_ONBOARDING_API_URL=http://localhost:8001`
3. Controlla console browser per errori CORS
4. Abilita debug mode: `VITE_ENABLE_DEBUG_MODE=true`

### Problema: Errore CORS

**Soluzione**: Il backend FastAPI dovrebbe già avere CORS abilitato. Se non funziona:
1. Verifica che `onboarding/api/main.py` abbia middleware CORS
2. Aggiungi `http://localhost:3001` agli allowed origins

### Problema: Porta 3001 già in uso

**Soluzione**:
```bash
# Cambia porta in vite.config.ts
server: {
  port: 3002,  // Usa porta diversa
}
```

---

## 📁 Struttura Progetto

```
onboarding-frontend/
├── src/
│   ├── components/          # Componenti React
│   │   ├── common/          # Header, LoadingSpinner, TypingIndicator
│   │   ├── onboarding/      # ConversationalContainer
│   │   └── steps/           # Step1-6 components
│   ├── services/            # API services
│   │   └── api/             # client.ts, onboardingApi.ts
│   ├── store/               # Zustand stores
│   │   ├── onboardingStore.ts
│   │   └── uiStore.ts
│   ├── types/               # TypeScript types
│   │   └── onboarding.ts
│   ├── hooks/               # Custom hooks
│   │   └── useOnboarding.ts
│   ├── config/              # Configuration
│   │   ├── api.ts
│   │   ├── constants.ts
│   │   └── theme.ts
│   ├── pages/               # Pages
│   │   └── OnboardingPage.tsx
│   ├── assets/              # Static assets
│   │   └── logos/           # Fylle logos
│   ├── App.tsx              # Root component
│   ├── main.tsx             # Entry point
│   └── index.css            # Global styles
├── public/
│   └── index.html
├── .env                     # Environment variables
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

---

## 🎨 Features Implementate

### UI/UX
- ✅ Conversational interface moderna
- ✅ Suggestion chips per input rapido
- ✅ Typing indicators animati
- ✅ Progress stepper
- ✅ Glassmorphism effects
- ✅ Smooth animations
- ✅ Responsive design
- ✅ Toast notifications

### Funzionalità
- ✅ Form validation con Yup
- ✅ State management con Zustand
- ✅ API integration con React Query
- ✅ Error handling
- ✅ Retry logic
- ✅ Request/response logging
- ✅ TypeScript type safety

### Step Components
- ✅ Step 1: Company Input (form con suggestions)
- ✅ Step 2: Research Progress (animated)
- ✅ Step 3: Snapshot Review (dettagliato)
- ✅ Step 4: Questions Form (dinamico)
- ✅ Step 5: Execution Progress (animated)
- ✅ Step 6: Results (con copy/download)

---

## 🔧 Comandi Disponibili

```bash
# Development
npm run dev          # Avvia dev server (porta 3001)

# Build
npm run build        # Build per produzione
npm run preview      # Preview build produzione

# Code Quality
npm run lint         # Lint codice
npm run format       # Format con Prettier
```

---

## 📝 Note Importanti

### Environment Variables

Tutte le variabili d'ambiente devono iniziare con `VITE_` per essere accessibili nel frontend.

### API Endpoints

Il frontend chiama questi endpoint:
- `POST /api/v1/onboarding/start`
- `POST /api/v1/onboarding/{session_id}/answers`
- `GET /api/v1/onboarding/{session_id}/status`
- `GET /api/v1/onboarding/{session_id}`

### Debug Mode

Abilita `VITE_ENABLE_DEBUG_MODE=true` per vedere:
- Log dettagliati delle chiamate API
- Request/response data
- Timing informazioni

---

## 🚀 Prossimi Step

1. **Installare Node.js** (se non già fatto)
2. **Installare dipendenze**: `npm install`
3. **Avviare backend**: `python -m onboarding.api.main`
4. **Avviare frontend**: `npm run dev`
5. **Testare flow completo**
6. **Verificare tutti gli step funzionino**

---

## 📞 Support

### Log Utili

**Frontend logs**: Console browser (F12)  
**Backend logs**: Terminale dove gira `python -m onboarding.api.main`  
**Network requests**: Network tab in browser DevTools

### Debug Checklist

- [ ] Backend attivo su porta 8001?
- [ ] Frontend attivo su porta 3001?
- [ ] File `.env` configurato correttamente?
- [ ] Console browser mostra errori?
- [ ] Network tab mostra chiamate API?
- [ ] Debug mode abilitato?

---

**Status**: 🟢 **READY FOR TESTING**  
**Next**: Installare Node.js e avviare `npm install`

