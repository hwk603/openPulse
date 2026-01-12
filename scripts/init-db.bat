@echo off
REM Initialize OpenPulse database (Windows version)

echo Initializing OpenPulse Database...

REM Check if .env exists
if not exist .env (
    echo .env file not found. Please create one from .env.example
    exit /b 1
)

REM Wait for PostgreSQL to be ready
echo Waiting for PostgreSQL to be ready...
:wait_postgres
docker-compose exec -T postgres pg_isready -U openpulse >nul 2>&1
if errorlevel 1 (
    echo    PostgreSQL is unavailable - sleeping
    timeout /t 2 /nobreak >nul
    goto wait_postgres
)
echo PostgreSQL is ready

REM Wait for Redis to be ready
echo Waiting for Redis to be ready...
:wait_redis
docker-compose exec -T redis redis-cli ping >nul 2>&1
if errorlevel 1 (
    echo    Redis is unavailable - sleeping
    timeout /t 2 /nobreak >nul
    goto wait_redis
)
echo Redis is ready

REM Wait for IoTDB to be ready
echo Waiting for IoTDB to be ready...
timeout /t 10 /nobreak >nul
echo IoTDB should be ready

REM Create database tables
echo Creating database tables...
python -c "from src.database import init_db; init_db()"
if errorlevel 1 (
    echo Failed to create database tables
    exit /b 1
)
echo Database tables created

REM Run migrations (if using Alembic)
if exist alembic (
    echo Running database migrations...
    alembic upgrade head
    echo Migrations completed
)

echo.
echo Database initialization completed successfully!
echo.
echo Next steps:
echo   1. Start the API server: uvicorn src.api.main:app --reload
echo   2. Start Celery worker: celery -A src.tasks.celery_app worker --loglevel=info
echo   3. Visit API docs: http://localhost:8000/docs
