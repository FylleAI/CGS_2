# 🤖 **SIEBERT ENHANCED ARTICLE - AGENT INSTRUCTIONS**

> **Agent-Optimized Knowledge Base Document 8 of 8**  
> **Target:** Enhanced Article Workflow Agent Optimization  
> **Focus:** Specific instructions for each agent role in the workflow

---

## 🎯 **ENHANCED ARTICLE WORKFLOW OVERVIEW**

### **3-Task Workflow Structure**
1. **Task 1**: `rag_specialist` - Brief Creation & Brand Context
2. **Task 2**: `rag_specialist` - Web Research & Brief Enhancement  
3. **Task 3**: `copywriter` - Final Content Creation with References

### **Critical Success Factors**
- **Reference Tracking**: Every web search result MUST be captured for reference box
- **Gen Z Voice**: Maintain authentic, conversational tone throughout
- **Siebert Integration**: Natural brand mentions without corporate speak
- **Action Orientation**: Every article must include specific next steps

---

## 🔍 **TASK 1: RAG_SPECIALIST - BRIEF CREATION**

### **Primary Objective**
Extract Siebert brand guidelines and create comprehensive brief for article topic with Gen Z focus.

### **Key Instructions**
1. **Use `rag_get_client_content`** to access complete Siebert knowledge base
2. **Focus on Enhanced Article guidelines** (documents 05-08)
3. **Extract Gen Z voice characteristics** and cultural references
4. **Identify topic-specific requirements** based on article subject
5. **Create detailed brief** including tone, structure, and key messages

### **Brief Creation Checklist**
- [ ] Brand voice guidelines extracted and summarized
- [ ] Gen Z audience characteristics identified
- [ ] Topic-specific approach determined
- [ ] Cultural references and analogies suggested
- [ ] Siebert integration points identified
- [ ] Compliance requirements noted
- [ ] Success metrics defined

### **Output Requirements**
Comprehensive brief including:
- **Topic Analysis**: Why this matters to Gen Z investors
- **Voice Guidelines**: Specific tone and language requirements
- **Structure Recommendation**: Suggested article flow and sections
- **Cultural Context**: Relevant analogies and references
- **Siebert Integration**: Natural brand mention opportunities
- **Research Needs**: Specific data and sources required

---

## 🌐 **TASK 2: RAG_SPECIALIST - WEB RESEARCH & ENHANCEMENT**

### **Primary Objective**
Conduct comprehensive web research to enhance brief with current data, trends, and sources for reference tracking.

### **Critical Requirements**
1. **MANDATORY**: Use `web_search` tool minimum 2 times
2. **CAPTURE ALL URLS**: Every search result must be documented
3. **Focus on Currency**: Prioritize recent data (last 48 hours for market content)
4. **Gen Z Relevance**: Include sources that speak to young investor experience
5. **Statistical Backing**: Find credible data to support all major claims

### **Search Strategy**
**First Search**: Broad topic exploration
- Query format: "[Topic] trends 2025 latest developments"
- Goal: Current landscape and major developments
- Capture: All URLs, publication dates, key statistics

**Second Search**: Specific data and statistics
- Query format: "[Topic] statistics data recent studies"
- Goal: Credible numbers and research findings
- Capture: Data sources, methodologies, expert quotes

**Additional Searches** (if needed):
- Gen Z-specific angles
- Expert commentary
- Market analysis
- Platform/tool information

### **Source Documentation Protocol**
For EVERY source found, document:
```
- URL: [Full web address]
- Title: [Article title]
- Publication: [Source name]
- Date: [Publication date]
- Key Data: [Relevant statistics/quotes]
- Relevance: [How it supports article]
```

### **Research Enhancement Checklist**
- [ ] Minimum 5 credible sources identified
- [ ] All URLs captured for reference box
- [ ] Current market data included
- [ ] Gen Z-relevant statistics found
- [ ] Expert commentary identified
- [ ] Cultural trends and connections noted
- [ ] Practical tools and platforms researched

### **Output Requirements**
Enhanced brief including:
- **Current Market Context**: Latest trends and developments
- **Statistical Support**: Credible data with sources
- **Expert Insights**: Commentary from industry leaders
- **Gen Z Angles**: Specific relevance to young investors
- **Cultural Connections**: Trending topics and analogies
- **Source List**: Complete documentation for reference box
- **Research Summary**: Key findings and insights

---

## ✍️ **TASK 3: COPYWRITER - FINAL CONTENT CREATION**

### **Primary Objective**
Create engaging, Gen Z-optimized article using enhanced brief while ensuring mandatory reference box inclusion.

### **Content Creation Requirements**
1. **Follow Structure Template**: Use standard Enhanced Article framework
2. **Maintain Gen Z Voice**: Conversational, authentic, empowering tone
3. **Include All Research**: Integrate findings from Task 2 naturally
4. **Create Reference Box**: MANDATORY section with all sources
5. **Optimize for Engagement**: Hook, visual breaks, clear actions

### **Article Structure Compliance**
```
1. Hook Section (100-150 words)
   - Relatable opening with emoji
   - Cultural connection or trending topic
   - Preview of value

2. Main Concept Section (300-400 words)
   - Problem statement with Gen Z context
   - Statistical backing with sources
   - Cultural analogies and explanations

3. Practical Application Section (250-350 words)
   - Step-by-step breakdown
   - Specific tools and platforms
   - Expected outcomes

4. Market Insights Section (100-150 words)
   - Mark Malek quote or Siebert commentary
   - Gen Z translation
   - Market context

5. Action Steps Section (150-200 words)
   - 3-5 specific, achievable actions
   - Checkmark formatting
   - Clear instructions

6. Community Section (100-150 words)
   - Reader spotlight or success story
   - Engagement question

7. Closing & Signature (50-75 words)
   - Empowering message
   - Community signature

8. Reference Box (MANDATORY)
   - All sources from research
   - Proper attribution
   - Compliance disclaimers
```

### **Voice and Tone Guidelines**
**DO Use:**
- Gaming analogies ("level up," "skill tree," "boss battle")
- Social media references ("algorithm," "going viral," "platform")
- Conversational transitions ("Let's be real," "Here's the thing")
- Empowering language ("You've got this," "Take control")
- Cultural references (current trends, generational experiences)

**DON'T Use:**
- Corporate jargon or overly formal language
- Condescending or patronizing tone
- Complex financial terminology without explanation
- Outdated cultural references
- Pushy sales language

### **Reference Box Requirements**
**MANDATORY INCLUSION** - Every article must end with:
```markdown
---
## 📚 **SOURCES & REFERENCES**

**Primary Research Sources:**
• [Publication] - [Title] - [URL] - [Access Date]
• [Publication] - [Title] - [URL] - [Access Date]

**Market Data Sources:**
• [Provider] - [Dataset] - [URL] - [Date]
• Siebert Financial Corp - Market Analysis - [Date]

**Expert Commentary:**
• Mark Malek, CIO, Siebert Financial - [Context]

**Statistical Sources:**
• [Organization] - [Study] - [URL] - [Date]

*Research conducted on [date]. All data current as of publication.*
*Investment involves risk. Past performance does not guarantee future results.*
---
```

### **Quality Assurance Checklist**
- [ ] Hook engages Gen Z audience immediately
- [ ] All research findings integrated naturally
- [ ] Statistics properly attributed
- [ ] Siebert mentions feel organic
- [ ] Action steps are specific and achievable
- [ ] Community engagement element included
- [ ] Reference box complete with all sources
- [ ] Compliance disclaimers included
- [ ] Word count within 800-1200 range
- [ ] Visual formatting optimized

### **Siebert Integration Guidelines**
**Natural Integration Points:**
- Market insights section (Mark Malek quotes)
- Expert commentary on trends
- Platform recommendations (when appropriate)
- Educational resource mentions
- Professional perspective on market events

**Avoid:**
- Forced product mentions
- Corporate marketing language
- Overly promotional content
- Breaking editorial independence

---

## 🚀 **WORKFLOW SUCCESS METRICS**

### **Content Quality Indicators**
- **Engagement**: Hook captures attention immediately
- **Education**: Complex concepts made accessible
- **Action**: Specific next steps provided
- **Authority**: Credible sources and expert insights
- **Authenticity**: Gen Z voice feels natural and genuine

### **Technical Requirements**
- **Word Count**: 800-1200 words
- **Source Count**: Minimum 5 credible sources
- **Reference Box**: Complete and properly formatted
- **Structure**: Follows template requirements
- **Compliance**: All disclaimers and attributions included

### **Brand Alignment**
- **Voice Consistency**: Matches Siebert's Gen Z positioning
- **Educational Focus**: Information over promotion
- **Professional Standards**: Maintains credibility
- **Community Building**: Strengthens reader relationship
- **Independence**: Clear editorial separation

---

## ⚠️ **CRITICAL REMINDERS**

### **Non-Negotiable Requirements**
1. **Reference Box MUST be included** - No exceptions
2. **All web search URLs MUST be captured** - Essential for transparency
3. **Gen Z voice MUST be authentic** - Avoid trying too hard
4. **Siebert integration MUST be natural** - No forced mentions
5. **Action steps MUST be specific** - Vague advice is not helpful

### **Common Pitfalls to Avoid**
- Forgetting to include reference box
- Using outdated cultural references
- Over-complicating financial concepts
- Forcing Siebert mentions unnaturally
- Providing vague or generic action steps
- Ignoring compliance requirements
- Missing current market context

---

*These agent instructions ensure consistent, high-quality Enhanced Articles that engage Gen Z readers while maintaining Siebert's professional standards and transparency requirements.*
