# ⚡ UniFi Connect EV Charge Report

[![Docker Hub](https://img.shields.io/docker/pulls/fgc92/ev-charging-report?style=flat-square&logo=docker)](https://hub.docker.com/r/fgc92/ev-charging-report)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](LICENSE)
[![GitHub Actions](https://img.shields.io/github/actions/workflow/status/fgadot/unifi-connect-ev-charging-report/docker-publish.yml?style=flat-square&logo=github)](https://github.com/fgadot/unifi-connect-ev-charging-report/actions)

A self-hosted web app that turns a **UniFi EV Station** charging history CSV into an interactive cost dashboard — with charts, month navigation, live kWh price editing, and Excel / PDF export.

Built with Django. Runs entirely in Docker. No cloud account required.

![Dashboard screenshot](https://raw.githubusercontent.com/fgadot/unifi-connect-ev-charging-report/main/docs/screenshot.png)

---

## Quick start

```bash
docker run -d -p 8000:8000 \
  -e DJANGO_SECRET_KEY=changeme \
  --name ev-report \
  fgc92/ev-charging-report:latest
```

Open **http://localhost:8000**, upload your CSV, done.

### With docker compose (recommended)

```bash
git clone https://github.com/fgadot/unifi-connect-ev-charging-report.git
cd unifi-connect-ev-charging-report
cp .env.example .env          # edit DJANGO_SECRET_KEY
docker compose up -d
```

---

## Features

| | |
|---|---|
| 📅 Month navigation | Only months present in your data appear |
| 💲 Live kWh price | Change the rate — all costs update instantly |
| 📊 4 charts | Daily cost, daily kWh, avg cost by day of week, cost by month |
| 📋 Day table | Sessions, kWh, charge time, cost, cumulative per day |
| ⬇ Excel export | Full workbook with editable price cell |
| ⬇ PDF export | Print-ready multi-page report |
| 🔔 Update notifications | Banner appears when a new Docker image is available |
| 🔄 Auto-update (optional) | Run with Watchtower to upgrade automatically |

---

## Auto-updates with Watchtower

To have the container update itself when a new image is pushed to Docker Hub, add Watchtower to your compose file:

```yaml
services:
  web:
    image: fgc92/ev-charging-report:latest
    ports:
      - "8000:8000"
    environment:
      - DJANGO_SECRET_KEY=changeme
    restart: unless-stopped
    labels:
      - "com.centurylinklabs.watchtower.enable=true"

  watchtower:
    image: containrrr/watchtower
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    command: --interval 300 --cleanup --label-enable
    restart: unless-stopped
```

Watchtower checks every 5 minutes and only updates containers with the `watchtower.enable=true` label — your other containers are not affected.

---

## Manual upgrade

If you see the update banner in the app:

```bash
docker pull fgc92/ev-charging-report:latest
docker stop ev-report && docker rm ev-report
docker run -d -p 8000:8000 \
  -e DJANGO_SECRET_KEY=changeme \
  --name ev-report \
  fgc92/ev-charging-report:latest
```

Or with compose: `docker compose pull && docker compose up -d`

---

## Expected CSV format

Export from your UniFi console. The file must contain:

| Column | Description |
|---|---|
| `Date (console local time)` | Session timestamp (local preferred) |
| `Date (UTC time)` | Fallback if local time column is absent |
| `Power Usage (kWh)` | Energy used per session |
| `Charge Time (s)` | Active charging seconds |
| `Total Time (s)` | Total session seconds |

---

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `DJANGO_SECRET_KEY` | *(required in prod)* | Django secret key — set to any long random string |
| `DEBUG` | `false` | Set to `true` for development error pages |

---

## CI/CD

Every push to `main` triggers a GitHub Actions workflow that builds a multi-arch image (`linux/amd64` + `linux/arm64`) and pushes it to Docker Hub as `fgc92/ev-charging-report:latest`.

Required GitHub secrets: `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN`.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Issues and PRs are welcome.

## License

[MIT](LICENSE) © 2026 Frank Gadot
