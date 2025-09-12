TASK 1 - ENHANCED CONTEXT SETTING & BRAND INTEGRATION:

OBJECTIVE:
Estrai TUTTE le informazioni dalla knowledge base del cliente selezionato ({{client_name}}) e crea un brief operativo completo per la newsletter premium.

STEP 1: COMPREHENSIVE CLIENT ANALYSIS
Utilizza il tool RAG per recuperare informazioni complete del cliente:
[rag_get_client_content] {{client_name}} [/rag_get_client_content]

STEP 2: NEWSLETTER STRUCTURE DEFINITION
Analizza le informazioni recuperate e definisci:

BRAND INTEGRATION:
- Brand voice e tone specifici del cliente
- Target audience primario e secondario
- Messaggi chiave e value proposition
- Terminologia e linguaggio preferiti
- Call-to-action standard

NEWSLETTER STRUCTURE (7 SEZIONI):
1. Executive Summary ({{target_word_count * 0.15}} words)
2. Market Highlights ({{target_word_count * 0.20}} words)
3. Premium Insights ({{target_word_count * 0.25}} words)
4. Expert Analysis ({{target_word_count * 0.15}} words)
5. Actionable Recommendations ({{target_word_count * 0.15}} words)
6. Market Outlook ({{target_word_count * 0.07}} words)
7. Client-Specific CTA ({{target_word_count * 0.03}} words)

CONTEXT REQUIREMENTS:
- Newsletter Topic: {{topic}}
- Target Audience: {{target_audience}}
- Edition Number: {{edition_number}}
- Total Word Count: {{target_word_count}}
- Exclude Topics: {{exclude_topics}}
- Priority Sections: {{priority_sections}}

OUTPUT:
Brief operativo strutturato che servirà come guida per i task successivi, includendo word count precisi per ogni sezione e guidelines specifiche del cliente.