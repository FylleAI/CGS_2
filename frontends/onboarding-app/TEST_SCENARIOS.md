# 🧪 Test Scenarios - Fylle AI Onboarding Frontend

## 📋 Checklist Pre-Test

- [ ] Node.js 18+ installato (`node --version`)
- [ ] Backend onboarding attivo su porta 8001 (`curl http://localhost:8001/health`)
- [ ] Dipendenze frontend installate (`npm install`)
- [ ] Frontend avviato (`npm run dev`)
- [ ] Browser aperto su http://localhost:3001

---

## ✅ Test Scenario 1: Happy Path - Flow Completo

### Obiettivo
Testare il flusso completo dall'input azienda alla generazione contenuto.

### Steps

#### 1. Step 1 - Company Input
1. Apri http://localhost:3001
2. Verifica che vedi:
   - Header con logo Fylle
   - Titolo "Welcome to Fylle AI Onboarding"
   - Form con campi: Company Name, Website, Goal, Email, Additional Context
   - Suggestion chips: "Tech Startup", "E-commerce", "SaaS", etc.
3. **Azione**: Clicca chip "Tech Startup"
   - ✅ Campo "Company Name" si riempie con "Tech Startup"
4. **Azione**: Compila form:
   - Company Name: "Acme Corp"
   - Website: "https://acme.com"
   - Goal: "LinkedIn Post"
   - Email: "test@acme.com"
   - Additional Context: "We build AI tools for developers"
5. **Azione**: Clicca "Start Research"
6. **Verifica**:
   - ✅ Bottone mostra loading spinner
   - ✅ Passa a Step 2

#### 2. Step 2 - Research Progress
1. **Verifica**:
   - ✅ Titolo "🔍 Researching Your Company"
   - ✅ Progress bar animata
   - ✅ 4 step di ricerca visibili
   - ✅ Typing indicator su step corrente
   - ✅ CheckCircle su step completati
2. **Attendi**: ~10-15 secondi
3. **Verifica**:
   - ✅ Passa automaticamente a Step 3

#### 3. Step 3 - Snapshot Review
1. **Verifica**:
   - ✅ Titolo "✅ Research Complete!"
   - ✅ Card "Company Overview" con nome azienda
   - ✅ Card "Target Audience"
   - ✅ Card "Brand Voice"
   - ✅ Card "Insights" (se disponibile)
   - ✅ Bottone "Continue to Questions"
2. **Azione**: Clicca "Continue to Questions"
3. **Verifica**:
   - ✅ Passa a Step 4

#### 4. Step 4 - Questions Form
1. **Verifica**:
   - ✅ Titolo "📝 A Few Questions"
   - ✅ Lista domande con numerazione
   - ✅ Ogni domanda ha: question, reason, input field
   - ✅ Bottone "Generate Content"
2. **Azione**: Rispondi alle domande
   - Compila tutti i campi richiesti (*)
3. **Azione**: Clicca "Generate Content"
4. **Verifica**:
   - ✅ Bottone mostra "Generating Content..."
   - ✅ Passa a Step 5

#### 5. Step 5 - Execution Progress
1. **Verifica**:
   - ✅ Titolo "⚙️ Generating Your Content"
   - ✅ Progress bar animata con gradient
   - ✅ Percentuale progresso (0-100%)
   - ✅ 5 step di esecuzione
   - ✅ Typing indicator su step corrente
   - ✅ Chip "Estimated time: 2-3 minutes"
2. **Attendi**: ~2-3 minuti (o meno se simulato)
3. **Verifica**:
   - ✅ Passa automaticamente a Step 6

#### 6. Step 6 - Results
1. **Verifica**:
   - ✅ Icona CheckCircle verde grande
   - ✅ Titolo "🎉 Success!"
   - ✅ Chip "Content Generated"
   - ✅ Card con preview contenuto
   - ✅ Bottoni: Copy, Download
   - ✅ Card "Session Details"
   - ✅ Bottone "Start New Onboarding"
2. **Azione**: Clicca "Copy to clipboard"
   - ✅ Toast notification "Content copied to clipboard!"
3. **Azione**: Clicca "Download"
   - ✅ File .txt scaricato
   - ✅ Toast notification "Content downloaded!"
4. **Azione**: Clicca "Start New Onboarding"
   - ✅ Torna a Step 1
   - ✅ Form vuoto

**✅ Test Passed**: Flow completo funziona

---

## ⚠️ Test Scenario 2: Form Validation

### Obiettivo
Testare validazione form Step 1.

### Steps

#### Test 2.1: Campo Required
1. Vai a Step 1
2. **Azione**: Lascia "Company Name" vuoto
3. **Azione**: Clicca "Start Research"
4. **Verifica**:
   - ✅ Errore sotto campo: "Company name is required"
   - ✅ Campo evidenziato in rosso
   - ✅ Form non inviato

#### Test 2.2: URL Validation
1. **Azione**: Inserisci website invalido: "not-a-url"
2. **Azione**: Clicca "Start Research"
3. **Verifica**:
   - ✅ Errore: "Must be a valid URL"

#### Test 2.3: Email Validation
1. **Azione**: Inserisci email invalida: "not-an-email"
2. **Azione**: Clicca "Start Research"
3. **Verifica**:
   - ✅ Errore: "Must be a valid email"

#### Test 2.4: Goal Required
1. **Azione**: Compila Company Name ma non selezionare Goal
2. **Azione**: Clicca "Start Research"
3. **Verifica**:
   - ✅ Errore: "Please select a goal"

**✅ Test Passed**: Validazione funziona

---

## 🔴 Test Scenario 3: Error Handling

### Obiettivo
Testare gestione errori API.

### Steps

#### Test 3.1: Backend Offline
1. **Setup**: Ferma backend onboarding (Ctrl+C)
2. **Azione**: Compila form Step 1 e clicca "Start Research"
3. **Verifica**:
   - ✅ Toast error: "Network Error" o simile
   - ✅ Rimane su Step 1
   - ✅ Bottone torna cliccabile

#### Test 3.2: Invalid Session ID
1. **Setup**: Riavvia backend
2. **Azione**: Modifica manualmente sessionId in store (DevTools)
3. **Azione**: Prova a procedere
4. **Verifica**:
   - ✅ Errore gestito gracefully
   - ✅ Toast error mostrato

#### Test 3.3: Retry Logic
1. **Setup**: Backend lento o instabile
2. **Azione**: Invia richiesta
3. **Verifica**:
   - ✅ Retry automatico (max 3 tentativi)
   - ✅ Exponential backoff

**✅ Test Passed**: Error handling robusto

---

## 📱 Test Scenario 4: Responsive Design

### Obiettivo
Testare UI su diversi dispositivi.

### Steps

#### Test 4.1: Desktop (1920x1080)
1. **Azione**: Apri in finestra full screen
2. **Verifica**:
   - ✅ Layout centrato
   - ✅ Max width container
   - ✅ Spacing adeguato

#### Test 4.2: Tablet (768x1024)
1. **Azione**: Resize browser a 768px width
2. **Verifica**:
   - ✅ Layout si adatta
   - ✅ Bottoni full width
   - ✅ Cards stack verticalmente

#### Test 4.3: Mobile (375x667)
1. **Azione**: Resize browser a 375px width
2. **Verifica**:
   - ✅ Header compatto
   - ✅ Form fields full width
   - ✅ Suggestion chips wrap
   - ✅ Stepper responsive
   - ✅ Scroll smooth

**✅ Test Passed**: Responsive su tutti i device

---

## 🎨 Test Scenario 5: UI/UX

### Obiettivo
Testare esperienza utente e animazioni.

### Steps

#### Test 5.1: Suggestion Chips
1. **Azione**: Clicca vari suggestion chips
2. **Verifica**:
   - ✅ Campo si riempie correttamente
   - ✅ Animazione smooth
   - ✅ Chip evidenziato

#### Test 5.2: Typing Indicator
1. **Azione**: Osserva typing indicator in Step 2 e 5
2. **Verifica**:
   - ✅ 3 dots animati
   - ✅ Bounce effect
   - ✅ Timing corretto (stagger)

#### Test 5.3: Progress Bar
1. **Azione**: Osserva progress bar in Step 2 e 5
2. **Verifica**:
   - ✅ Animazione smooth
   - ✅ Gradient colorato
   - ✅ Percentuale aggiornata

#### Test 5.4: Stepper
1. **Azione**: Naviga tra step
2. **Verifica**:
   - ✅ Step corrente evidenziato
   - ✅ Step completati con checkmark
   - ✅ Step futuri disabilitati

#### Test 5.5: Toast Notifications
1. **Azione**: Trigger varie azioni (copy, download, errors)
2. **Verifica**:
   - ✅ Toast appare in alto a destra
   - ✅ Auto-dismiss dopo 3s
   - ✅ Icone corrette (success, error)
   - ✅ Colori appropriati

**✅ Test Passed**: UX fluida e piacevole

---

## 🔍 Test Scenario 6: Browser DevTools

### Obiettivo
Verificare logging e debug.

### Steps

#### Test 6.1: Console Logs (Debug Mode ON)
1. **Setup**: Verifica `.env` ha `VITE_ENABLE_DEBUG_MODE=true`
2. **Azione**: Apri DevTools Console (F12)
3. **Azione**: Esegui flow completo
4. **Verifica**:
   - ✅ Log richieste API: `[API Request] POST /api/v1/onboarding/start`
   - ✅ Log risposte API: `[API Response] 200`
   - ✅ Log errori dettagliati
   - ✅ Timing informazioni

#### Test 6.2: Network Tab
1. **Azione**: Apri DevTools Network tab
2. **Azione**: Esegui flow completo
3. **Verifica**:
   - ✅ Chiamate a `http://localhost:8001/api/v1/onboarding/start`
   - ✅ Headers corretti (Content-Type, X-Request-ID)
   - ✅ Request payload corretto
   - ✅ Response status 200/201
   - ✅ Response body valido

#### Test 6.3: React DevTools
1. **Setup**: Installa React DevTools extension
2. **Azione**: Apri React DevTools
3. **Verifica**:
   - ✅ Component tree visibile
   - ✅ Props corretti
   - ✅ State aggiornato
   - ✅ No memory leaks

#### Test 6.4: Zustand DevTools
1. **Azione**: Apri Redux DevTools (compatibile con Zustand)
2. **Verifica**:
   - ✅ Store state visibile
   - ✅ Actions logged
   - ✅ Time-travel debugging funziona

**✅ Test Passed**: Debug tools funzionanti

---

## ⚡ Test Scenario 7: Performance

### Obiettivo
Verificare performance e ottimizzazioni.

### Steps

#### Test 7.1: Initial Load
1. **Azione**: Apri http://localhost:3001 (hard refresh)
2. **Verifica**:
   - ✅ First Contentful Paint < 1s
   - ✅ Time to Interactive < 2s
   - ✅ No layout shifts

#### Test 7.2: Bundle Size
1. **Azione**: `npm run build`
2. **Azione**: Controlla output
3. **Verifica**:
   - ✅ Main bundle < 500KB (gzipped)
   - ✅ Vendor chunks separati
   - ✅ Code splitting attivo

#### Test 7.3: Memory Usage
1. **Azione**: Apri DevTools Performance tab
2. **Azione**: Esegui flow completo 3 volte
3. **Verifica**:
   - ✅ No memory leaks
   - ✅ Heap size stabile
   - ✅ No excessive re-renders

**✅ Test Passed**: Performance ottimale

---

## 📊 Test Results Summary

| Scenario | Status | Notes |
|----------|--------|-------|
| 1. Happy Path | ⏳ Pending | Richiede backend attivo |
| 2. Form Validation | ⏳ Pending | Test locale |
| 3. Error Handling | ⏳ Pending | Richiede backend |
| 4. Responsive Design | ⏳ Pending | Test browser resize |
| 5. UI/UX | ⏳ Pending | Test visuale |
| 6. DevTools | ⏳ Pending | Test debug |
| 7. Performance | ⏳ Pending | Test build |

---

## 🐛 Bug Report Template

Se trovi un bug, usa questo template:

```markdown
### Bug Description
[Descrizione chiara del problema]

### Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Expected Behavior
[Cosa dovrebbe succedere]

### Actual Behavior
[Cosa succede invece]

### Screenshots
[Se applicabile]

### Environment
- Browser: [Chrome/Firefox/Safari]
- Version: [versione browser]
- OS: [Windows/Mac/Linux]
- Frontend version: [1.0.0]

### Console Errors
[Copia errori da console]

### Network Errors
[Copia errori da network tab]
```

---

## ✅ Acceptance Criteria

Il frontend è pronto per produzione quando:

- [ ] Tutti i 7 test scenarios passano
- [ ] No errori in console
- [ ] No warning in console
- [ ] Performance metrics OK
- [ ] Responsive su mobile/tablet/desktop
- [ ] Accessibilità base OK (keyboard navigation)
- [ ] Error handling robusto
- [ ] Loading states chiari
- [ ] Toast notifications funzionanti
- [ ] Backend integration OK

---

**Happy Testing! 🧪**

