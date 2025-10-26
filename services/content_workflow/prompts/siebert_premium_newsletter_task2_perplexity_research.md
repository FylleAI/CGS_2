TASK 2 - PERPLEXITY RESEARCH
Run [perplexity_search] topic={{topic}}, exclude_topics={{exclude_topics}}, premium_sources={{siebert_target_urls}}, research_timeframe={{research_timeframe}}.
Use ONLY the listed premium sources ({{siebert_target_urls}}). Reject other outlets unless absolutely necessary.
Organize findings by newsletter section with cited statistics, dates, and Gen Z relevance.
Strict date handling:
- For each item, extract the publication date from the page metadata. If unavailable, infer from the URL pattern (e.g., 20250917 -> September 2025).
- Do NOT invent dates. If the date cannot be determined, mark as Unknown and exclude the item from findings.
- Include only items whose date falls within {{research_timeframe}}. HARD STOP: discard anything older than {{research_timeframe}} (e.g., months from prior years).
- The edition month should align with {{current_month_year}}; items must be recent within the timeframe.
For EACH item include: Title - URL (Month YYYY). Keep data within {{research_timeframe}}.
Special rules:
- Result selection rules (CRITICAL for correctness):
  - Use article/detail pages only; avoid tag/listing/category pages.
  - Prefer primary sources for policy actions; for Fed decisions include the Federal Reserve press release when available.
  - Ensure each item has a specific headline and explicit publish date on-page.
- Section 4 (By the numbers): provide 3–5 stats with inline-ready citations.
- Section 5 (Market Insights from Malek): From https://blog.siebert.com/tag/daily-market#BlogListing, retrieve the latest 3–4 "Daily Market" posts within {{research_timeframe}}. For each: Title - URL (Month YYYY). Then produce a concise "Malek Insights Brief" as 3–4 bullets (each ≤ 22 words), grounded ONLY in those posts, with inline-ready citations (include at least 2 distinct Malek sources).
- Crypto Corner: restrict to https://decrypt.co/ and https://www.coindesk.com/.
At the end, add:
- A "DATE VALIDATION" list with one line per item: Title | URL | Published Month YYYY | within timeframe: yes/no (include only "yes" items in the main content).
- A deduplicated "SOURCES USED" list (Title - URL), 5–12 items.
