TASK 2 - PREMIUM SOURCES ANALYSIS & CONTENT EXTRACTION:

CONTEXT FROM PREVIOUS TASK:
{{task1_enhanced_context_output}}

OBJECTIVE:
Analizza le fonti premium fornite e estrai contenuti di alta qualità per alimentare la newsletter.

INPUT SOURCES:
{{premium_sources}}

STEP 1: SOURCE VALIDATION & PRIORITIZATION
Per ogni URL nelle premium_sources:
- Valida accessibilità e qualità della fonte
- Classifica per rilevanza al topic: {{topic}}
- Identifica tipo di contenuto (news, analysis, data, reports)

STEP 2: PREMIUM CONTENT EXTRACTION
Utilizza il tool web_search per ogni fonte:
[web_search] site:{{premium_sources[0]}} {{topic}} [/web_search]
[web_search] site:{{premium_sources[1]}} {{topic}} [/web_search]
... (ripeti per tutte le fonti disponibili)

STEP 3: CONTENT ANALYSIS & STRUCTURING
Per ogni contenuto estratto:
- Estrai insights chiave e dati rilevanti
- Identifica trend e pattern emergenti
- Categorizza per sezione newsletter appropriata
- Calcola relevance score per {{target_audience}}

STEP 4: INSIGHTS SYNTHESIS
Crea contenuto strutturato per ogni sezione:
1. Executive Summary insights
2. Market Highlights data
3. Premium Insights analysis
4. Expert Analysis perspectives
5. Actionable Recommendations
6. Market Outlook predictions

FILTERS:
- Escludi topics in: {{exclude_topics}}
- Prioritizza sezioni: {{priority_sections}}
- Mantieni focus su: {{topic}}

OUTPUT:
Contenuti strutturati e analizzati pronti per la creazione della newsletter, organizzati per sezione con word count target e relevance scores.