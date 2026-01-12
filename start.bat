@echo off
REM OpenPulse Quick Start Script for Windows

echo 🔮 OpenPulse - Starting services...

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    exit /b 1
)

REM Create necessary directories
echo 📁 Creating directories...
if not exist logs mkdir logs
if not exist data\raw mkdir data\raw
if not exist data\processed mkdir data\processed

REM Copy .env.example to .env if not exists
if not exist .env (
    echo 📝 Creating .env file...
    copy .env.example .env
)

REM Start services
echo 🚀 Starting Docker services...
docker-compose up -d

REM Wait for services to be ready
echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Check service status
echo ✅ Checking service status...
docker-compose ps

echo.
echo 🎉 OpenPulse is ready!
echo.
echo 📊 Access the services:
echo   - API Documentation: http://localhost:8000/docs
echo   - API ReDoc: http://localhost:8000/redoc
echo   - Web Dashboard: Open web-dashboard\index.html in your browser
echo.
echo 🔧 Useful commands:
echo   - View logs: docker-compose logs -f
echo   - Stop services: docker-compose down
echo   - Restart services: docker-compose restart
echo.
echo 📖 For more information, see README.md
