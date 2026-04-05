"""
Skills System - User can add skills, CEO assigns skills to agents/departments
"""
import os
import json

SKILLS_FILE = os.path.join(os.path.dirname(__file__), "skills.json")

def load_skills():
    if os.path.exists(SKILLS_FILE):
        with open(SKILLS_FILE, "r") as f:
            return json.load(f)
    return {"skills": [], "agent_skills": {}}

def save_skills(data):
    with open(SKILLS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_skill(name, description, category="general", tools=None):
    data = load_skills()
    skill = {
        "name": name,
        "description": description,
        "category": category,
        "tools": tools or []
    }
    data["skills"].append(skill)
    save_skills(data)
    return skill

def assign_skill(agent_name, skill_name):
    data = load_skills()
    if agent_name not in data["agent_skills"]:
        data["agent_skills"][agent_name] = []
    if skill_name not in data["agent_skills"][agent_name]:
        data["agent_skills"][agent_name].append(skill_name)
    save_skills(data)
    return {"agent": agent_name, "skill": skill_name, "status": "assigned"}

def get_agent_skills(agent_name):
    data = load_skills()
    skill_names = data["agent_skills"].get(agent_name, [])
    return [s for s in data["skills"] if s["name"] in skill_names]

def get_all_skills():
    return load_skills()

def remove_agent_skill(agent_name, skill_name):
    data = load_skills()
    if agent_name in data["agent_skills"]:
        data["agent_skills"][agent_name] = [s for s in data["agent_skills"][agent_name] if s != skill_name]
        save_skills(data)
    return {"agent": agent_name, "skill": skill_name, "status": "removed"}

# Default skills - Updated with .claude/skills folder structure
DEFAULT_SKILLS = [
    {"name": "web-development", "description": "Build full-stack websites with React, Next.js, Tailwind CSS, HTML/CSS. Create landing pages, responsive designs, modern UI components.", "category": "development", "tools": ["code_generator", "file_writer", "browser_preview"]},
    {"name": "image-generation", "description": "Create stunning images, graphics, and visual assets using AI. Generate logos, banners, social media graphics, product mockups.", "category": "creative", "tools": ["ai_image_generator", "color_palette", "brand_guidelines"]},
    {"name": "social-media-marketing", "description": "Create engaging social media content, ad copy, and marketing campaigns. Platforms: Instagram, Twitter/X, LinkedIn, Facebook, TikTok.", "category": "marketing", "tools": ["content_generator", "hashtag_research", "analytics_tracker"]},
    {"name": "qa-testing", "description": "Write tests, debug code, perform QA. Unit tests, integration tests, end-to-end testing, bug fixing.", "category": "qa", "tools": ["test_runner", "debugger", "coverage_analyzer"]},
    {"name": "devops-deployment", "description": "Deploy apps, manage infrastructure, CI/CD pipelines, monitoring, and scaling.", "category": "infrastructure", "tools": ["deployer", "docker_generator", "ci_cd_setup"]},
    {"name": "product-strategy", "description": "Product planning, roadmap creation, user research, feature prioritization, PRD writing.", "category": "product", "tools": ["roadmap_builder", "user_story_generator", "metrics_tracker"]},
    {"name": "data-analysis", "description": "Analyze data, create charts, build ML models, generate insights and reports.", "category": "data", "tools": ["data_processor", "chart_generator", "ml_model_builder"]},
    {"name": "security-audit", "description": "Scan project for vulnerabilities, implement auth security, protect API keys, prevent bot attacks, secure deployment.", "category": "security", "tools": ["vulnerability_scanner", "auth_hardener", "bot_defense", "secret_detector"]},
    {"name": "hr-management", "description": "Manage hiring, onboarding, employee communications, team building, and HR operations.", "category": "hr", "tools": ["jd_generator", "onboarding_builder", "communication_helper"]},
]

def init_default_skills():
    data = load_skills()
    if not data["skills"]:
        data["skills"] = DEFAULT_SKILLS
        # Assign default skills to agents (updated to match new skill names)
        data["agent_skills"] = {
            "Atlas": ["web-development", "product-strategy", "data-analysis"],
            "Amit": ["web-development", "devops-deployment"],
            "Ravi": ["web-development", "qa-testing", "devops-deployment"],
            "Priya": ["web-development", "image-generation"],
            "Rohan": ["image-generation"],
            "Kavita": ["social-media-marketing", "data-analysis"],
            "Sneha": ["qa-testing", "security-audit"],
            "Vikram": ["devops-deployment", "security-audit"],
            "Neha": ["product-strategy", "data-analysis"],
            "Arjun": ["data-analysis"],
            "Deepak": ["security-audit"],
            "Pooja": ["hr-management", "social-media-marketing"],
        }
        save_skills(data)
        return data
    return data
