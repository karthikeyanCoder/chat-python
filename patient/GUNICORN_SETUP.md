# Gunicorn Setup Guide - Patient Alert System

## Overview
The Patient Alert System Flask application is now configured to run with Gunicorn for production deployment.

## Quick Start

### Windows
```bash
# Run the batch file
start_gunicorn.bat
```

### Linux/Mac
```bash
# Make script executable (first time only)
chmod +x start_gunicorn.sh

# Run the script
./start_gunicorn.sh
```

### Manual Command
```bash
# Using config file (recommended)
gunicorn --config gunicorn_config.py wsgi:app

# Simple command (basic)
gunicorn --bind 0.0.0.0:5002 --workers 4 wsgi:app

# With custom workers and timeout
gunicorn --bind 0.0.0.0:5002 --workers 4 --timeout 120 wsgi:app
```

## Configuration

### Environment Variables
Create a `.env` file in the `patient/` directory:

```env
# Server Configuration
PORT=5002
GUNICORN_WORKERS=4
GUNICORN_RELOAD=False
LOG_LEVEL=info

# Database Configuration
MONGO_URI=mongodb://localhost:27017
DB_NAME=patients_db
COLLECTION_NAME=Patient_test

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-change-this-in-production

# Email Configuration
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key

# Other configurations...
```

### Gunicorn Configuration File
The `gunicorn_config.py` file contains all Gunicorn settings:

- **Workers**: Auto-calculated based on CPU cores (2 * CPU + 1)
- **Bind**: 0.0.0.0:5002 (or PORT env variable)
- **Timeout**: 120 seconds
- **Worker Class**: sync
- **Preload App**: True (saves memory)
- **Max Requests**: 1000 (prevents memory leaks)

### Custom Configuration
Edit `gunicorn_config.py` to customize:

```python
# Change number of workers
workers = 8

# Change timeout
timeout = 300

# Enable auto-reload (development only)
reload = True

# Change worker class (for async)
worker_class = 'gevent'  # Requires: pip install gevent
```

## Production Deployment

### Basic Production Command
```bash
gunicorn --config gunicorn_config.py wsgi:app
```

### With Supervisor (Linux)
Create `/etc/supervisor/conf.d/patient_alert.conf`:

```ini
[program:patient_alert]
directory=/path/to/patient
command=/path/to/venv/bin/gunicorn --config gunicorn_config.py wsgi:app
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/patient_alert/error.log
stdout_logfile=/var/log/patient_alert/access.log
```

### With Systemd (Linux)
Create `/etc/systemd/system/patient_alert.service`:

```ini
[Unit]
Description=Patient Alert System Gunicorn
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/patient
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn --config gunicorn_config.py wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable patient_alert
sudo systemctl start patient_alert
sudo systemctl status patient_alert
```

### Behind Nginx (Recommended)
Create `/etc/nginx/sites-available/patient_alert`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 120s;
        proxy_read_timeout 120s;
    }
}
```

### Docker Deployment
Add to your `Dockerfile`:

```dockerfile
FROM python:3.11.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5002

CMD ["gunicorn", "--config", "gunicorn_config.py", "wsgi:app"]
```

## Performance Tuning

### Worker Calculation
- **CPU-bound**: `workers = (2 * CPU cores) + 1`
- **I/O-bound**: `workers = CPU cores * 4`
- **Default**: 4-8 workers for most use cases

### Worker Classes
- **sync**: Default, best for most cases
- **gevent**: For high concurrency (requires: `pip install gevent`)
- **eventlet**: Alternative async (requires: `pip install eventlet`)
- **gthread**: Threaded workers

### Timeout Settings
- **Default**: 120 seconds
- **Long-running tasks**: 300+ seconds
- **API calls**: 60 seconds usually sufficient

## Monitoring

### Health Check
```bash
curl http://localhost:5002/health
```

### View Logs
Gunicorn logs to stdout/stderr by default. Redirect to files:

```bash
gunicorn --config gunicorn_config.py wsgi:app \
  >> logs/access.log 2>> logs/error.log
```

### Process Management
```bash
# View running Gunicorn processes
ps aux | grep gunicorn

# Kill all Gunicorn processes
pkill gunicorn

# Graceful restart (SIGHUP)
kill -HUP <master_pid>

# Graceful shutdown (SIGTERM)
kill -TERM <master_pid>
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 5002
# Windows:
netstat -ano | findstr :5002

# Linux/Mac:
lsof -i :5002

# Kill the process
# Windows:
taskkill /PID <pid> /F

# Linux/Mac:
kill -9 <pid>
```

### Import Errors
Ensure you're in the `patient/` directory when running:
```bash
cd patient
gunicorn --config gunicorn_config.py wsgi:app
```

### Database Connection Issues
- Check MongoDB is running
- Verify `.env` file has correct `MONGO_URI`
- Test connection: `mongo` or `mongosh`

### Worker Timeout
If requests timeout, increase in `gunicorn_config.py`:
```python
timeout = 300  # 5 minutes
```

## Development vs Production

### Development
```bash
# With auto-reload
GUNICORN_RELOAD=True gunicorn --config gunicorn_config.py wsgi:app

# Or use Flask dev server
python run_app.py
```

### Production
```bash
# Production settings
GUNICORN_RELOAD=False \
LOG_LEVEL=warning \
gunicorn --config gunicorn_config.py wsgi:app
```

## Environment-Specific Settings

### Development
```env
PORT=5002
GUNICORN_WORKERS=2
GUNICORN_RELOAD=True
LOG_LEVEL=debug
DEBUG=True
```

### Production
```env
PORT=5002
GUNICORN_WORKERS=8
GUNICORN_RELOAD=False
LOG_LEVEL=warning
DEBUG=False
```

## API Endpoints
Once running, access:

- **Health**: http://localhost:5002/health
- **API Root**: http://localhost:5002/
- **Database Health**: http://localhost:5002/health/database
- **Modules**: See `/health` response for all available endpoints

## Additional Resources

- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Flask Production Best Practices](https://flask.palletsprojects.com/en/latest/deploying/)
- [Nginx + Gunicorn Tutorial](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-20-04)


