# Debugging Skill

## name
debugging

## description
Analyzes code, finds bugs, security issues, and provides exact fixes with explanations.

## trigger_keywords
- bug
- error
- fix
- debug
- broken
- not working
- issue
- problem
- crash
- exception
- vulnerability

## steps
1. Receive the code or error description
2. Analyze for syntax errors, logic bugs, security vulnerabilities
3. Identify root cause of each issue
4. Provide exact fix with before/after code
5. Explain why the fix works
6. Suggest preventing measures

## input_format
{
  "code": "Code to debug",
  "error": "Error message (optional)",
  "language": "python | javascript | html | css | sql",
  "context": "What the code is supposed to do"
}

## output_format
{
  "issues_found": [
    {
      "type": "syntax | logic | security | performance",
      "severity": "critical | high | medium | low",
      "line": "line number or description",
      "description": "What is wrong",
      "fix": "Exact fix with code",
      "explanation": "Why this fixes the issue"
    }
  ],
  "summary": "Overall assessment",
  "prevention_tips": ["tip1", "tip2"]
}

## examples
### Input
{"code": "def add(a, b): return a + b\nprint(add('5', 3))", "error": "TypeError", "language": "python", "context": "Add two numbers"}

### Output
{
  "issues_found": [
    {
      "type": "type",
      "severity": "high",
      "line": "print(add('5', 3))",
      "description": "String '5' passed to function expecting integer",
      "fix": "print(add(int('5'), 3))  or  print(add(5, 3))",
      "explanation": "Python cannot add string and int directly. Convert string to int first."
    }
  ],
  "summary": "1 type error found. Function logic is correct.",
  "prevention_tips": ["Use type hints", "Add input validation", "Use try/except for type safety"]
}