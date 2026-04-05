# Document Formatter Skill

## name
document_formatter

## description
Formats documents, reports, and text content with professional styling and structure.

## trigger_keywords
- document
- report
- format
- resume
- proposal
- invoice
- letter
- markdown
- pdf
- clean up

## steps
1. Analyze input document type and content
2. Identify sections, headings, and structure
3. Apply appropriate formatting (headings, lists, tables)
4. Add professional styling (fonts, spacing, margins)
5. Generate output in requested format (HTML, MD, plain text)

## input_format
{
  "type": "report | resume | proposal | invoice | letter | general",
  "content": "Raw text content",
  "format": "html | markdown | plain",
  "style": "professional | creative | minimal"
}

## output_format
{
  "formatted_content": "Formatted document",
  "format_used": "html | markdown",
  "sections": ["section1", "section2"]
}

## examples
### Input
{"type": "report", "content": "Q1 Sales: 500 units, Revenue: 50000, Growth: 15%", "format": "html", "style": "professional"}

### Output
{
  "formatted_content": "<h1>Q1 Sales Report</h1><table><tr><td>Sales</td><td>500 units</td></tr><tr><td>Revenue</td><td>$50,000</td></tr><tr><td>Growth</td><td>15%</td></tr></table>",
  "format_used": "html",
  "sections": ["Q1 Sales Report", "Summary"]
}