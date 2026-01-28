"""
Slack notifier - send alerts via Slack
"""

import json
import requests
from src.utils.config import Config
from src.utils.logging import get_logger

logger = get_logger("alerts.slack_notifier")


class SlackNotifier:
    """Send notifications to Slack"""
    
    def __init__(self, webhook_url=None):
        self.logger = logger
        self.webhook_url = webhook_url or Config.SLACK_WEBHOOK_URL
    
    def send_message(self, message, channel=None):
        """
        Send a plain text message to Slack
        
        Args:
            message: str, message content
            channel: str, channel name (optional)
        
        Returns:
            bool: success
        """
        if not self.webhook_url:
            self.logger.warning("Slack webhook URL not configured")
            return False
        
        payload = {
            "text": message,
        }
        
        if channel:
            payload["channel"] = channel
        
        try:
            response = requests.post(self.webhook_url, json=payload)
            if response.status_code == 200:
                self.logger.debug("✓ Slack message sent")
                return True
            else:
                self.logger.error(f"Slack error: {response.status_code}")
                return False
        
        except Exception as e:
            self.logger.error(f"Failed to send Slack message: {str(e)}")
            return False
    
    def send_trade_alert(self, ticker, play, confidence, price):
        """
        Send formatted trade alert
        
        Args:
            ticker: str, stock ticker
            play: str, play type
            confidence: float, confidence score
            price: float, current price
        
        Returns:
            bool: success
        """
        message = f"""
🚀 *NEW TRADE ALERT*
Ticker: `{ticker}`
Play: {play}
Confidence: {confidence:.0f}%
Price: ${price:.2f}
"""
        return self.send_message(message)
    
    def send_weekly_report(self, report_text):
        """
        Send weekly summary report
        
        Args:
            report_text: str, formatted report
        
        Returns:
            bool: success
        """
        return self.send_message(report_text)


if __name__ == "__main__":
    notifier = SlackNotifier()
    
    # Test message (will only send if webhook is configured)
    notifier.send_message("✓ Slack notifier initialized")
