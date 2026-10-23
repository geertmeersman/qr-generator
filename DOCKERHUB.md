# qr-generator

![screenshot](https://raw.githubusercontent.com/geertmeersman/qr-generator/main/images/screenshot.png)

Flask-based QR code generator with multi-language support (nl, en, fr, de).

## Current versions

| Component | Version |
|-----------|---------|
| Python | PYTHON_VERSION_PLACEHOLDER |

## Supported QR types

- **URL** — Any web URL
- **SEPA** — European bank transfer (BCD format)
- **WiFi** — WiFi network credentials
- **vCard** — Contact card (v3.0)
- **Text** — Plain text

## Usage

```bash
docker run -p 5000:5000 geertmeersman/qr-generator:latest
```

Or with Docker Compose:

```yaml
services:
  qr-web:
    image: geertmeersman/qr-generator:latest
    container_name: qr-web
    ports:
      - "5000:5000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
    restart: unless-stopped
```

Open `http://localhost:5000` in your browser.

## Auto-updates

Rebuilt automatically whenever the upstream `python:3.13-slim` image is updated.
