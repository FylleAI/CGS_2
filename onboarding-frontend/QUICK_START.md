# ⚡ Quick Start - Fylle AI Onboarding Frontend

## 🎯 Obiettivo

Avviare il frontend onboarding in **5 minuti**.

---

## ✅ Prerequisiti

### 1. Node.js (RICHIESTO)

**Verifica se installato**:
```bash
node --version
```

**Se non installato**:
1. Vai su: https://nodejs.org/
2. Scarica versione **LTS** (18.x o superiore)
3. Installa e riavvia terminale
4. Verifica: `node --version`

### 2. Backend Onboarding (RICHIESTO)

**Verifica se attivo**:
```bash
curl http://localhost:8001/health
```

**Se non attivo**:
```bash
# In un terminale separato
cd C:\Users\david\Desktop\onboarding
python -m onboarding.api.main
```

---

## 🚀 Avvio in 3 Step

### Step 1: Naviga nella cartella

```bash
cd C:\Users\david\Desktop\onboarding\onboarding-frontend
```

### Step 2: Installa dipendenze (SOLO PRIMA VOLTA)

```bash
npm install
```

⏱️ **Tempo**: 2-3 minuti

### Step 3: Avvia frontend

```bash
npm run dev
```

✅ **Fatto!** Il browser si aprirà automaticamente su http://localhost:3001

---

## 🧪 Test Rapido

### 1. Verifica UI

- ✅ Vedi logo Fylle in alto?
- ✅ Vedi form "Company Input"?
- ✅ Vedi suggestion chips (Tech Startup, E-commerce, etc.)?

### 2. Test Flow Minimo

1. **Clicca** chip "Tech Startup"
2. **Seleziona** goal: "LinkedIn Post"
3. **Clicca** "Start Research"
4. **Osserva** progress animato
5. **Attendi** completamento flow

---

## 📁 File Importanti

```
onboarding-frontend/
├── QUICK_START.md              ← Sei qui
├── SETUP_INSTRUCTIONS.md       ← Guida dettagliata
├── TEST_SCENARIOS.md           ← Test completi
├── IMPLEMENTATION_GUIDE.md     ← Dettagli implementazione
├── README.md                   ← Documentazione progetto
├── .env                        ← Configurazione
└── src/                        ← Codice sorgente
```

---

## 🐛 Problemi Comuni

### ❌ `npm: command not found`

**Soluzione**: Node.js non installato
1. Installa da https://nodejs.org/
2. Riavvia terminale
3. Riprova

### ❌ `ECONNREFUSED localhost:8001`

**Soluzione**: Backend non attivo
```bash
# In terminale separato
python -m onboarding.api.main
```

### ❌ Porta 3001 già in uso

**Soluzione**: Cambia porta in `vite.config.ts`:
```typescript
server: {
  port: 3002,  // Usa porta diversa
}
```

### ❌ Errori durante `npm install`

**Soluzione**: Pulisci cache
```bash
npm cache clean --force
npm install
```

---

## 📊 Comandi Utili

```bash
# Development
npm run dev          # Avvia dev server

# Build
npm run build        # Build produzione
npm run preview      # Preview build

# Code Quality
npm run lint         # Lint codice
npm run format       # Format codice
```

---

## 🎨 Features Principali

### UI Moderna
- ✅ Design conversazionale
- ✅ Suggestion chips per input rapido
- ✅ Typing indicators animati
- ✅ Progress bars con gradient
- ✅ Glassmorphism effects
- ✅ Toast notifications

### Flow Completo (6 Step)
1. **Company Input** - Form con validazione
2. **Research Progress** - Animazione ricerca
3. **Snapshot Review** - Review dati azienda
4. **Questions** - Form domande dinamico
5. **Execution Progress** - Generazione contenuto
6. **Results** - Visualizzazione + download

### Tech Stack
- React 18 + TypeScript
- Material-UI (MUI)
- Zustand (state)
- React Query (API)
- React Hook Form (forms)
- Axios (HTTP)

---

## 📞 Supporto

### Debug Mode

Abilita logging dettagliato in `.env`:
```bash
VITE_ENABLE_DEBUG_MODE=true
```

Poi apri Console browser (F12) per vedere log API.

### Verifica Configurazione

Controlla `.env`:
```bash
VITE_ONBOARDING_API_URL=http://localhost:8001
VITE_CGS_API_URL=http://localhost:8000
VITE_ENABLE_DEBUG_MODE=true
```

### Log Utili

- **Frontend logs**: Console browser (F12)
- **Backend logs**: Terminale backend
- **Network requests**: Network tab (F12)

---

## 🎯 Prossimi Step

### Dopo il primo avvio:

1. **Testa flow completo** (vedi `TEST_SCENARIOS.md`)
2. **Verifica responsive** (resize browser)
3. **Testa error handling** (ferma backend e riprova)
4. **Personalizza** (modifica theme, colori, etc.)

### Per produzione:

1. **Build**: `npm run build`
2. **Test build**: `npm run preview`
3. **Deploy**: Carica cartella `dist/` su server

---

## ✅ Checklist Avvio

- [ ] Node.js installato (`node --version`)
- [ ] Backend attivo (`curl http://localhost:8001/health`)
- [ ] Dipendenze installate (`npm install`)
- [ ] Frontend avviato (`npm run dev`)
- [ ] Browser aperto su http://localhost:3001
- [ ] UI visibile e funzionante
- [ ] Test flow minimo completato

---

## 🎉 Tutto Pronto!

Se hai completato la checklist, il frontend è **operativo**!

### Risorse:
- **Frontend**: http://localhost:3001
- **Backend**: http://localhost:8001
- **Docs Backend**: http://localhost:8001/docs

### Documentazione:
- `SETUP_INSTRUCTIONS.md` - Setup dettagliato
- `TEST_SCENARIOS.md` - Test completi
- `IMPLEMENTATION_GUIDE.md` - Dettagli tecnici
- `README.md` - Overview progetto

---

**Developed with ❤️ for Fylle AI**  
**Version**: 1.0.0  
**Status**: 🟢 **READY**

---

## 💡 Tips

### Hot Reload
Il frontend ha **hot reload** attivo. Modifica file in `src/` e vedi cambiamenti istantanei nel browser.

### DevTools
Installa **React DevTools** extension per debug avanzato.

### Performance
Per build ottimizzato: `npm run build` (output in `dist/`)

### Customization
- **Theme**: `src/config/theme.ts`
- **Colors**: Cambia `#00D084` con tuo brand color
- **Logo**: Sostituisci file in `src/assets/logos/`
- **Steps**: Modifica componenti in `src/components/steps/`

---

**Happy Coding! 🚀**

