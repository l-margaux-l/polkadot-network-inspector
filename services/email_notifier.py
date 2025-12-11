import logging
from email.message import EmailMessage

import aiosmtplib

from config import (
    SMTP_SERVER,
    SMTP_PORT,
    SENDER_EMAIL,
    SENDER_PASSWORD,
    ALERT_EMAIL_RECIPIENTS,
)
from services.alerts import Alert

logger = logging.getLogger(__name__)


class EmailNotifier:
    """Handles sending email alerts asynchronously."""

    @staticmethod
    async def send_alert(alert: Alert) -> bool:
        """
        Send an email alert to configured recipients.

        Args:
            alert: The Alert object containing details.

        Returns:
            bool: True if sent successfully, False otherwise.
        """
        if not SENDER_EMAIL or not SENDER_PASSWORD:
            logger.warning("Email credentials not set. Skipping email alert.")
            return False

        if not ALERT_EMAIL_RECIPIENTS or ALERT_EMAIL_RECIPIENTS == [""]:
            logger.warning("No email recipients configured. Skipping email alert.")
            return False

        subject = f"[{alert.level.upper()}] Polkadot Node Alert: {alert.node_name}"
        body = (
            f"Alert Level: {alert.level.upper()}\n"
            f"Node: {alert.node_name}\n"
            f"Metric: {alert.metric_name}\n"
            f"Time: {alert.timestamp}\n\n"
            f"Message:\n{alert.message}\n"
        )

        message = EmailMessage()
        message["From"] = SENDER_EMAIL
        message["To"] = ", ".join(ALERT_EMAIL_RECIPIENTS)
        message["Subject"] = subject
        message.set_content(body)

        try:
            await aiosmtplib.send(
                message,
                hostname=SMTP_SERVER,
                port=SMTP_PORT,
                username=SENDER_EMAIL,
                password=SENDER_PASSWORD,
                start_tls=True,
            )
            logger.info(f"Email alert sent to {len(ALERT_EMAIL_RECIPIENTS)} recipients")
            return True

        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return False
