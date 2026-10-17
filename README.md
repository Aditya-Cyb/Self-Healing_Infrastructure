# Self-Healing Infrastructure with Prometheus, Alertmanager & Ansible

## 1. Project Overview

This project implements a local self-healing infrastructure using Docker, Prometheus, Alertmanager, Flask, and Ansible. It monitors an NGINX service and automatically attempts recovery when a service-down alert is received.

## 2. Objectives

- Monitor NGINX service availability.
- Collect NGINX metrics using Prometheus.
- Detect service failure through alert rules.
- Send alerts from Alertmanager to a Flask webhook.
- Execute an Ansible playbook to restart the NGINX container.
- Verify recovery using container status and HTTP response.

## 3. Tools and Technologies

- Docker and Docker Compose
- NGINX
- NGINX Prometheus Exporter
- Prometheus
- Alertmanager
- Python and Flask
- Ansible
- Git and GitHub

## 4. Architecture and Workflow

1. NGINX runs as a Docker container and exposes port `8081` on the host.
2. The NGINX Prometheus Exporter collects metrics from NGINX's `/stub_status` endpoint.
3. Prometheus scrapes exporter metrics on port `9113` and evaluates alert rules.
4. When `NginxTargetDown` fires, Prometheus sends the alert to Alertmanager.
5. Alertmanager forwards the notification to the Flask webhook at `http://webhook:5000/alert`.
6. The webhook identifies the `NginxTargetDown` alert and executes `restart-nginx.yml` through Ansible.
7. Ansible restarts the `self-healing-nginx` container.

## 5. Project Structure

```text
self-healing-infrastructure/
├── alertmanager/
│   └── alertmanager.yml
├── ansible/
│   └── restart-nginx.yml
├── nginx/
│   └── default.conf
├── prometheus/
│   ├── alerts.yml
│   └── prometheus.yml
├── screenshots/
├── webhook/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml
└── README.md
```

## 6. Setup and Execution

Start all services:

```bash
docker compose up -d --build
```

Check container status:

```bash
docker compose ps
```

Open the following local endpoints:

- NGINX: http://localhost:8081
- Prometheus: http://localhost:9090
- Alertmanager: http://localhost:9093

Check Prometheus targets at `http://localhost:9090/targets` and alert rules at `http://localhost:9090/alerts`.

## 7. Testing and Results

The project was tested by stopping the NGINX container to simulate a service failure.

```bash
docker stop self-healing-nginx
```

Prometheus reported `nginx_up = 0` and the `NginxTargetDown` alert entered the firing state. Alertmanager delivered the notification to the webhook, which executed the Ansible recovery playbook.

The webhook logs confirmed successful recovery, and the Ansible recap reported:

```text
ok=1 changed=1 unreachable=0 failed=0
```

The NGINX container returned to the `Up` state, and an HTTP request to `http://localhost:8081` returned `HTTP/1.1 200 OK`.

**Result:** The end-to-end alert-to-recovery workflow was successfully tested in the local Docker environment.

## 8. Conclusion

This project demonstrates how monitoring, alerting, webhook automation, and configuration management can be integrated to recover a failed service automatically. It provides a local demonstration of self-healing infrastructure and can be extended with additional health checks, notification channels, and recovery policies.

## 9. Important Note

This is a local learning project, not a production-ready deployment. The webhook container has access to the Docker socket, which grants powerful control over the Docker host. Production deployments require appropriate access restrictions, authentication, and a production-grade web server.
