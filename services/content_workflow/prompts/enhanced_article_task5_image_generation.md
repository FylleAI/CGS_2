# TASK 5 - IMAGE GENERATION

## CONTEXT
You have received a compliance-approved article. Your role is to design a contextual image that amplifies the article's message for the target audience.

## INPUTS
- **Article Content**: {{task4_compliance_review}}
- **Topic**: {{topic}}
- **Target Audience**: {{target_audience}}
- **Image Style**: {{image_style}}
- **Image Provider**: {{image_provider}}
- **Image Size**: {{image_size}}
- **Image Quality**: {{image_quality}}
- **Image Focus (optional)**: {{image_focus}}


## TASK INSTRUCTIONS

### Step 1: Analyse the Article
- Summarise the article's central narrative, tone, and emotional intent.
- Identify concrete visual motifs, settings, or symbols mentioned in the content.
- Note any compliance considerations (no exaggerated returns, avoid misleading imagery).

### Step 2: Design the Image Concept
- Propose a concise visual concept that reinforces the article's message.
- Ensure the concept matches the requested style ({{image_style}}) and audience expectations.
- Describe colour palette, composition, and focal elements.

### Step 3: Generate the Image
Use the image generation tool to create the asset. Provide all required parameters exactly as shown:

[image_generation_tool]
article_content: {{task4_compliance_review}}
image_style: {{image_style}}
image_provider: {{image_provider}}
topic: {{topic}}
target_audience: {{target_audience}}
image_size: {{image_size}}
image_quality: {{image_quality}}
image_focus: {{image_focus}}
[/image_generation_tool]

## CRITICAL REQUIREMENTS
- You MUST include exactly one [image_generation_tool] block. Do not skip it.
- Do NOT fabricate image_url or image_data. They must come from the tool result only.
- The system will replace your tool block with [image_generation_tool RESULT] ... markers containing JSON.
- Keep any narrative commentary minimal (≤ 2 lines) and place it AFTER the tool block.

## FINAL OUTPUT STRUCTURE
1) The tool block (required):

[image_generation_tool]
article_content: {{task4_compliance_review}}
image_style: {{image_style}}
image_provider: {{image_provider}}
topic: {{topic}}
target_audience: {{target_audience}}
image_size: {{image_size}}
image_quality: {{image_quality}}
image_focus: {{image_focus}}
[/image_generation_tool]

2) Optionally: 1–2 lines describing the visual concept (no JSON, no URLs).

## QUALITY CHECKLIST
- ✅ Tool block present with article_content, image_style, image_provider
- ✅ Visual concept reinforces the article's primary takeaway
- ✅ Style and tone align with {{image_style}} and the target audience
- ✅ Result respects brand safety and compliance requirements
