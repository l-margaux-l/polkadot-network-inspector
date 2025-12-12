import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, AsyncMock, MagicMock
import unittest
import asyncio

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from services.slack_notifier import SlackNotifier
from services.alerts import Alert


class TestSlackNotifier(unittest.TestCase):

    def setUp(self):
        self.alert = Alert(
            level="critical",
            message="Finality lag is 75 blocks (threshold: 50)",
            timestamp=datetime.now(),
            node_name="polkadot-validator-1",
            metric_name="finality_lag"
        )

    @patch("services.slack_notifier.SLACK_WEBHOOK_URL", "https://hooks.slack.com/services/test")
    @patch("services.slack_notifier.aiohttp.ClientSession")
    def test_send_alert_success(self, mock_session_class):
        """Test successful Slack webhook POST request."""
        mock_response = AsyncMock()
        mock_response.status = 200
        
        mock_post = AsyncMock()
        mock_post.__aenter__ = AsyncMock(return_value=mock_response)
        mock_post.__aexit__ = AsyncMock(return_value=None)
        
        mock_session = AsyncMock()
        mock_session.post = MagicMock(return_value=mock_post)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_class.return_value = mock_session

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(SlackNotifier.send_alert(self.alert))
        loop.close()

        self.assertTrue(result)
        print("✓ Slack send success test passed")

    @patch("services.slack_notifier.SLACK_WEBHOOK_URL", "https://hooks.slack.com/services/test")
    @patch("services.slack_notifier.aiohttp.ClientSession")
    def test_send_alert_webhook_error(self, mock_session_class):
        """Test Slack webhook returning error status."""
        mock_response = AsyncMock()
        mock_response.status = 400
        
        mock_post = AsyncMock()
        mock_post.__aenter__ = AsyncMock(return_value=mock_response)
        mock_post.__aexit__ = AsyncMock(return_value=None)
        
        mock_session = AsyncMock()
        mock_session.post = MagicMock(return_value=mock_post)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_class.return_value = mock_session

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(SlackNotifier.send_alert(self.alert))
        loop.close()

        self.assertFalse(result)
        print("✓ Webhook error handling test passed")

    @patch("services.slack_notifier.SLACK_WEBHOOK_URL", "")
    def test_send_alert_no_webhook(self):
        """Test graceful failure when webhook URL not configured."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(SlackNotifier.send_alert(self.alert))
        loop.close()

        self.assertFalse(result)
        print("✓ Missing webhook test passed")

    def test_payload_structure(self):
        """Test that payload has correct structure for Slack."""
        payload = SlackNotifier._build_payload(self.alert)

        self.assertIn("text", payload)
        self.assertIn("attachments", payload)
        self.assertEqual(len(payload["attachments"]), 1)
        
        attachment = payload["attachments"][0]
        self.assertIn("color", attachment)
        self.assertIn("title", attachment)
        self.assertIn("fields", attachment)
        self.assertEqual(len(attachment["fields"]), 4)
        
        print("✓ Payload structure test passed")

    def test_emoji_mapping(self):
        """Test correct emoji selection for alert levels."""
        self.assertEqual(SlackNotifier.EMOJI_MAP["critical"], "🔴")
        self.assertEqual(SlackNotifier.EMOJI_MAP["warning"], "🟡")
        self.assertEqual(SlackNotifier.EMOJI_MAP["info"], "🟢")
        print("✓ Emoji mapping test passed")


if __name__ == '__main__':
    unittest.main()
