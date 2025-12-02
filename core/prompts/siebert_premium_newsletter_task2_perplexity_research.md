TASK 2 - PERPLEXITY RESEARCH

═══════════════════════════════════════════════════════════════════════════════
STEP 1: RUN PERPLEXITY SEARCH (PRIORITIZE OFFICIAL SOURCES)
═══════════════════════════════════════════════════════════════════════════════

Run [perplexity_search] topic={{topic}}, exclude_topics={{exclude_topics}}, premium_sources={{siebert_target_urls}}, research_timeframe={{research_timeframe}}.

APPROVED SOURCE DOMAINS (PRIORITIZE THESE IN YOUR RESEARCH):
✅ TIER 1 - OFFICIAL GOVERNMENT SOURCES (HIGHEST PRIORITY):
- Federal Reserve (federalreserve.gov) - for Fed policy, FOMC minutes, rate decisions
- Bureau of Labor Statistics (bls.gov) - for unemployment, jobs data, CPI
- Bureau of Economic Analysis (bea.gov) - for GDP, PCE inflation, personal income
- U.S. Census Bureau (census.gov) - for housing starts, retail sales
- U.S. Treasury (treasury.gov) - for Treasury yields, debt data

✅ TIER 2 - APPROVED FINANCIAL DATA PROVIDERS:
- CME FedWatch (cmegroup.com) - for Fed rate probabilities
- Conference Board (conference-board.org) - for Consumer Confidence
- Freddie Mac PMMS (freddiemac.com) - for mortgage rates
- Bankrate (bankrate.com) - for savings rates, loan rates
- Trading Economics (tradingeconomics.com) - for economic indicators

✅ TIER 3 - APPROVED NEWS OUTLETS:
- Reuters (reuters.com)
- Wall Street Journal (wsj.com)
- New York Times (nytimes.com)
- Yahoo Finance (finance.yahoo.com)
- Siebert Blog (blog.siebert.com)

═══════════════════════════════════════════════════════════════════════════════
STEP 2: COPY THE CITATIONS ARRAY (MANDATORY - DO THIS IMMEDIATELY AFTER SEARCH)
═══════════════════════════════════════════════════════════════════════════════

After Perplexity returns, locate the "citations" array in the JSON response.
COPY each URL exactly as it appears. Do not modify, shorten, or paraphrase.

EXAMPLE - Perplexity returns this JSON:
```json
{
  "citations": [
    "https://www.cbsnews.com/news/federal-reserve-december-2025-rate-cut-probability-fomc-meeting-economy/",
    "https://fortune.com/2025/11/24/stocks-fed-interest-rate-cut-december/",
    "https://www.federalreserve.gov/newsevents/pressreleases/monetary20251029a.htm"
  ]
}
```

YOUR OUTPUT MUST START WITH:
```
## PERPLEXITY CITATIONS (COPIED VERBATIM FROM JSON)
1. https://www.cbsnews.com/news/federal-reserve-december-2025-rate-cut-probability-fomc-meeting-economy/
2. https://fortune.com/2025/11/24/stocks-fed-interest-rate-cut-december/
3. https://www.federalreserve.gov/newsevents/pressreleases/monetary20251029a.htm
```

═══════════════════════════════════════════════════════════════════════════════
STEP 3: COPY THE SEARCH_RESULTS ARRAY
═══════════════════════════════════════════════════════════════════════════════

Also copy URLs from the "search_results" array:
```
## PERPLEXITY SEARCH_RESULTS (COPIED VERBATIM FROM JSON)
| Title | URL | Date |
|-------|-----|------|
| Is the Federal Reserve likely to cut... | https://www.cbsnews.com/news/federal-reserve... | 2025-11-20 |
| Stock markets: Suddenly, a Fed interest... | https://fortune.com/2025/11/24/stocks-fed... | 2025-11-24 |
```

═══════════════════════════════════════════════════════════════════════════════
STEP 4: USE ONLY THOSE URLs IN YOUR RESEARCH SUMMARY
═══════════════════════════════════════════════════════════════════════════════

When writing section summaries, EVERY source URL must come from Steps 2 or 3.

✅ CORRECT FORMAT:
"Fed rate cut probability has fluctuated from 97% to 22% based on economic data
(Source: CBS News - https://www.cbsnews.com/news/federal-reserve-december-2025-rate-cut-probability-fomc-meeting-economy/)"

❌ WRONG - This URL was NOT in the Perplexity response:
"Fed signals measured approach (Source: Reuters - https://www.reuters.com/markets/us/fed-officials...)"

═══════════════════════════════════════════════════════════════════════════════
⚠️ CRITICAL WARNING: YOU HAVE BEEN FABRICATING URLs
═══════════════════════════════════════════════════════════════════════════════

In previous runs, Perplexity returned these REAL citations:
- https://www.cbsnews.com/...
- https://fortune.com/...
- https://www.federalreserve.gov/...

But you INVENTED these FAKE URLs that were NOT in the response:
❌ https://www.reuters.com/markets/us/fed-officials-signal... (FABRICATED)
❌ https://www.cnbc.com/2024/12/19/stock-market-today... (FABRICATED)
❌ https://www.bloomberg.com/news/articles/2024-12-19/... (FABRICATED)
❌ https://blog.siebert.com/tag/daily-market/fed-policy... (FABRICATED)

These URLs look plausible but DO NOT EXIST in the Perplexity response.
This breaks the newsletter because compliance must remove unverified sources.

RULE: If a URL is not in the "citations" or "search_results" arrays, IT DOES NOT EXIST.

═══════════════════════════════════════════════════════════════════════════════
FACT INTEGRITY RULES (CRITICAL - ZERO TOLERANCE FOR FABRICATION):
═══════════════════════════════════════════════════════════════════════════════

1. DO NOT INVENT FEDERAL RESERVE OFFICIALS OR QUOTES:
   - NEVER fabricate names of Fed officials (e.g., "Vice Chair Sarah Bloom Raskin" - she is NOT Vice Chair)
   - NEVER attribute statements to Fed officials unless from official Fed press releases
   - NEVER claim any Fed official "signaled" or "indicated" future policy
   - The Fed NEVER pre-announces policy decisions
   - ONLY use quotes from federalreserve.gov official statements

2. DO NOT INVENT MARKET STATISTICS:
   - ALL specific percentages, dollar amounts, and data points MUST have a primary source URL
   - NO inventing: yield levels, S&P movements, bond prices, ETF flows, mortgage rates
   - CME FedWatch probabilities: ONLY cite if you have the EXACT URL from CME Group
   - Treasury yields: ONLY from treasury.gov or Reuters with URL
   - Mortgage rates: ONLY from Freddie Mac PMMS with URL
   - Stock movements: ONLY from Reuters/Bloomberg with URL

3. DO NOT INVENT CALCULATIONS OR PROJECTIONS:
   - NO "Bonds gained $X per $100,000 investment" - this is projection
   - NO hypothetical investment returns
   - NO performance inferences

4. URL INTEGRITY (CRITICAL - READ THIS CAREFULLY):
   - ONLY USE URLs THAT APPEAR IN THE PERPLEXITY JSON RESPONSE
   - Check the "citations" array - those are the ONLY valid URLs
   - Check the "search_results" array "url" fields - those are also valid
   - DO NOT INVENT URLs that "look right" for Reuters, Bloomberg, CNBC, WSJ
   - DO NOT CONSTRUCT URLs based on article titles you imagine
   - If a source is not in the Perplexity response, IT DOES NOT EXIST
   - For blog.siebert.com: ONLY use URLs from actual Perplexity results
   - If no Siebert URLs returned: "No verified Siebert blog posts found"

5. MALEK QUOTES - STRICT RULES:
   - DO NOT invent quotes from Mark Malek or any Siebert analyst
   - ONLY use verbatim quotes from actual blog.siebert.com URLs returned by Perplexity
   - If no Siebert blog URLs found, state: "No Malek quotes available - use general educational framing"
   - NEVER fabricate phrases like "Rate environment transitions require..."

═══════════════════════════════════════════════════════════════════════════════
DATE VALIDATION (MANDATORY - DO THIS FIRST):
═══════════════════════════════════════════════════════════════════════════════

1. For EVERY article, verify the publication date BEFORE including it.
2. Extract date from: page metadata, article byline, URL pattern (e.g., /2025/11/27/ or 20251127).
3. If date cannot be verified → EXCLUDE the article. Do NOT guess dates.
4. If date is outside {{research_timeframe}} → EXCLUDE immediately. No exceptions.
5. Only proceed with articles that pass date validation.

Organize findings by newsletter section with cited statistics, dates, and Gen Z relevance.

For EACH validated item include: Title - URL (Month YYYY).

Special rules:
- Result selection (CRITICAL):
  - Use article/detail pages only; avoid tag/listing/category pages.
  - Prefer primary sources for policy actions; for Fed decisions include the Federal Reserve press release.
  - Each item MUST have a specific headline AND explicit publish date on-page.
- Section 4 (By the numbers): provide 3–5 stats with inline-ready citations, all within {{research_timeframe}}.
- Section 5 (Market Insights from Malek):
  - ONLY include blog.siebert.com URLs that Perplexity actually returned.
  - If Perplexity found no Siebert blog posts, output: "No verified Siebert blog URLs available. Use general Siebert educational perspective without specific citations."
  - DO NOT fabricate URLs like "/tag/daily-market/fed-watch-december-2025"
- Crypto Corner: restrict to https://decrypt.co/ and https://www.coindesk.com/.

REQUIRED OUTPUT SECTIONS:

1. **PERPLEXITY CITATIONS RECEIVED** (mandatory, place at top):
   List the EXACT URLs from the Perplexity response "citations" array:
   ```
   CITATIONS FROM PERPLEXITY:
   1. [exact URL from citations array]
   2. [exact URL from citations array]
   ...
   ```
   This proves you are using real URLs, not fabricated ones.

2. **DATE VALIDATION TABLE** (mandatory):
   | Title | URL | Published Date | Within Timeframe |
   |-------|-----|----------------|------------------|
   IMPORTANT: The URL column MUST contain ONLY URLs from the PERPLEXITY CITATIONS above.
   If a URL is not in the citations list, DO NOT include it in this table.

3. **SOURCES USED** (deduplicated list):
   Title - URL (Month YYYY)
   ALL URLs must match exactly with the PERPLEXITY CITATIONS section above.

4. **SIEBERT BLOG STATUS**:
   - If Perplexity returned blog.siebert.com URLs: list them
   - If not: "No verified Siebert blog URLs found. Downstream tasks should use general educational framing."

5. **RESEARCH SUMMARY BY SECTION**:
   Use ONLY information from the URLs listed in PERPLEXITY CITATIONS.
   DO NOT add information from sources not in the Perplexity response.
