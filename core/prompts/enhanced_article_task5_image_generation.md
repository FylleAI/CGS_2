# TASK 5 - IMAGE GENERATION

## CONTEXT
You have received a compliance-approved article. Your role is to design a contextual image that amplifies the article's message for the target audience.

## INPUTS
- **Article Content**: {{task4_compliance_review}}
- **Topic**: {{topic}}
- **Target Audience**: {{target_audience}}
- **Image Style**: {{image_style}}
- **Image Provider**: {{image_provider}}

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
[/image_generation_tool]

## OUTPUT FORMAT
Return a JSON object with the following structure:
```
{
  "image_concept": "Short description of the visual idea",
  "generation_prompt": "Prompt submitted to the tool",
  "image_metadata": {
    "provider": "openai",
    "style": "professional",
    "size": "1024x1024"
  },
  "success": true,
  "image_url": "https://... or null if unavailable",
  "image_data": "Base64 payload if provided"
}
```

## QUALITY CHECKLIST
- ✅ Visual concept reinforces the article's primary takeaway.
- ✅ Style and tone align with {{image_style}} and the target audience.
- ✅ Tool call includes article_content, image_style, and image_provider parameters.
- ✅ Result respects brand safety and compliance requirements.
