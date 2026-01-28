# PowerShell script to prepare NewsGenie repository for GitHub
# Run this with: powershell -ExecutionPolicy Bypass -File prepare-repo.ps1

Write-Host "🔧 Preparing NewsGenie repository for GitHub..." -ForegroundColor Blue

# Remove sensitive files from git tracking if they're already tracked
Write-Host "🛡️ Removing sensitive files from git tracking..." -ForegroundColor Yellow

# Check and remove .env file from git if it's tracked
$envTracked = git ls-files | Select-String "^\.env$"
if ($envTracked) {
    Write-Host "⚠️ Found .env file in git tracking - removing it..." -ForegroundColor Red
    git rm --cached .env
} else {
    Write-Host "✅ .env file not tracked by git" -ForegroundColor Green
}

# Check and remove database files from git if tracked
$dbTracked = git ls-files | Select-String "\.db$"
if ($dbTracked) {
    Write-Host "⚠️ Found database files in git tracking - removing them..." -ForegroundColor Red
    git rm --cached "*.db"
} else {
    Write-Host "✅ No database files tracked by git" -ForegroundColor Green
}

# Check and remove __pycache__ directories if tracked
$pycacheTracked = git ls-files | Select-String "__pycache__"
if ($pycacheTracked) {
    Write-Host "⚠️ Found __pycache__ directories in git tracking - removing them..." -ForegroundColor Red
    git rm --cached -r __pycache__/
} else {
    Write-Host "✅ No __pycache__ directories tracked by git" -ForegroundColor Green
}

# Check and remove log files if tracked
$logTracked = git ls-files | Select-String "\.log$"
if ($logTracked) {
    Write-Host "⚠️ Found log files in git tracking - removing them..." -ForegroundColor Red
    git rm --cached "*.log"
} else {
    Write-Host "✅ No log files tracked by git" -ForegroundColor Green
}

# Add all safe files to git
Write-Host "📁 Adding safe files to git..." -ForegroundColor Blue

$safeFiles = @(
    ".gitignore",
    ".env.example", 
    "README.md",
    "DEPLOYMENT.md",
    "requirements.txt",
    "app.py",
    "ProjectNewsGenie.ipynb",
    "Dockerfile",
    "docker-compose.yml",
    "nginx.conf",
    "init-db.sql", 
    "prometheus.yml",
    "k8s-deployment.yaml",
    "deploy.sh",
    ".github/",
    ".dockerignore"
)

foreach ($file in $safeFiles) {
    if (Test-Path $file) {
        git add $file
        Write-Host "   Added: $file" -ForegroundColor DarkGreen
    }
}

Write-Host ""
Write-Host "✅ Repository prepared for GitHub!" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Next steps:" -ForegroundColor Cyan
Write-Host "1. Review the changes: " -NoNewline; Write-Host "git status" -ForegroundColor White
Write-Host "2. Commit the changes: " -NoNewline; Write-Host "git commit -m 'Add NewsGenie enterprise production setup'" -ForegroundColor White  
Write-Host "3. Push to GitHub: " -NoNewline; Write-Host "git push origin main" -ForegroundColor White
Write-Host ""
Write-Host "⚠️ IMPORTANT:" -ForegroundColor Red
Write-Host "   - Keep your .env file LOCAL only" -ForegroundColor Yellow
Write-Host "   - Share .env.example with your team" -ForegroundColor Yellow
Write-Host "   - Never commit real API keys" -ForegroundColor Yellow