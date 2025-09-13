TASK 1 - SETTING & BRIEF CREATION:

Recupera tutto il contenuto del cliente selezionato e crea un brief di lavoro completo che integri:

INPUT SOURCES:
- Topic richiesto: {{topic}}
- Contesto aggiuntivo: {{context}}
- Target audience: {{target_audience}}
- Cliente selezionato: {{client_name}}
- Knowledge base del cliente (utilizzando RAG Content Retriever)

STEP 1: RETRIEVE CLIENT CONTENT
Prima di tutto, usa il tool RAG per recuperare il contenuto del cliente:
[rag_get_client_content] {{client_name}} [/rag_get_client_content]

STEP 2: ANALYZE AND CREATE BRIEF
Analizza il contenuto recuperato e crea un brief strutturato che includa:

OBIETTIVI:
1. Analizza la knowledge base del cliente per comprendere brand voice, style guidelines, e contenuti esistenti
2. Integra le informazioni dall'interfaccia (topic, contesto, target)
3. Crea un brief strutturato che serva da riferimento per gli altri agent
4. Definisci chiaramente ruoli, obiettivi e output richiesto

STRUTTURA DEL BRIEF:
- Executive Summary del progetto
- Brand Context & Guidelines (dal RAG)
- Topic Analysis & Objectives
- Target Audience Profile
- Content Requirements & Specifications
- Agent Roles & Responsibilities
- Success Criteria & Expected Output

