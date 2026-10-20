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

## 8. Day 2: Monitoring and Alerting Improvements

### Additional Alert Rules

The Prometheus alert configuration was extended with three rules:

- `NginxTargetDown` — detects when the NGINX availability metric is zero.
- `NginxExporterDown` — detects when Prometheus cannot scrape the NGINX exporter.
- `PrometheusTargetDown` — detects when Prometheus cannot scrape its own metrics endpoint.

### Exporter Failure and Recovery Test

The NGINX exporter was temporarily stopped to simulate a monitoring-target failure. Prometheus successfully triggered the `NginxExporterDown` alert with warning severity.

The exporter was then started again. Both the NGINX exporter target and Prometheus target returned to the `up` state, and the Prometheus alerts API returned an empty active-alert list.

**Result:** The additional exporter-down alert was verified, and normal monitoring was restored after the exporter restarted.


## 9. Conclusion

This project demonstrates how monitoring, alerting, webhook automation, and configuration management can be integrated to recover a failed service automatically. It provides a local demonstration of self-healing infrastructure and can be extended with additional health checks, notification channels, and recovery policies.

## 10. Important Note

This is a local learning project, not a production-ready deployment. The webhook container has access to the Docker socket, which grants powerful control over the Docker host. Production deployments require appropriate access restrictions, authentication, and a production-grade web server.

## 11. Day 3: End-to-End Recovery Verification

### Objective
Verify the alert-to-recovery workflow using Prometheus, Alertmanager, a Flask webhook, and Ansible.

### Verification Steps
1. Checked that all Docker Compose services were running.
2. Updated the `NginxTargetDown` alert rule to detect a zero or missing `nginx_up` metric.
3. Verified that the webhook received the `NginxTargetDown` alert from Alertmanager.
4. Confirmed that the webhook executed the Ansible recovery playbook.
5. Checked the Ansible recap: `ok=1`, `changed=1`, `failed=0`.
6. Verified that NGINX was running and returned `HTTP/1.1 200 OK`.

### Result
The webhook notification and Ansible recovery playbook executed successfully. NGINX was healthy after the recovery workflow.

**Note:** The NGINX container uses Docker's `unless-stopped` restart policy. The collected evidence confirms successful webhook/Ansible execution and post-recovery health, but does not independently prove that Ansible alone caused the container restart.

### Evidence
- `screenshots/day3-automatic-recovery-logs.png`
- `screenshots/day3-recovery-verified.png`

## 12. Day 4: Controlled Self-Healing Recovery Verification

### Objective
Verify the alert-driven recovery workflow using Prometheus, Alertmanager, a Flask webhook, Ansible, and Docker.

### Verification Steps
1. Confirmed that all five Docker Compose services were running.
2. Temporarily changed the NGINX restart policy to `no` for a controlled recovery test.
3. Stopped the NGINX container and checked the Prometheus alert state.
4. Verified webhook logs showing receipt of the `NginxTargetDown` alert.
5. Verified that the webhook executed the Ansible recovery playbook successfully.
6. Confirmed the Ansible recap showed `changed=1` and `failed=0`.
7. Verified that NGINX returned `HTTP/1.1 200 OK` after the recovery workflow.
8. Restored the original Docker Compose configuration and verified that all five services were running.

### Result
The alert notification reached the webhook, the Ansible recovery playbook executed successfully, and NGINX returned a successful HTTP response afterward.

**Limitation:** The collected logs establish successful alert delivery, Ansible execution, and post-recovery health. They do not independently establish that Ansible was the sole cause of the container restart.

### Evidence
- `screenshots/day3-automatic-recovery-logs.png`
- `screenshots/day3-recovery-verified.png`
