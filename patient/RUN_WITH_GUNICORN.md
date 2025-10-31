# 🚀 Running Patient Alert System with Gunicorn

## ✅ Quick Start (Choose One)

### Option 1: Use Startup Scripts (Easiest)

**Windows:**
```cmd
start_gunicorn.bat
```

**Linux/Mac:**
```bash
chmod +x start_gunicorn.sh
./start_gunicorn.sh
```

### Option 2: Manual Command with Config

```bash
cd patient
gunicorn --config gunicorn_config.py wsgi:app
```

### Option 3: Simple Command (No Config)

```bash
cd patient
gunicorn --bind 0.0.0.0:5002 --workers 4 wsgi:app
```

---

## 📋 Prerequisites

1. **Gunicorn installed** (already in requirements.txt)
   ```bash
   pip install gunicorn
   ```

2. **MongoDB running**
   ```bash
   # Check if MongoDB is running
   # Windows: services.msc -> MongoDB
   # Linux: sudo systemctl status mongod
   ```

3. **Environment variables** (.env file configured)

---

## 🔧 Configuration

### Gunicorn Settings (gunicorn_config.py)

- **Port**: 5002 (from .env PORT variable)
- **Workers**: Auto-calculated (2 * CPU cores + 1)
- **Timeout**: 120 seconds
- **Preload**: True (saves memory)
- **Auto-reload**: False (set GUNICORN_RELOAD=True for dev)

### Environment Variables (.env)

```env
PORT=5002
GUNICORN_WORKERS=4
GUNICORN_RELOAD=False
LOG_LEVEL=info
MONGO_URI=mongodb://localhost:27017
DB_NAME=patients_db
OPENAI_API_KEY=your-key-here
```

---

## 🎯 Common Commands

### Development
```bash
# With auto-reload
export GUNICORN_RELOAD=True
gunicorn --config gunicorn_config.py wsgi:app

# Or just use Flask dev server
python run_app.py
```

### Production
```bash
# Production mode (no reload)
gunicorn --config gunicorn_config.py wsgi:app

# With specific number of workers
gunicorn --workers 8 --config gunicorn_config.py wsgi:app

# Custom timeout for long requests
gunicorn --timeout 300 --config gunicorn_config.py wsgi:app
```

### Background Mode (Daemon)
```bash
# Start in background
gunicorn --daemon --config gunicorn_config.py wsgi:app

# Stop daemon
pkill gunicorn  # Linux/Mac
taskkill /F /IM gunicorn.exe  # Windows
```

---

## 🧪 Testing

### 1. Test WSGI Import
```bash
cd patient
python -c "from wsgi import app; print('WSGI OK')"
```

### 2. Test Gunicorn Start
```bash
cd patient
gunicorn --bind 0.0.0.0:5002 --workers 1 --timeout 10 wsgi:app
# Press Ctrl+C after it starts successfully
```

### 3. Test API Health
```bash
curl http://localhost:5002/health

# Expected response:
# {"status": "healthy", "database": "connected", ...}
```

### 4. Test Database Connection
```bash
curl http://localhost:5002/health/database
```

---

## 📊 Monitoring

### View Active Workers
```bash
# Windows
tasklist | findstr gunicorn

# Linux/Mac
ps aux | grep gunicorn
```

### Check Port Usage
```bash
# Windows
netstat -ano | findstr :5002

# Linux/Mac
lsof -i :5002
```

### View Logs
Gunicorn logs to console by default. To save logs:

```bash
gunicorn --config gunicorn_config.py wsgi:app \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log
```

---

## 🐛 Troubleshooting

### Problem: Port already in use
```bash
# Windows
netstat -ano | findstr :5002
taskkill /PID <pid> /F

# Linux/Mac
lsof -i :5002
kill -9 <pid>
```

### Problem: Module not found
```bash
# Ensure you're in patient/ directory
cd patient

# Check Python path
python -c "import sys; print(sys.path)"

# Reinstall dependencies
pip install -r requirements.txt
```

### Problem: Database not connected
```bash
# Check MongoDB status
# Windows: services.msc
# Linux: sudo systemctl status mongod

# Test connection
curl http://localhost:5002/health/database

# Force reconnect
curl -X POST http://localhost:5002/health/database/reconnect
```

### Problem: Workers timeout
Edit `gunicorn_config.py`:
```python
timeout = 300  # Increase to 5 minutes
```

---

## 🚀 Deployment Options

### Heroku
```bash
# Procfile already configured
git push heroku main
```

### Render
```bash
# Build command: pip install -r requirements.txt
# Start command: gunicorn --config gunicorn_config.py wsgi:app
```

### Docker
```dockerfile
FROM python:3.11.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5002
CMD ["gunicorn", "--config", "gunicorn_config.py", "wsgi:app"]
```

### Nginx Reverse Proxy
```nginx
location / {
    proxy_pass http://127.0.0.1:5002;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

---

## 📈 Performance Tips

### Optimal Workers
- **CPU-bound**: 2 * CPU cores + 1
- **I/O-bound**: CPU cores * 4
- **Recommended**: 4-8 workers for most cases

### Worker Classes
```bash
# Sync (default) - good for most cases
gunicorn --worker-class sync wsgi:app

# Gevent (async) - high concurrency
pip install gevent
gunicorn --worker-class gevent --workers 4 wsgi:app

# Threads - CPU-bound tasks
gunicorn --worker-class gthread --threads 4 wsgi:app
```

### Memory Optimization
```python
# In gunicorn_config.py
max_requests = 1000  # Restart workers after 1000 requests
max_requests_jitter = 50  # Add randomness to prevent all workers restarting together
preload_app = True  # Load app before forking (saves memory)
```

---

## 🔐 Security

### Production Settings
```env
DEBUG=False
JWT_SECRET_KEY=<strong-random-key>
```

### SSL/HTTPS
```bash
gunicorn \
  --keyfile /path/to/keyfile.pem \
  --certfile /path/to/certfile.pem \
  --bind 0.0.0.0:443 \
  wsgi:app
```

---

## 📝 Files Created

✅ `wsgi.py` - WSGI entry point for Gunicorn
✅ `gunicorn_config.py` - Gunicorn configuration
✅ `start_gunicorn.bat` - Windows startup script
✅ `start_gunicorn.sh` - Linux/Mac startup script
✅ `Procfile` - Updated for Heroku/Render
✅ `.gitignore` - Updated to exclude Gunicorn logs

---

## 📚 Resources

- Full Guide: `GUNICORN_SETUP.md`
- Quick Reference: `GUNICORN_QUICKSTART.txt`
- API Documentation: Check `/health` endpoint
- Gunicorn Docs: https://docs.gunicorn.org/

---

**Ready to start!** Just run `start_gunicorn.bat` (Windows) or `./start_gunicorn.sh` (Linux/Mac)


