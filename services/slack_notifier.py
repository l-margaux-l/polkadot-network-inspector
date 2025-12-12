import logging
import aiohttp

from config import SLACK_WEBHOOK_URL
from services.alerts import Alert

logger = logging.getLogger(__name__)


class SlackNotifier:
    """Sends alert notifications to Slack via webhook."""

    EMOJI_MAP = {
        "critical": "🔴",
        "warning": "🟡",
        "info": "🟢",
    }

    @staticmethod
    async def send_alert(alert: Alert) -> bool:
        """
        Send alert to Slack channel via webhook.

        Args:
            alert: The Alert object containing notification details.

        Returns:
            bool: True if sent successfully, False otherwise.
        """
        if not SLACK_WEBHOOK_URL:
            logger.warning("Slack webhook URL not configured. Skipping notification.")
            return False

        payload = SlackNotifier._build_payload(alert)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    SLACK_WEBHOOK_URL,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status == 200:
                        logger.info(f"Slack alert sent for {alert.node_name}")
                        return True
                    else:
                        logger.error(
                            f"Slack webhook returned status {response.status}"
                        )
                        return False

        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
            return False

    @staticmethod
    def _build_payload(alert: Alert) -> dict:
        """Build Slack message payload with formatting."""
        emoji = SlackNotifier.EMOJI_MAP.get(alert.level, "⚪")
        color = {
            "critical": "#FF0000",
            "warning": "#FFA500",
            "info": "#00FF00",
        }.get(alert.level, "#808080")

        return {
            "text": f"{emoji} {alert.level.upper()} Alert",
            "attachments": [
                {
                    "color": color,
                    "title": f"Node: {alert.node_name}",
                    "fields": [
                        {
                            "title": "Metric",
                            "value": alert.metric_name,
                            "short": True,
                        },
                        {
                            "title": "Level",
                            "value": alert.level.upper(),
                            "short": True,
                        },
                        {
                            "title": "Details",
                            "value": alert.message,
                            "short": False,
                        },
                        {
                            "title": "Timestamp",
                            "value": alert.timestamp.isoformat(),
                            "short": False,
                        },
                    ],
                }
            ],
        }
