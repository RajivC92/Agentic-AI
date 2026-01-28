#!/bin/bash
# Git Repository Preparation Script for NewsGenie
# This script prepares your repository for safe GitHub pushing

echo "🔧 Preparing NewsGenie repository for GitHub..."

# Remove sensitive files from git tracking if they're already tracked
echo "🛡️ Removing sensitive files from git tracking..."

# Remove .env file from git if it's tracked
if git ls-files | grep -q "^\.env$"; then
    echo "⚠️ Found .env file in git tracking - removing it..."
    git rm --cached .env
else
    echo "✅ .env file not tracked by git"
fi

# Remove database files from git if tracked
if git ls-files | grep -q "\.db$"; then
    echo "⚠️ Found database files in git tracking - removing them..."
    git rm --cached *.db
else
    echo "✅ No database files tracked by git"
fi

# Remove __pycache__ directories if tracked
if git ls-files | grep -q "__pycache__"; then
    echo "⚠️ Found __pycache__ directories in git tracking - removing them..."
    git rm --cached -r __pycache__/
else
    echo "✅ No __pycache__ directories tracked by git"
fi

# Remove log files if tracked
if git ls-files | grep -q "\.log$"; then
    echo "⚠️ Found log files in git tracking - removing them..."
    git rm --cached *.log
else
    echo "✅ No log files tracked by git"
fi

# Add all safe files to git
echo "📁 Adding safe files to git..."
git add .gitignore
git add .env.example
git add README.md
git add DEPLOYMENT.md
git add requirements.txt
git add app.py
git add ProjectNewsGenie.ipynb
git add Dockerfile
git add docker-compose.yml
git add nginx.conf
git add init-db.sql
git add prometheus.yml
git add k8s-deployment.yaml
git add deploy.sh
git add .github/
git add .dockerignore

echo "✅ Repository prepared for GitHub!"
echo ""
echo "🚀 Next steps:"
echo "1. Review the changes: git status"
echo "2. Commit the changes: git commit -m 'Add NewsGenie enterprise production setup'"
echo "3. Push to GitHub: git push origin main"
echo ""
echo "⚠️ IMPORTANT: Make sure to:"
echo "   - Keep your .env file LOCAL only"
echo "   - Share .env.example with your team"
echo "   - Never commit real API keys"