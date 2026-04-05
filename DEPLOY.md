# AI Agency Portal - Deployment Guide

## Step 1: GitHub Setup

### Login to GitHub CLI
```bash
gh auth login --web
```
Browser will open. Copy the code and go to https://github.com/login/device

### Create Repo and Push
```bash
cd ai-agency-portal
gh repo create ai-agency-portal --public --source=. --remote=origin --push
```

### Manual Alternative
```bash
cd ai-agency-portal
git remote add origin https://github.com/YOUR_USERNAME/ai-agency-portal.git
git branch -M main
git push -u origin main
```

---

## Step 2: Deploy Frontend to Vercel

### Install Vercel CLI
```bash
npm i -g vercel
```

### Login to Vercel
```bash
vercel login
```

### Deploy Frontend
```bash
cd ai-agency-portal/frontend
vercel --prod
```

### Update API URL
After deploying backend, update the API URL in:
`frontend/app/page.js` line 3:
```js
const API = 'https://YOUR_BACKEND_URL.com';
```

---

## Step 3: Deploy Backend (Python FastAPI)

### Option A: Render.com (Recommended - Free)
1. Go to https://render.com
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Connect your `ai-agency-portal` repo
5. Settings:
   - Root Directory: `ai-agency-portal/backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python main.py`
   - Environment: Python 3
6. Add environment variables:
   - `OPENROUTER_API_KEY`: your-api-key
   - `OPENROUTER_MODEL`: qwen/qwen3.6-plus:free
7. Deploy!

### Option B: Railway.app (Free Tier)
1. Go to https://railway.app
2. Sign up with GitHub
3. "New Project" → "Deploy from GitHub repo"
4. Select `ai-agency-portal`
5. Set root directory to `ai-agency-portal/backend`
6. Add env vars:
   - `OPENROUTER_API_KEY`: your-api-key
7. Deploy!

### Option C: PythonAnywhere (Free)
1. Go to https://www.pythonanywhere.com
2. Create account
3. Upload backend files
4. Configure WSGI for FastAPI

---

## Step 4: Connect Frontend to Backend

After backend is deployed, get the URL (e.g., `https://ai-agency-backend.onrender.com`)

Update frontend:
```bash
cd ai-agency-portal/frontend/app
# Edit page.js line 3:
# const API = 'https://YOUR_BACKEND_URL.com';
```

Redeploy frontend:
```bash
cd ai-agency-portal/frontend
vercel --prod
```

---

## Quick Deploy Commands

### Check Status
```bash
gh auth status
git status
```

### Push Updates
```bash
cd ai-agency-portal
git add -A
git commit -m "update"
git push origin main
```

### Redeploy Frontend
```bash
cd ai-agency-portal/frontend
vercel --prod
```

### Redeploy Backend (Render)
- Push to GitHub triggers auto-deploy
- Or manually trigger in Render dashboard