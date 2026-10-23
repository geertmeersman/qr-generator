# qr-generator

Flask-based QR code generator with multi-language support, based on `python:3.13-slim`.

![screenshot](images/screenshot.png)

## Current versions

| Component | Version |
|-----------|---------|
| Python | 3.13 |

## What's inside

- Flask + Flask-Babel (i18n: nl, en, fr, de)
- qrcode[pil]

## Supported QR types

| Type | Description |
|------|-------------|
| URL | Any web URL |
| SEPA | European bank transfer (BCD format) |
| WiFi | WiFi network credentials |
| vCard | Contact card (v3.0) |
| Text | Plain text |

## Usage

```bash
docker pull <your-dockerhub-username>/qr-generator:latest
docker run -p 5000:5000 <your-dockerhub-username>/qr-generator:latest
```

Open `http://localhost:5000` in your browser.

## CI/CD

| Workflow | Trigger | Description |
|----------|---------|-------------|
| `pr-validate` | Pull request | Hadolint lint + build check |
| `docker-publish` | Daily / manual | Upstream digest check, Trivy scan, multi-platform build & push |

## Auto-updates

The image is automatically rebuilt and pushed to Docker Hub whenever the upstream `python:3.13-slim` image is updated (checked daily).

## Secrets required

| Secret | Description |
|--------|-------------|
| `DOCKERHUB_USERNAME` | Your Docker Hub username |
| `DOCKERHUB_TOKEN` | Docker Hub access token |
