# PaddleOCR Microservice

A FastAPI-based microservice for Optical Character Recognition (OCR) using PaddleOCR, with dynamic webhook configuration support.

## Features

- **OCR Processing**: Extract text from images using PaddleOCR
- **Multiple Input Methods**: File upload and base64 encoded images
- **Dynamic Webhook System**: Configure webhooks through API without code changes
- **Environment Configuration**: Configure webhook defaults through environment variables
- **Multiple Language Support**: English, Chinese, Korean, Japanese, and more
- **Health Monitoring**: Built-in health checks and metrics
- **Web Interface**: HTML interface for webhook management

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the environment template and configure your settings:

```bash
cp env.template .env
```

Edit `.env` file with your configuration:

```env
# Webhook Configuration
WEBHOOK_ENABLED=true
DEFAULT_WEBHOOK_URL=https://your-n8n-instance.com/webhook/ocr
DEFAULT_WEBHOOK_METHOD=POST
DEFAULT_WEBHOOK_TIMEOUT=30
DEFAULT_WEBHOOK_RETRY_ATTEMPTS=3
DEFAULT_WEBHOOK_RETRY_DELAY=1
DEFAULT_WEBHOOK_HEADERS={"Content-Type": "application/json", "Authorization": "Bearer your-token"}
DEFAULT_WEBHOOK_PAYLOAD_TEMPLATE={"custom_field": "{{filename}}", "processed_at": "{{timestamp}}"}
```

### 3. Start the Service

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Or use the provided batch file on Windows:

```bash
start.bat
```

## API Endpoints

### OCR Endpoints

- `POST /api/v1/ocr/upload` - Upload image file for OCR
- `POST /api/v1/ocr/base64` - Process base64 encoded image
- `GET /api/v1/ocr/languages` - Get supported languages

### Webhook Management

- `GET /api/v1/webhook/configs` - List all webhook configurations
- `POST /api/v1/webhook/configs` - Create new webhook configuration
- `PUT /api/v1/webhook/configs/{id}` - Update webhook configuration
- `DELETE /api/v1/webhook/configs/{id}` - Delete webhook configuration
- `POST /api/v1/webhook/configs/{id}/enable` - Enable webhook
- `POST /api/v1/webhook/configs/{id}/disable` - Disable webhook
- `POST /api/v1/webhook/configs/{id}/test` - Test webhook configuration
- `GET /api/v1/webhook/configs/summary` - Get configuration summary
- `GET /api/v1/webhook/environment` - Get environment settings

### Service Endpoints

- `GET /` - Service information
- `GET /health` - Health check
- `GET /metrics` - Service metrics

## Webhook Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `WEBHOOK_ENABLED` | Enable/disable webhook functionality | `true` |
| `DEFAULT_WEBHOOK_URL` | Default webhook endpoint URL | `` |
| `DEFAULT_WEBHOOK_METHOD` | Default HTTP method | `POST` |
| `DEFAULT_WEBHOOK_TIMEOUT` | Default timeout in seconds | `30` |
| `DEFAULT_WEBHOOK_RETRY_ATTEMPTS` | Default retry attempts | `3` |
| `DEFAULT_WEBHOOK_RETRY_DELAY` | Default retry delay in seconds | `1` |
| `DEFAULT_WEBHOOK_HEADERS` | Default headers (JSON) | `{"Content-Type": "application/json"}` |
| `DEFAULT_WEBHOOK_PAYLOAD_TEMPLATE` | Default payload template (JSON) | `` |
| `WEBHOOK_CONFIG_FILE` | Configuration file path | `webhook_configs.json` |
| `WEBHOOK_MAX_CONFIGS` | Maximum configurations allowed | `100` |
| `WEBHOOK_ALLOW_EXTERNAL_URLS` | Allow external URLs | `true` |
| `WEBHOOK_REQUIRE_AUTHENTICATION` | Require authentication | `false` |

### Webhook Configuration Model

```json
{
  "id": "uuid",
  "name": "Webhook Name",
  "url": "https://endpoint.com/webhook",
  "enabled": true,
  "method": "POST",
  "headers": {"Content-Type": "application/json"},
  "timeout": 30,
  "retry_attempts": 3,
  "retry_delay": 1,
  "payload_template": {},
  "filters": {},
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Payload Template Variables

You can use these placeholders in your custom payload template:

- `{{filename}}` - Original image filename
- `{{text_count}}` - Number of text elements found
- `{{config_name}}` - Webhook configuration name
- `{{timestamp}}` - Current timestamp
- `{{ocr_data}}` - Full OCR result data

### Example Payload Template

```json
{
  "custom_field": "{{filename}}",
  "processed_at": "{{timestamp}}",
  "text_count": "{{text_count}}",
  "webhook_name": "{{config_name}}",
  "ocr_results": "{{ocr_data}}"
}
```

## Web Interface

Open `webhook_manager.html` in your browser to manage webhook configurations through a user-friendly interface.

Features:
- View current environment settings
- Create new webhook configurations
- Enable/disable webhooks
- Test webhook configurations
- Delete webhook configurations
- Real-time status updates

## Usage Examples

### 1. Basic OCR with File Upload

```bash
curl -X POST "http://localhost:8000/api/v1/ocr/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@image.jpg"
```

### 2. Create Webhook Configuration

```bash
curl -X POST "http://localhost:8000/api/v1/webhook/configs" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "n8n Production",
    "url": "https://n8n.example.com/webhook/ocr",
    "enabled": true,
    "method": "POST",
    "timeout": 30,
    "retry_attempts": 3,
    "headers": {"Authorization": "Bearer token123"}
  }'
```

### 3. Test Webhook Configuration

```bash
curl -X POST "http://localhost:8000/api/v1/webhook/test"
```

## Configuration Files

- `webhook_configs.json` - Stores webhook configurations (auto-generated)
- `.env` - Environment variables (copy from `env.template`)

## Troubleshooting

### Common Issues

1. **Webhook not sending**: Check if webhook is enabled and URL is configured
2. **Timeout errors**: Increase `DEFAULT_WEBHOOK_TIMEOUT` in environment
3. **Authentication errors**: Configure proper headers in webhook configuration
4. **External URL blocked**: Set `WEBHOOK_ALLOW_EXTERNAL_URLS=false` for security

### Logs

Check the console output for detailed logging information. The service logs:
- Webhook creation/updates
- OCR processing results
- Webhook delivery status
- Configuration changes

### Health Check

```bash
curl http://localhost:8000/health
```

This will show the status of all services including webhook configurations.

## Security Considerations

- Set `WEBHOOK_ALLOW_EXTERNAL_URLS=false` in production if only internal webhooks are needed
- Use authentication headers for sensitive webhook endpoints
- Regularly review and clean up unused webhook configurations
- Monitor webhook delivery logs for suspicious activity

## Development

### Project Structure

```
app/
├── __init__.py
├── main.py              # FastAPI application entry point
├── config.py            # Configuration settings
├── api/
│   ├── __init__.py
│   └── endpoints.py     # API route definitions
├── models/
│   ├── __init__.py
│   ├── schemas.py       # Pydantic models
│   └── webhook_config.py # Webhook configuration models
└── services/
    ├── __init__.py
    ├── ocr_service.py   # OCR processing logic
    ├── webhook_service.py # Webhook delivery service
    └── webhook_config_service.py # Webhook configuration management
```

### Adding New Features

1. Add new models in `app/models/`
2. Implement business logic in `app/services/`
3. Create API endpoints in `app/api/endpoints.py`
4. Update configuration in `app/config.py` if needed
5. Add environment variables to `env.template`

## License

This project is open source and available under the MIT License.
