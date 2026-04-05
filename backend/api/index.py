"""Vercel Serverless Function Wrapper for FastAPI"""
import sys
import os

# Add parent directory to path so we can import main
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

# Ensure required directories exist for Vercel serverless
os.makedirs(os.path.join(backend_dir, "data"), exist_ok=True)
os.makedirs(os.path.join(backend_dir, "skills", "default"), exist_ok=True)
os.makedirs(os.path.join(backend_dir, "output"), exist_ok=True)

from main import app
from mangum import Mangum

handler = Mangum(app, debug=True)
