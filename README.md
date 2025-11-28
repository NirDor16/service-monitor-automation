# Service Monitor Automation

A small **Python-based service & network monitor** 
The tool runs a series of checks against external services (HTTP APIs and
network endpoints), logs the results, sends alerts to Slack on failures, and
can be executed locally or inside Docker / Docker Compose.

---

## 🔍 Features

- **HTTP API checks**
  - Calls multiple HTTP endpoints
  - Measures response time (ms)
  - Validates HTTP status codes
- **Network connectivity checks**
  - ICMP ping
  - DNS lookup
  - TCP port check (e.g. GitHub 443)
- **Config-driven via YAML**
  - Services and endpoints defined in `monitor/config.yaml`
- **Structured logging**
  - Logs to console **and** `logs/monitor.log`
  - Includes timestamp, level, component and message
- **Slack alerts**
  - Sends a notification when checks fail
  - Slack webhook is configured in `config.yaml`
- **Automated tests with pytest**
  - Basic tests for API and network logic in `tests/`
- **Containerized**
  - `Dockerfile` + `docker-compose.yml`
  - Single command to run the whole suite in a container

This project is intentionally small but realistic – good for demonstrating
hands-on experience with automation, monitoring and infrastructure tools.

---

## 🧱 Project Structure

```text
service-monitor-automation/
├─ monitor/
│  ├─ __init__.py
│  ├─ api_checker.py       # HTTP API checks
│  ├─ network_checker.py   # Network checks (ping, DNS, TCP)
│  ├─ logger.py            # Logging setup (file + console)
│  ├─ alert.py             # Slack alert integration
│  ├─ config_loader.py     # Loads and parses config.yaml
│  ├─ config.yaml          # Services & alerts configuration
├─ tests/
│  ├─ conftest.py
│  ├─ test_api.py
│  ├─ test_network.py
├─ scripts/
│  ├─ run_checks.sh        # Linux shell wrapper
│  ├─ run_checks.ps1       # Windows PowerShell wrapper
├─ logs/
│  ├─ monitor.log          # Created at runtime
├─ Dockerfile
├─ docker-compose.yml
├─ requirements.txt
└─ README.md

