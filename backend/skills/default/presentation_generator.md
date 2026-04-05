# Presentation Generator Skill

## name
presentation_generator

## description
Creates presentation slides with structured content, visuals, and speaker notes.

## trigger_keywords
- presentation
- slides
- pitch deck
- ppt
- keynote
- slideshare
- pitch
- proposal deck

## steps
1. Analyze presentation topic and audience
2. Determine slide count and structure (title, content, conclusion)
3. Generate slide content (headlines, bullet points, visuals descriptions)
4. Add speaker notes for each slide
5. Apply design theme suggestions
6. Output in HTML/CSS presentation format

## input_format
{
  "topic": "Presentation topic",
  "audience": "target audience",
  "slide_count": 5-15,
  "theme": "professional | creative | minimal | corporate",
  "key_points": ["point1", "point2", "point3"]
}

## output_format
{
  "slides": [
    {
      "title": "Slide title",
      "content": ["bullet points"],
      "visual_suggestion": "description of visual",
      "speaker_notes": "notes for presenter"
    }
  ],
  "theme_applied": "theme name",
  "total_slides": number
}

## examples
### Input
{"topic": "AI Agency Services", "audience": "potential clients", "slide_count": 5, "theme": "professional", "key_points": ["services", "process", "results", "pricing", "contact"]}

### Output
{
  "slides": [
    {"title": "Welcome to AI Agency", "content": ["Transform your business with AI"], "visual_suggestion": "hero image", "speaker_notes": "Introduce yourself"},
    {"title": "Our Services", "content": ["Web Development", "SEO", "Marketing"], "visual_suggestion": "service icons", "speaker_notes": "Explain each service"},
    {"title": "Our Process", "content": ["Discovery", "Build", "Deploy"], "visual_suggestion": "timeline graphic", "speaker_notes": "Walk through process"},
    {"title": "Results", "content": ["100+ projects", "95% satisfaction"], "visual_suggestion": "stats dashboard", "speaker_notes": "Share success stories"},
    {"title": "Get Started", "content": ["Contact us today"], "visual_suggestion": "CTA button", "speaker_notes": "Call to action"}
  ],
  "theme_applied": "professional",
  "total_slides": 5
}