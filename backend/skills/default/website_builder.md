# Website Builder Skill

## name
website_builder

## description
Generates complete website structure with frontend, backend, and deployment configuration.

## trigger_keywords
- website
- web app
- landing page
- ecommerce
- portfolio
- dashboard
- site
- html
- css
- responsive

## steps
1. Analyze request type (landing, ecommerce, dashboard, portfolio)
2. Generate project structure (frontend, backend, assets)
3. Create HTML structure with semantic tags
4. Apply Tailwind CSS classes for responsive design
5. Generate JavaScript for interactivity
6. Create backend API routes if needed
7. Add deployment configuration

## input_format
{
  "type": "landing | ecommerce | portfolio | dashboard | webapp",
  "title": "Project name",
  "features": ["feature1", "feature2"],
  "tech_stack": ["html", "css", "tailwind", "react", "fastapi"]
}

## output_format
{
  "project_structure": {"files": [...]},
  "frontend_code": {"html": "...", "css": "...", "js": "..."},
  "backend_code": {"routes": "..."},
  "deployment": {"config": "..."}
}

## examples
### Input
{"type": "landing", "title": "Clothing Store", "features": ["hero section", "product grid", "contact form"]}

### Output
{
  "project_structure": {
    "files": ["index.html", "style.css", "script.js", "api.py"]
  },
  "frontend_code": {
    "html": "<!DOCTYPE html>...full HTML with Tailwind CDN...",
    "css": ".custom-class {...}",
    "js": "document.addEventListener('DOMContentLoaded', () => {...})"
  },
  "backend_code": {
    "routes": "POST /api/contact\nGET /api/products"
  },
  "deployment": {
    "config": "vercel.json or render.yaml content"
  }
}