TASK 3 - SIEBERT NEWSLETTER ASSEMBLY
Merge {{task1_siebert_context_setup_output}} and {{task2_perplexity_research_output}} to craft the 8-section newsletter for edition {{edition_number}}.
Follow word counts from {{target_word_count}} and assemble EXACTLY 8 sections.

HEADER & BRANDING (MANDATORY):
- Title must be "{{newsletter_title}}" (uppercase allowed). Never use "Future Millionaires".
- Edition line must be "*{{current_month_year}} Edition*".
- Greet and sign with the community name: "{{community_name}}" (do not invent alternatives).

CITATIONS (MANDATORY):
- Inline format: (Source: Outlet, Month YYYY - https://full.url) with a full URL every time.
- Apply on first occurrence of each specific fact/stat/claim; if two sources corroborate, separate with "; ".
- If a citation lacks a URL or is outside {{research_timeframe}}, replace the claim with an in-timeframe, fully-cited alternative or remove it.

DATE CONSISTENCY & TIMEFRAME ENFORCEMENT:
- Derive Month YYYY from the source itself (page metadata or URL pattern like 20250917 -> September 2025). Do not invent dates.
- If the narrative includes a month/year that conflicts with the source date or is outside {{research_timeframe}}, correct the narrative or remove the claim.
- The final draft must not contain months/years outside {{research_timeframe}} (e.g., do not include old items like "December 2024").

SOURCE POLICY:
- Prioritize ONLY the premium sources from {{siebert_target_urls}}.
- Crypto Corner must cite ONLY decrypt.co or coindesk.com.
- Section 5 (Market Insights from Malek): Use ONLY insights from the latest 3–4 Daily Market posts captured in {{task2_perplexity_research_output}} (blog.siebert.com).
- Section 5 FORMAT (mandatory):
  - Start with a 1-line hook (≤ 20 words), no quotes.
  - Then 3–4 bullets, each ≤ 22 words, each grounded in a distinct Malek post; include at least 2 inline citations across bullets.
  - No long quotes (>5 words). No extra paragraphs or filler.
  - Total length 130–165 words (prefer 140–155).
- If those posts are missing from Task 2, perform [web_search] https://blog.siebert.com/tag/daily-market#BlogListing [/web_search], retrieve the latest 3–4 posts within {{research_timeframe}}, and use them for Section 5 with inline citations.

STYLE:
- Conversational, empowering, Gen Z voice with cultural hooks; mobile-friendly (2–3 sentence paragraphs).
- Include emojis in headers and bullets where appropriate.
- Do NOT use em dashes (—); prefer commas or a simple hyphen (-).

OUTPUT:
- Complete markdown newsletter with inline citations as specified above. Do not add extra sections beyond the 8 required.
