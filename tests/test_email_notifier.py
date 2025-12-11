import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, AsyncMock
import unittest
import asyncio

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from services.email_notifier import EmailNotifier
from services.alerts import Alert


class TestEmailNotifier(unittest.TestCase):
    
    def setUp(self):
        self.alert = Alert(
            level="critical",
            message="Test alert message",
            timestamp=datetime.now(),
            node_name="test-node",
            metric_name="test_metric"
        )

    @patch("services.email_notifier.aiosmtplib.send", new_callable=AsyncMock)
    @patch("services.email_notifier.SENDER_EMAIL", "test@example.com")
    @patch("services.email_notifier.SENDER_PASSWORD", "secret")
    @patch("services.email_notifier.ALERT_EMAIL_RECIPIENTS", ["admin@example.com"])
    def test_send_alert_success(self, mock_send):
        """Test successful email sending."""
        
        # Run async function in sync test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(EmailNotifier.send_alert(self.alert))
        loop.close()

        self.assertTrue(result)
        mock_send.assert_called_once()
        
        # Verify message content arguments
        call_args = mock_send.call_args
        message = call_args[0][0]
        self.assertIn("[CRITICAL]", message["Subject"])
        self.assertEqual(message["To"], "admin@example.com")
        print("✓ Email send success test passed")

    @patch("services.email_notifier.aiosmtplib.send", new_callable=AsyncMock)
    @patch("services.email_notifier.SENDER_EMAIL", "") # Empty credentials
    def test_send_alert_no_creds(self, mock_send):
        """Test graceful failure when credentials missing."""
        
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(EmailNotifier.send_alert(self.alert))
        loop.close()

        self.assertFalse(result)
        mock_send.assert_not_called()
        print("✓ Missing credentials test passed")

    @patch("services.email_notifier.aiosmtplib.send", side_effect=Exception("SMTP Error"))
    @patch("services.email_notifier.SENDER_EMAIL", "test@example.com")
    @patch("services.email_notifier.SENDER_PASSWORD", "secret")
    @patch("services.email_notifier.ALERT_EMAIL_RECIPIENTS", ["admin@example.com"])
    def test_send_alert_exception(self, mock_send):
        """Test handling of SMTP exceptions."""
        
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(EmailNotifier.send_alert(self.alert))
        loop.close()

        self.assertFalse(result)
        print("✓ Exception handling test passed")


if __name__ == '__main__':
    unittest.main()
