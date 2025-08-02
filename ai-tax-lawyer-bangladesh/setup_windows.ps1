# Windows PowerShell Setup Script for AI Tax Lawyer Bangladesh
# Run this in PowerShell as Administrator

Write-Host "🚀 Setting up AI Tax Lawyer Bangladesh - Week 1 Completion" -ForegroundColor Green

# Check Python installation
Write-Host "🐍 Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Python not found. Please install Python 3.8+ from https://python.org" -ForegroundColor Red
    exit 1
}

# Check pip
Write-Host "📦 Checking pip..." -ForegroundColor Yellow
$pipVersion = pip --version 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Pip found: $pipVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Pip not found. Installing pip..." -ForegroundColor Red
    python -m ensurepip --upgrade
}

# Create virtual environment
Write-Host "🏗️ Creating virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✅ Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "🔌 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Install core dependencies only (for Week 1)
Write-Host "📚 Installing core dependencies..." -ForegroundColor Yellow
$corePackages = @(
    "pydantic>=2.5.0",
    "python-dotenv>=1.0.0", 
    "pymongo>=4.6.0",
    "requests>=2.31.0",
    "fastapi>=0.104.0"
)

foreach ($package in $corePackages) {
    Write-Host "   Installing $package..." -ForegroundColor Cyan
    pip install $package
}

# Test MongoDB connection
Write-Host "🗄️ Testing MongoDB connection..." -ForegroundColor Yellow
python -c "
import pymongo
try:
    client = pymongo.MongoClient('mongodb+srv://habib:Khurshida71@cluster0.qqlnw.mongodb.net/ai-tax-lawyer?retryWrites=true&w=majority&appName=Cluster0')
    client.admin.command('ping')
    print('✅ MongoDB connection successful')
except Exception as e:
    print(f'❌ MongoDB connection failed: {e}')
"

# Check Docker Desktop
Write-Host "🐳 Checking Docker Desktop..." -ForegroundColor Yellow
$dockerVersion = docker --version 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Docker found: $dockerVersion" -ForegroundColor Green
    
    # Start RAGFlow
    Write-Host "🔍 Starting RAGFlow..." -ForegroundColor Yellow
    Set-Location "..\ragflow"
    
    if (Test-Path ".env") {
        Write-Host "✅ RAGFlow .env file found" -ForegroundColor Green
    } else {
        Write-Host "⚠️ RAGFlow .env file missing. Please create one." -ForegroundColor Yellow
    }
    
    # Check if RAGFlow is running
    $ragflowStatus = docker-compose ps 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "📊 RAGFlow status:" -ForegroundColor Cyan
        docker-compose ps
    }
    
    Set-Location "..\ai-tax-lawyer-bangladesh"
    
} else {
    Write-Host "⚠️ Docker not found. Install Docker Desktop for RAGFlow support" -ForegroundColor Yellow
}

# Run Week 1 completion test
Write-Host "🧪 Running Week 1 completion test..." -ForegroundColor Yellow
python week1_completion_test.py

Write-Host "🎉 Week 1 setup complete!" -ForegroundColor Green
Write-Host "📋 Next steps:" -ForegroundColor Yellow
Write-Host "   1. Install Docker Desktop if not done" -ForegroundColor White
Write-Host "   2. Start RAGFlow: cd ../ragflow && docker-compose up -d" -ForegroundColor White
Write-Host "   3. Run tests: python week1_completion_test.py" -ForegroundColor White