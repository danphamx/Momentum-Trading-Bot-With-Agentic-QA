"""
Email notifier - send alerts via email
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.utils.config import Config
from src.utils.logging import get_logger

logger = get_logger("alerts.email_notifier")


class EmailNotifier:
    """Send notifications via email"""
    
    def __init__(self, sender_email=None, sender_password=None):
        self.logger = logger
        self.sender_email = sender_email or Config.EMAIL_ADDRESS
        self.sender_password = sender_password or Config.EMAIL_PASSWORD
    
    def send_email(self, recipient, subject, body, is_html=False):
        """
        Send an email
        
        Args:
            recipient: str or list, recipient email(s)
            subject: str, email subject
            body: str, email body
            is_html: bool, whether body is HTML
        
        Returns:
            bool: success
        """
        if not self.sender_email or not self.sender_password:
            self.logger.warning("Email credentials not configured")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = recipient if isinstance(recipient, str) else ', '.join(recipient)
            
            content_type = 'html' if is_html else 'plain'
            msg.attach(MIMEText(body, content_type))
            
            # Connect and send
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(self.sender_email, self.sender_password)
                server.sendmail(
                    self.sender_email,
                    recipient if isinstance(recipient, str) else recipient,
                    msg.as_string()
                )
            
            self.logger.debug(f"✓ Email sent to {recipient}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to send email: {str(e)}")
            return False
    
    def send_trade_alert(self, recipient, ticker, play, confidence, price):
        """
        Send formatted trade alert email
        
        Args:
            recipient: str, recipient email
            ticker: str, stock ticker
            play: str, play type
            confidence: float, confidence score
            price: float, current price
        
        Returns:
            bool: success
        """
        subject = f"🚀 New Trade Alert: {ticker}"
        
        body = f"""
<h2>New Trade Opportunity</h2>

<p><strong>Ticker:</strong> {ticker}</p>
<p><strong>Play:</strong> {play}</p>
<p><strong>Confidence:</strong> {confidence:.0f}%</p>
<p><strong>Entry Price:</strong> ${price:.2f}</p>

<hr>

<p>This trade passed Alpha Agent filters and technical analysis.</p>
"""
        
        return self.send_email(recipient, subject, body, is_html=True)
    
    def send_weekly_report(self, recipient, report_html):
        """
        Send weekly summary report
        
        Args:
            recipient: str or list, recipient email(s)
            report_html: str, HTML formatted report
        
        Returns:
            bool: success
        """
        subject = "📊 Momentum Mastery Weekly Report"
        return self.send_email(recipient, subject, report_html, is_html=True)


if __name__ == "__main__":
    notifier = EmailNotifier()
    
    # Test (will only send if configured)
    print("✓ Email notifier initialized")
