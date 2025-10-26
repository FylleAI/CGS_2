# FASE 3: Piano di Azione Dettagliato - Code Migration

## 📋 Obiettivo
Completare la migrazione da `core/` + `onboarding/` a `services/` con shared contracts in `packages/contracts/`.

## 🎯 Struttura Target

```
services/
├── content_workflow/     (ex core/)
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   └── prompts/
├── card_service/
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   └── api/
└── onboarding/
    ├── domain/
    ├── application/
    ├── infrastructure/
    └── api/

frontends/
├── card-explorer/        (ex card-frontend/)
└── cgs-console/
    └── react-app/        (ex web/react-app/)

packages/
└── contracts/            (shared models)
    ├── __init__.py
    ├── company_snapshot.py
    ├── card_summary.py
    └── workflow_context.py
```

## 📝 Step-by-Step Plan

### STEP 1: Creare directory structure
- [ ] Creare `services/` directory
- [ ] Creare `services/content_workflow/`
- [ ] Creare `services/card_service/`
- [ ] Creare `services/onboarding/`
- [ ] Creare `frontends/` directory
- [ ] Creare `frontends/card-explorer/`
- [ ] Creare `frontends/cgs-console/`
- [ ] Creare `packages/contracts/`

### STEP 2: Migrare Card Service
- [ ] Copiare `core/card_service/` → `services/card_service/`
- [ ] Aggiornare import in `services/card_service/`
- [ ] Aggiornare `api/rest/main.py` per importare da `services/card_service/`

### STEP 3: Migrare Onboarding
- [ ] Copiare `onboarding/` → `services/onboarding/`
- [ ] Aggiornare import in `services/onboarding/`
- [ ] Aggiornare `api/rest/main.py` per importare da `services/onboarding/`

### STEP 4: Migrare Content Workflow
- [ ] Copiare `core/` (escludendo `card_service/`) → `services/content_workflow/`
- [ ] Aggiornare import in `services/content_workflow/`
- [ ] Aggiornare `api/rest/main.py` per importare da `services/content_workflow/`

### STEP 5: Creare Shared Contracts
- [ ] Creare `packages/contracts/company_snapshot.py`
- [ ] Creare `packages/contracts/card_summary.py`
- [ ] Creare `packages/contracts/workflow_context.py`
- [ ] Aggiornare import in tutti i servizi

### STEP 6: Migrare Frontends
- [ ] Spostare `card-frontend/` → `frontends/card-explorer/`
- [ ] Spostare `web/react-app/` → `frontends/cgs-console/react-app/`
- [ ] Aggiornare API URLs nei frontend

### STEP 7: Aggiornare Main API
- [ ] Aggiornare `api/rest/main.py` per importare da `services/`
- [ ] Aggiornare `api/rest/v1/dependencies.py`
- [ ] Aggiornare tutti gli endpoint

### STEP 8: Aggiornare Tests
- [ ] Aggiornare import in `tests/`
- [ ] Eseguire test suite completa
- [ ] Verificare che tutti i test passano

### STEP 9: Cleanup
- [ ] Rimuovere `core/` directory
- [ ] Rimuovere `onboarding/` directory (se non usato altrove)
- [ ] Rimuovere `card-frontend/` directory
- [ ] Rimuovere `web/` directory (se non usato altrove)
- [ ] Aggiornare `.gitignore`

### STEP 10: Commit e Push
- [ ] Commit della migrazione
- [ ] Push a `feature/card-service-v1`
- [ ] Preparare PR per merge

## ⚠️ Considerazioni Importanti

1. **Backward Compatibility**: Mantenere compatibility shim per payload legacy
2. **Import Updates**: Aggiornare TUTTI gli import in modo sistematico
3. **Test Coverage**: Eseguire test suite completa dopo ogni step
4. **Documentation**: Aggiornare README e docs
5. **Gradual Migration**: Fare step piccoli e testabili

## 🔄 Flusso di Lavoro Consigliato

1. Creare directory structure
2. Copiare file (non eliminare ancora)
3. Aggiornare import
4. Eseguire test
5. Se tutto passa, eliminare vecchie directory
6. Commit finale

## 📊 Stima Tempo

- STEP 1-2: 30 min
- STEP 3-4: 1 ora
- STEP 5: 30 min
- STEP 6: 30 min
- STEP 7-8: 1 ora
- STEP 9-10: 30 min

**TOTALE: ~4 ore**

