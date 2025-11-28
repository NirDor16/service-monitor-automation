import requests
import logging
from .logger import logger
from .config_loader import load_config


def send_alert(message: str):
    """
    Send an alert message to Slack using the webhook defined in config.yaml.
    """
    # Load configuration dynamically (avoids circular imports)
    config = load_config()

    # Extract Slack webhook URL
    webhook = config.get("alerts", {}).get("slack_webhook")

    if not webhook:
        logger.error("No Slack webhook configured!")
        return

    try:
        payload = {"text": message}
        resp = requests.post(webhook, json=payload, timeout=5)

        if resp.status_code != 200:
            logger.error(f"Slack error {resp.status_code}: {resp.text}")
        else:
            logger.info("Alert sent successfully to Slack")

    except Exception as e:
        logger.error(f"Failed to send Slack alert: {e}")
