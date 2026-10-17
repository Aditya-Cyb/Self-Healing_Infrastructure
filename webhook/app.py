
from flask import Flask, request, jsonify
import subprocess
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route("/alert", methods=["POST"])
def receive_alert():
    payload = request.get_json(silent=True) or {}
    logger.info("Received Alertmanager notification")

    for alert in payload.get("alerts", []):
        if alert.get("status") != "firing":
            continue

        alert_name = alert.get("labels", {}).get("alertname")
        logger.info("Firing alert received: %s", alert_name)

        if alert_name != "NginxTargetDown":
            continue

        try:
            result = subprocess.run(
                [
                    "ansible-playbook",
                    "-i", "localhost,",
                    "/app/restart-nginx.yml"
                ],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                logger.error("Recovery failed: %s", result.stderr)
                return jsonify({
                    "status": "recovery_failed",
                    "details": result.stderr
                }), 500

            logger.info("Recovery successful: %s", result.stdout)
            return jsonify({
                "status": "recovery_triggered",
                "details": result.stdout
            }), 200

        except Exception:
            logger.exception("Error while running recovery playbook")
            return jsonify({
                "status": "recovery_failed",
                "details": "Check webhook container logs"
            }), 500

    return jsonify({"status": "no_action_required"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
