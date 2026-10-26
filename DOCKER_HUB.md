<p align="center">
  <a href="https://github.com/geertmeersman"><img src="https://img.shields.io/badge/maintainer-Geert%20Meersman-green?style=for-the-badge&logo=github"></a>
  <a href="https://www.buymeacoffee.com/geertmeersman"><img src="https://img.shields.io/badge/Buy%20me%20an%20Omer-donate-yellow?style=for-the-badge&logo=buymeacoffee"></a>
</p>

<p align="center">
  <a href="https://github.com/geertmeersman/qr-generator/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg"></a>
  <a href="https://github.com/geertmeersman/qr-generator/releases"><img src="https://img.shields.io/github/v/release/geertmeersman/qr-generator?logo=github"></a>
</p>

<p align="center">
  <img src="https://img.shields.io/docker/pulls/geertmeersman/qr-generator">
  <img src="https://img.shields.io/docker/v/geertmeersman/qr-generator?label=docker%20image%20version">
</p>

![screenshot](https://raw.githubusercontent.com/geertmeersman/qr-generator/main/images/screenshot-url.png)

Flask-based QR code generator with multi-language support (nl, en, fr, de).

## Screenshots

| URL | SEPA | WiFi |
|-----|------|------|
| ![URL](https://raw.githubusercontent.com/geertmeersman/qr-generator/main/images/screenshot-url.png) | ![SEPA](https://raw.githubusercontent.com/geertmeersman/qr-generator/main/images/screenshot-sepa.png) | ![WiFi](https://raw.githubusercontent.com/geertmeersman/qr-generator/main/images/screenshot-wifi.png) |

| vCard | Text | Admin |
|-------|------|-------|
| ![vCard](https://raw.githubusercontent.com/geertmeersman/qr-generator/main/images/screenshot-vcard.png) | ![Text](https://raw.githubusercontent.com/geertmeersman/qr-generator/main/images/screenshot-text.png) | ![Admin](https://raw.githubusercontent.com/geertmeersman/qr-generator/main/images/screenshot-admin.png) |

## Current versions

| Component | Version |
|-----------|---------|
| Python | 3.13.17-slim |

## Supported QR types

| Type | Fields |
|------|--------|
| URL | URL |
| SEPA | Recipient name, IBAN, Amount, BIC, Message |
| WiFi | SSID, Password, Security, Hidden |
| vCard | Name, Company, Job title, Phone, Email, Website, Street, City, Postal code, Country, Photo |
| Text | Free text |

## Usage

```bash
docker run -p 5000:5000 -v qr-data:/app/data geertmeersman/qr-generator:latest
```

Or with Docker Compose:

```yaml
services:
  qr-web:
    image: geertmeersman/qr-generator:latest
    container_name: qr-web
    ports:
      - "5000:5000"
    volumes:
      - qr-data:/app/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
    restart: unless-stopped

volumes:
  qr-data:
```

Open `http://localhost:5000` in your browser.

## Deep links

You can pre-fill the form via URL parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `tab` | `url` \| `sepa` \| `wifi` \| `vcard` \| `text` | Opens the specified tab |

**URL:** `?tab=url&url=https://example.com`

**SEPA:** `?tab=sepa&naam=Jan%20Janssen&iban=BE00000000000000&bedrag=10.00&bic=GEBABEBB&mededeling=Invoice%202026-001`

**WiFi:** `?tab=wifi&ssid=MyNetwork&password=secret&security=WPA&hidden=0`

**vCard:** `?tab=vcard&naam=Jan%20Janssen&bedrijf=Acme&functie=CEO&tel=%2B32499000000&email=jan@example.com&url=https://example.com&straat=Hoofdstraat%201&stad=Brussel&postcode=1000&land=Belgium`

**Text:** `?tab=text&text=Hello%20World`

## vCard hosting

| Path | Description |
|------|-------------|
| `/vcard/<id>` | Public vCard page with download button |
| `/vcard/<id>/download` | Direct `.vcf` download |
| `/admin` | Admin dashboard (login required) |
| `/admin/setup` | First-time admin account setup |

> Mount `/app/data` to persist vCards and the admin database.

## Auto-updates

Rebuilt automatically whenever the upstream `python:3.13-slim` image is updated.

---

© 2026 [Geert Meersman](https://github.com/geertmeersman) — Licensed under the [MIT License](https://github.com/geertmeersman/qr-generator/blob/main/LICENSE) — [Releases](https://github.com/geertmeersman/qr-generator/releases)
