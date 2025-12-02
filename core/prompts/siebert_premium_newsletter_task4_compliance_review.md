TASK 4 - SIEBERT COMPLIANCE REVIEW

═══════════════════════════════════════════════════════════════════════════════
⚠️ STEP 1: URL VERIFICATION (CRITICAL - USE VERIFIED LIST BELOW)
═══════════════════════════════════════════════════════════════════════════════

{{perplexity_verified_urls_formatted}}

THE URLs ABOVE WERE EXTRACTED PROGRAMMATICALLY FROM PERPLEXITY'S API RESPONSE.
THESE ARE THE ONLY VALID URLs. ANY URL NOT IN THIS LIST IS FABRICATED.

INPUTS TO CHECK:
- The VERIFIED URL list above (extracted programmatically - authoritative source)
- {{task3_newsletter_assembly_output}} contains the newsletter with citations

VERIFICATION PROCESS:

1. FOR EACH URL in the newsletter (Task 3 output):
   ✅ If URL appears in the VERIFIED list above → KEEP the citation WITH the URL
   ❌ If URL does NOT appear in the VERIFIED list above → FABRICATED → REMOVE the claim

2. VALID URLs MUST BE PRESERVED WITH CLICKABLE LINKS:
   - Keep the full URL path (not truncated)
   - Keep the (Source: Outlet, Month YYYY - https://full.url) format
   - These links WILL become clickable <a href="..."> tags in the final HTML email

COMMON FABRICATED URL PATTERNS (REMOVE IF NOT IN VERIFIED LIST):
- reuters.com/markets/us/... URLs not in verified list
- cnbc.com/2024/... URLs not in verified list
- bloomberg.com/news/articles/... URLs not in verified list
- wsj.com/articles/... URLs not in verified list
- marketwatch.com/story/... URLs not in verified list
- blog.siebert.com/tag/daily-market/... URLs not in verified list

If a URL looks plausible but is NOT in the VERIFIED list above, it is FABRICATED.
REMOVE the entire claim that uses a fabricated URL.
KEEP claims that have VERIFIED URLs from the list above - these will be clickable links!

═══════════════════════════════════════════════════════════════════════════════

TIMEFRAME VALIDATION:
- Current date: {{current_date}}
- Allowed timeframe: {{research_timeframe}}
- Scan the ENTIRE newsletter for any dates/months outside {{research_timeframe}}.
- If found: REMOVE that content entirely or replace with in-timeframe alternatives.

Review {{task3_newsletter_assembly_output}} for FINRA Rule 2210 and SEC compliance.

===============================================================================
FACT FABRICATION CHECK (CRITICAL - ZERO TOLERANCE):
===============================================================================

FEDERAL RESERVE OFFICIALS - VERIFY OR REMOVE:
- If ANY Fed official is named, verify they are a REAL current official
- Current Fed Chair: Jerome Powell (only use if from official source)
- REMOVE any invented official names (e.g., "Vice Chair Sarah Bloom Raskin" - she is NOT Vice Chair)
- REMOVE any claims that Fed officials "signaled" or "indicated" future policy
- The Fed NEVER pre-announces policy decisions - remove such claims

MARKET STATISTICS - VERIFY OR REMOVE:
- ALL specific percentages MUST have a source URL
- REMOVE: "X% probability of rate cut" without CME FedWatch URL
- REMOVE: "Bonds gained $X per $100,000" (projection - non-compliant)
- REMOVE: Treasury yield levels without treasury.gov/Reuters URL
- REMOVE: Mortgage rate claims without Freddie Mac PMMS URL
- If no URL provided for a statistic, REMOVE the statistic

MALEK QUOTES - VERIFY OR REMOVE:
- ONLY allow Malek quotes if they have a verified blog.siebert.com URL
- REMOVE any invented quotes like "Rate environment transitions require..."
- If no verified Siebert URL, replace with: "According to Siebert's educational resources..."

HYPE/SENSATIONAL LANGUAGE - REMOVE:
- "rate cut season" - REMOVE
- "market grooves" - REMOVE
- "this is where it gets interesting" - REMOVE
- "represents real money" - REMOVE
- "accumulation conditions" - REMOVE
- "creates rotation opportunities" - REMOVE
- "rewards patience over reaction" - REMOVE (advisory)

===============================================================================
STRUCTURE VALIDATION (MANDATORY):
===============================================================================

REQUIRED SECTIONS (EXACTLY 8):
1. Intro Greeting (50-60 words)
2. Feature Story (280-320 words) - MUST have 3+ inline citations
3. Market Reality Check (200-250 words) - MUST have 2+ inline citations
4. By The Numbers (120-150 words) - MUST have 1+ inline citation
5. Market Insights from Malek (130-165 words) - Educational perspective
6. Your Move This Week (150-180 words) - Educational framing, not imperatives
7. Quick Links (70 words) - LIST OF 4-6 SOURCE LINKS USED IN THE NEWSLETTER
8. Sign-off (30-40 words)

QUICK LINKS SECTION FORMAT (MANDATORY - DO NOT DELETE):
The Quick Links section MUST contain clickable source references.
Format each link as: [Source Name](URL)
Example:
📎 Quick Links
- [Federal Reserve Press Release](https://www.federalreserve.gov/newsevents/...)
- [BLS Employment Report](https://www.bls.gov/news.release/...)
- [Treasury Department](https://home.treasury.gov/...)

FORBIDDEN SECTIONS (REMOVE IF PRESENT):
- Reader Spotlight / Community Wins / Community Stories - DELETE ENTIRELY
- P.S. lines or postscripts - DELETE ENTIRELY
- "Your Turn" engagement prompts - DELETE ENTIRELY
- Any section beyond the 8 required - DELETE ENTIRELY

===============================================================================
BANNED PHRASE SCANNER (FIND AND REPLACE):
===============================================================================

SCAN FOR AND REMOVE/REPLACE THESE EXACT PHRASES:

PROMOTIONAL LANGUAGE:
- "this could be your moment" - REMOVE entire sentence
- "your investment opportunity" - REPLACE with "current market developments"
- "portfolio opportunity" / "portfolio opportunities" - REPLACE with "market conditions"
- "significant opportunities" - REPLACE with "notable developments"
- "creating opportunities" - REPLACE with "creating conditions"
- "get paid to participate" - REMOVE entire sentence
- "profit-taking" - REPLACE with "position adjustments"
- "enhance your investment strategy" - REMOVE entire sentence
- "portfolio optimization moment" - REMOVE entire sentence
- "entry opportunities" - REPLACE with "market conditions"
- "buying opportunities" - REPLACE with "market conditions"

IMPERATIVE/ADVISORY:
- "Review your..." - REPLACE with "Some investors review their..."
- "Increase your..." - REPLACE with "Some consider increasing..."
- "Evaluate your..." - REPLACE with "Some evaluate their..."
- "Consider this a..." - REMOVE if implying action
- "Lock in rates" - REPLACE with "Current rates are..."
- "Secure rates before" - REMOVE entire sentence
- "Use volatility" - REPLACE with "During volatility, some..."
- "Use this moment" - REMOVE entire sentence
- "should just start investing" - REMOVE entire sentence
- "Can finally enter the market" - REPLACE with "may have more options"

PREDICTIVE LANGUAGE:
- "lower rates will benefit" - REPLACE with "lower rates have historically been associated with"
- "rates may benefit growth stocks" - REPLACE with "rate changes can affect different sectors"
- "creates refinancing opportunities" - REPLACE with "affects refinancing conditions"
- "historically benefits younger investors" - REMOVE the word "benefits"
- "markets pricing in" - REPLACE with "market expectations suggest"

CASUAL/SLANG LANGUAGE (HIGH PRIORITY - REMOVE ALL):
- "we're here for it" - REMOVE entire sentence
- "main character energy" - REMOVE entire phrase
- "giving X energy" - REMOVE entire phrase
- "plot twists" / "financial plot twists" - REPLACE with "developments"
- "smart money is" / "smart money doing" - REPLACE with "some market participants are"
- "better safe than sorry" - REMOVE entire phrase
- "opened doors for" - REPLACE with "created conditions for"
- "soft launch" - REMOVE or REPLACE with neutral language
- "emotional whiplash" - REPLACE with "significant movement"
- "hot take" - REMOVE entirely
- "lowkey" / "highkey" - REMOVE entirely
- "basically" - REMOVE when used casually
- "honestly" - REMOVE when used casually
- "serving up" - REMOVE and rephrase
- "here for it" - REMOVE entirely
- Any TikTok/internet slang - REMOVE and rephrase professionally

SENSATIONAL LANGUAGE:
- "significant portfolio opportunities" - REPLACE with "market developments"
- "your moment to enhance" - REMOVE entire sentence
- "sophisticated portfolio diversification" - REPLACE with "diversification strategies"
- "take a X approach" - REPLACE with "consider X as one option"
- Any exclamation marks (!) - REPLACE with periods

===============================================================================
EMOJI COMPLIANCE:
===============================================================================

ALLOWED LOCATIONS:
- Section headers (e.g., "📈 Feature Story")
- Opening greeting line only ("👋 Hey Wealthbuilders,")
- Sign-off line ("✨ Stay Empowered and Keep Building,")

FORBIDDEN LOCATIONS (REMOVE):
- Mid-paragraph emojis
- Bullet point emojis at start of bullets
- Inline emojis within sentences

BULLET POINT FORMAT:
- Use simple dot character for all bullets, NOT emoji bullets
- Remove any emoji at the start of bullet points

===============================================================================
ADDRESS CONSISTENCY:
===============================================================================

FIND AND STANDARDIZE:
- "Future Millionaires" - REPLACE with "Wealthbuilders"
- "The Future Millionaires Community" - REPLACE with "The Wealthbuilder Team"
- "Future Wealth Builders" - REPLACE with "Wealthbuilders"
- Use "Wealthbuilders" as the ONLY community name throughout

===============================================================================
SECTION 6 (YOUR MOVE) COMPLIANCE CHECK:
===============================================================================

VERIFY FORMAT:
- Action items must be framed as educational considerations, NOT instructions
- Each item must start with "Some investors..." or "One approach..." or similar

NON-COMPLIANT to COMPLIANT TRANSFORMATIONS:
- "Review your emergency fund" becomes "Some investors review emergency fund allocations"
- "Increase systematic investing" becomes "Dollar-cost averaging is one approach during volatility"
- "Evaluate bond duration" becomes "Bond duration is a factor some consider"
- "Lock in current rates" becomes "Current high-yield savings rates remain available"

===============================================================================
SECTION 7 (QUICK LINKS) COMPLIANCE CHECK:
===============================================================================

REQUIRED FORMAT:
📎 Quick Links
- [Source Name 1](URL1)
- [Source Name 2](URL2)
- [Source Name 3](URL3)
- [Source Name 4](URL4)

REQUIREMENTS:
- MUST contain 4-6 clickable links
- Links MUST be from the VERIFIED URL list at the top of this prompt
- Each link should use markdown format: [Display Name](Full URL)
- Prioritize Tier 1 (government) and Tier 2 (financial data) sources

===============================================================================
SECTION 8 (SIGN-OFF) COMPLIANCE CHECK:
===============================================================================

REQUIRED FORMAT (EXACTLY):
✨ Stay Empowered and Keep Building,
The Wealthbuilder Team

REMOVE IF PRESENT:
- Any P.S. line
- Any additional sentences after signature

===============================================================================
CITATION & TIMEFRAME CHECKS:
===============================================================================

- Every inline citation must include Month YYYY matching the source publish date
- HARD CHECK: ALL cited items must fall within {{research_timeframe}}
- Every citation MUST include a full URL

URL VALIDATION (CRITICAL):
- Check that all URLs appear to be from real sources
- REMOVE citations with fabricated URLs (e.g., URLs that look made up)
- blog.siebert.com citations: If URL pattern looks invented (e.g., "/daily-market-insights-november-2025"),
  REMOVE the citation and keep the educational point without a fake URL
- If a Malek insight has no verifiable URL, present it as general Siebert perspective without citation

Section 5 (Malek):
- 1-line hook + 3-4 bullets, 130-165 words
- Only include blog.siebert.com citations if URLs are from actual Perplexity results
- If no verified Siebert URLs, present as "According to Siebert's market perspectives..."

Style safeguards:
- Preserve Siebert educational voice (NOT casual/slang)
- Do NOT use em dashes; prefer normal punctuation
- Insert risk disclaimer where appropriate
- Maintain professional tone throughout - no Gen Z internet slang

===============================================================================
FINAL COMPLIANCE AUDIT:
===============================================================================

Before outputting, verify:
1. Exactly 8 sections (Intro, Feature, Market Reality, Numbers, Malek, Your Move, Quick Links, Sign-off)
2. No banned promotional/advisory phrases remain
3. Emojis only in headers, opening greeting, and sign-off
4. Consistent "Wealthbuilders" address (NOT "Future Wealth Builders")
5. Section 6 uses educational framing, not imperatives
6. Section 7 (Quick Links) has 4-6 clickable markdown links
7. Section 8 sign-off: "✨ Stay Empowered and Keep Building, The Wealthbuilder Team" - NO P.S.
8. All dates within {{research_timeframe}}
9. All citations have full URLs from the VERIFIED list
10. Total inline citations: 6-8 throughout the newsletter (format: Source: Name (Month YYYY))

Output:
- Corrected newsletter with all compliance issues resolved
- Add comment at end: <!-- COMPLIANCE: Removed sections/phrases: [list] -->
