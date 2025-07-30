# Checklist Completa: Creazione Nuovo Workflow CGSRef

**Data**: 2025-07-27  
**Versione**: 1.0  
**Sistema**: CGSRef Content Generation

---

## 📋 Panoramica del Processo

Per creare un nuovo workflow nel sistema CGSRef sono necessari **7 passi principali**:

1. **Definizione Workflow** - Pianificazione e design
2. **Backend Implementation** - Handler, template, registrazione
3. **Frontend Configuration** - API service, form, validazione
4. **Testing** - Verifica funzionamento end-to-end
5. **Documentation** - Documentazione del nuovo workflow
6. **Deployment** - Deploy e monitoraggio
7. **Maintenance** - Manutenzione e ottimizzazioni

---

## 🎯 STEP 1: Definizione Workflow

### ✅ 1.1 Pianificazione
- [ ] **Nome workflow**: Definire nome univoco (es: `social_media_post`)
- [ ] **Categoria**: Scegliere categoria (`article`, `newsletter`, `social`, `custom`)
- [ ] **Descrizione**: Scrivere descrizione chiara e concisa
- [ ] **Target audience**: Definire pubblico di riferimento
- [ ] **Obiettivi**: Definire cosa deve produrre il workflow

### ✅ 1.2 Design Task Flow
- [ ] **Task 1**: Definire primo task (es: Brief Creation)
- [ ] **Task 2**: Definire secondo task (es: Research)
- [ ] **Task 3**: Definire task finale (es: Content Creation)
- [ ] **Agenti**: Scegliere agenti per ogni task (`rag_specialist`, `copywriter`, etc.)
- [ ] **Dipendenze**: Definire dipendenze tra task

### ✅ 1.3 Definizione Variabili
- [ ] **Variabili Required**: Elencare campi obbligatori
- [ ] **Variabili Optional**: Elencare campi opzionali
- [ ] **Tipi di dato**: Definire tipi (`string`, `number`, `boolean`, etc.)
- [ ] **Validazioni**: Definire regole di validazione
- [ ] **Valori default**: Definire valori predefiniti

---

## 🔧 STEP 2: Backend Implementation

### ✅ 2.1 Creazione Handler
**File**: `core/infrastructure/workflows/handlers/{nome_workflow}_handler.py`

```python
"""
{Nome Workflow} workflow handler.
"""

import logging
from typing import Dict, Any

from ..base.workflow_base import WorkflowHandler
from ..registry import register_workflow

logger = logging.getLogger(__name__)

@register_workflow('{nome_workflow}')
class {NomeWorkflow}Handler(WorkflowHandler):
    """Handler for {nome_workflow} workflow."""
    
    def validate_inputs(self, context: Dict[str, Any]) -> None:
        """Validate inputs specific to {nome_workflow}."""
        super().validate_inputs(context)
        # Aggiungi validazioni specifiche
        
    def prepare_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for {nome_workflow}."""
        context = super().prepare_context(context)
        # Aggiungi preparazioni specifiche
        return context
        
    def post_process_task(self, task_id: str, task_output: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Post-process task output."""
        # Aggiungi post-processing per ogni task
        return context
        
    def post_process_workflow(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Final post-processing."""
        try:
            # Aggiungi post-processing finale specifico del workflow

            # CRITICAL: Always call parent method to preserve workflow_metrics
            context = super().post_process_workflow(context)
            logger.info("✅ Parent post-processing completed - workflow_metrics preserved")

            return context
        except Exception as e:
            logger.error(f"❌ POST-PROCESSING ERROR: {str(e)}")
            # Even in case of error, call parent to preserve workflow_metrics
            return super().post_process_workflow(context)
```

**Checklist Handler**:
- [ ] Creare file handler
- [ ] Implementare `validate_inputs()`
- [ ] Implementare `prepare_context()`
- [ ] Implementare `post_process_task()`
- [ ] Implementare `post_process_workflow()`
- [ ] Aggiungere logging appropriato
- [ ] Testare sintassi Python

### ✅ 2.2 Creazione Template JSON
**File**: `core/infrastructure/workflows/templates/{nome_workflow}.json`

```json
{
  "name": "{nome_workflow}",
  "version": "1.0",
  "description": "Descrizione del workflow",
  "handler": "{nome_workflow}_handler",
  "variables": [
    {
      "name": "campo_required",
      "type": "string",
      "required": true,
      "description": "Descrizione campo"
    },
    {
      "name": "campo_optional",
      "type": "boolean",
      "required": false,
      "default": false,
      "description": "Descrizione campo opzionale"
    }
  ],
  "tasks": [
    {
      "id": "task1_nome",
      "name": "Nome Task 1",
      "agent": "rag_specialist",
      "description_template": "Template del task con {{variabili}}",
      "dependencies": []
    },
    {
      "id": "task2_nome",
      "name": "Nome Task 2", 
      "agent": "copywriter",
      "description_template": "Template del task 2",
      "dependencies": ["task1_nome"]
    }
  ]
}
```

**Checklist Template**:
- [ ] Creare file JSON
- [ ] Definire metadata (name, version, description)
- [ ] Definire tutte le variabili con tipi e validazioni
- [ ] Definire tutti i task con agenti e dipendenze
- [ ] Scrivere description_template con placeholder {{variabili}}
- [ ] Validare sintassi JSON

### ✅ 2.3 Registrazione Handler
**File**: `core/infrastructure/workflows/handlers/__init__.py`
```python
from .{nome_workflow}_handler import {NomeWorkflow}Handler

__all__ = ['EnhancedArticleHandler', '{NomeWorkflow}Handler']
```

**File**: `core/infrastructure/workflows/__init__.py`
```python
from .handlers.{nome_workflow}_handler import {NomeWorkflow}Handler
```

**Checklist Registrazione**:
- [ ] Aggiungere import in `handlers/__init__.py`
- [ ] Aggiungere import in `workflows/__init__.py`
- [ ] Verificare auto-registrazione con decorator

---

## 🎨 STEP 3: Frontend Configuration

### ✅ 3.1 API Service Configuration
**File**: `web/react-app/src/services/api.ts`

Aggiungere in `getWorkflowTypes()`:
```typescript
{
  id: '{nome_workflow}',
  name: '{nome_workflow}',
  displayName: 'Nome Display',
  description: 'Descrizione per UI',
  category: 'article', // o 'newsletter', 'social', 'custom'
  requiredFields: [
    {
      id: 'campo_required',
      name: 'campo_required',
      label: 'Label Campo',
      type: 'text', // 'text', 'textarea', 'number', 'boolean', 'select'
      required: true,
      placeholder: 'Placeholder text'
    }
  ],
  optionalFields: [
    {
      id: 'campo_optional',
      name: 'campo_optional', 
      label: 'Label Campo Opzionale',
      type: 'boolean',
      required: false
    }
  ]
}
```

**Checklist API Service**:
- [ ] Aggiungere workflow in `getWorkflowTypes()`
- [ ] Definire tutti i required fields
- [ ] Definire tutti gli optional fields
- [ ] Scegliere tipi di campo appropriati
- [ ] Aggiungere placeholder e label

### ✅ 3.2 Form Schema e Validation
**File**: `web/react-app/src/components/WorkflowForm.tsx`

```typescript
// Schema di validazione
const {nomeWorkflow}Schema = yup.object({
  campo_required: yup
    .string()
    .required('Campo obbligatorio')
    .min(3, 'Minimo 3 caratteri'),
  campo_optional: yup.boolean().optional(),
});

// Type definition
type {NomeWorkflow}FormData = {
  campo_required: string;
  campo_optional?: boolean;
};
```

**Checklist Form Schema**:
- [ ] Creare schema Yup per validazione
- [ ] Definire type TypeScript per form data
- [ ] Aggiungere validazioni appropriate (min, max, pattern)
- [ ] Testare validazioni

### ✅ 3.3 Form Rendering
**File**: `web/react-app/src/components/WorkflowForm.tsx`

```typescript
// Aggiungere in getValidationSchema()
if (selectedWorkflow?.id === '{nome_workflow}') {
  return {nomeWorkflow}Schema;
}

// Aggiungere in getDefaultValues()
if (selectedWorkflow?.id === '{nome_workflow}') {
  return {
    campo_required: '',
    campo_optional: false,
  };
}

// Aggiungere render function
const render{NomeWorkflow}Form = () => (
  <Box>
    {/* Form fields */}
  </Box>
);

// Aggiungere in return statement
{selectedWorkflow.id === '{nome_workflow}' && render{NomeWorkflow}Form()}
```

**Checklist Form Rendering**:
- [ ] Aggiungere schema in `getValidationSchema()`
- [ ] Aggiungere default values in `getDefaultValues()`
- [ ] Creare render function per il form
- [ ] Aggiungere conditional rendering nel return
- [ ] Implementare tutti i field types necessari
- [ ] Aggiungere error handling e validation messages

---

## 🧪 STEP 4: Testing

### ✅ 4.1 Backend Testing
- [ ] **Syntax Check**: Verificare sintassi Python
- [ ] **Import Test**: Verificare import e registrazione
- [ ] **Handler Test**: Testare metodi del handler
- [ ] **Template Test**: Validare JSON template
- [ ] **Registry Test**: Verificare registrazione nel registry

### ✅ 4.2 Frontend Testing
- [ ] **Compilation**: Verificare compilazione TypeScript
- [ ] **Form Rendering**: Testare rendering del form
- [ ] **Validation**: Testare validazioni form
- [ ] **API Integration**: Testare integrazione con API
- [ ] **UI/UX**: Verificare esperienza utente

### ✅ 4.3 End-to-End Testing
- [ ] **Workflow Selection**: Testare selezione workflow
- [ ] **Form Submission**: Testare invio form
- [ ] **Content Generation**: Testare generazione contenuto
- [ ] **Error Handling**: Testare gestione errori
- [ ] **Performance**: Verificare performance

---

## 📚 STEP 5: Documentation

### ✅ 5.1 Technical Documentation
- [ ] **Handler Documentation**: Documentare metodi e logica
- [ ] **Template Documentation**: Documentare struttura template
- [ ] **API Documentation**: Documentare endpoint e parametri
- [ ] **Form Documentation**: Documentare campi e validazioni

### ✅ 5.2 User Documentation
- [ ] **Workflow Guide**: Creare guida utente
- [ ] **Field Descriptions**: Documentare tutti i campi
- [ ] **Examples**: Fornire esempi di utilizzo
- [ ] **Best Practices**: Documentare best practices

---

## 🚀 STEP 6: Deployment

### ✅ 6.1 Pre-Deployment
- [ ] **Code Review**: Review del codice
- [ ] **Testing**: Test completi
- [ ] **Documentation**: Documentazione completa
- [ ] **Backup**: Backup del sistema esistente

### ✅ 6.2 Deployment
- [ ] **Backend Deploy**: Deploy modifiche backend
- [ ] **Frontend Deploy**: Deploy modifiche frontend
- [ ] **Verification**: Verificare deployment
- [ ] **Monitoring**: Monitorare sistema

---

## 🔧 STEP 7: Maintenance

### ✅ 7.1 Post-Deployment
- [ ] **Monitoring**: Monitorare performance e errori
- [ ] **User Feedback**: Raccogliere feedback utenti
- [ ] **Bug Fixes**: Correggere eventuali bug
- [ ] **Optimizations**: Implementare ottimizzazioni

### ✅ 7.2 Long-term Maintenance
- [ ] **Updates**: Aggiornamenti periodici
- [ ] **Feature Enhancements**: Miglioramenti funzionalità
- [ ] **Performance Tuning**: Ottimizzazioni performance
- [ ] **Documentation Updates**: Aggiornamenti documentazione

---

## 📝 Template Files Summary

### Backend Files da Creare:
1. `core/infrastructure/workflows/handlers/{nome_workflow}_handler.py`
2. `core/infrastructure/workflows/templates/{nome_workflow}.json`

### Backend Files da Modificare:
1. `core/infrastructure/workflows/handlers/__init__.py`
2. `core/infrastructure/workflows/__init__.py`

### Frontend Files da Modificare:
1. `web/react-app/src/services/api.ts`
2. `web/react-app/src/components/WorkflowForm.tsx`

### Files Automatici (non richiedono modifiche):
1. `api/rest/v1/endpoints/workflows.py` (già gestisce dinamicamente)
2. `web/react-app/src/components/WorkflowSelector.tsx` (già dinamico)
3. `web/react-app/src/types/index.ts` (tipi già definiti)

---

**Checklist Status**: ✅ COMPLETA
**Pronto per implementazione**: ✅ SÌ

---

## 📋 RIFERIMENTO RAPIDO: Premium Newsletter Workflow

Per il workflow Premium Newsletter specifico, consultare il file dedicato:
`PREMIUM_NEWSLETTER_IMPLEMENTATION_GUIDE.md`

Questo file contiene:
- Pianificazione dettagliata del workflow premium_newsletter
- Specifiche tecniche complete
- Vincoli di sicurezza e procedure di rollback
- Checklist di implementazione step-by-step
- Prompt pronto per l'agent di implementazione
