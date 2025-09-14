TASK 2 - MULTI-SOURCE RESEARCH WITH PERPLEXITY INTEGRATION:

CONTEXT FROM PREVIOUS TASK:
{{task1_siebert_context_setup_output}}

OBJECTIVE:
Conduct focused premium research using Perplexity AI with specific target URLs to gather real-time content for the newsletter.

IMPORTANT TOOL USAGE NOTES:
- Use named parameters in all tool calls (topic=value, exclude_topics=value)
- exclude_topics should be pipe-separated: "topic1|topic2|topic3"
- premium_sources should be specific URLs separated by pipes
- Respect the research_timeframe parameter: {{research_timeframe}}
- Focus ONLY on premium financial research for quality over quantity

STEP 1: PREMIUM FINANCIAL RESEARCH (SINGLE FOCUSED RESEARCH)
Execute targeted financial research with specific premium URLs:
[research_premium_financial] topic={{topic}}, exclude_topics=crypto day trading|get rich quick|penny stocks, research_timeframe={{research_timeframe}}, premium_sources={{siebert_target_urls}} [/research_premium_financial]

NOTE: We are eliminating multiple research steps to focus on quality data from premium sources only.

STEP 2: CONTENT CATEGORIZATION
Organize research findings by newsletter section:

FEATURE STORY CONTENT:
- Main financial news and developments from premium sources
- Market trends with broad implications
- Expert analysis and commentary with source attribution

MARKET REALITY CHECK:
- 3-4 key trends affecting young investors
- Gen Z specific market implications
- Accessible trend explanations with real data

BY THE NUMBERS:
- Key statistics and data points from research
- Market performance metrics from premium sources
- Demographic-specific financial data with citations

ACTIONABLE INSIGHTS:
- Practical investment strategies based on research
- Concrete steps for beginners
- Risk-appropriate recommendations with source backing

STEP 3: CULTURAL RELEVANCE MAPPING
Identify opportunities for:
- Pop culture analogies and references
- Social media trend connections
- Gaming, tech, and lifestyle parallels
- Current events integration

CRITICAL REQUIREMENTS:
- ALL content MUST be based on the Perplexity research findings
- Include specific data points, statistics, and quotes from sources
- Cite source URLs where applicable
- NO generic content - everything must be research-backed
- Focus on {{research_timeframe}} data only

FILTERS APPLIED:
- Exclude: {{exclude_topics}}
- Focus: {{topic}} with Gen Z relevance
- Sources: Specific premium URLs only
- Timeframe: {{research_timeframe}} priority

OUTPUT:
Structured research content organized by newsletter section with mandatory source attribution, specific data points, and real-time insights. ALL content must reference the Perplexity research findings.

