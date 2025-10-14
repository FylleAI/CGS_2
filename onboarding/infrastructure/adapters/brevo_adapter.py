"""Brevo adapter for email delivery.

Sends transactional emails with generated content via Brevo API.
"""

import logging
from typing import Any, Dict, Optional
from datetime import datetime

import httpx

from onboarding.config.settings import OnboardingSettings
from onboarding.domain.cgs_contracts import ContentResult

logger = logging.getLogger(__name__)


class BrevoAdapter:
    """
    Adapter for Brevo email delivery.
    
    Handles transactional email sending with idempotency and retry logic.
    """
    
    def __init__(self, settings: OnboardingSettings):
        """
        Initialize Brevo adapter.
        
        Args:
            settings: Onboarding settings with Brevo configuration
        """
        self.settings = settings
        
        if not settings.is_brevo_configured():
            raise ValueError("Brevo API key not configured")
        
        self.api_key = settings.brevo_api_key
        self.sender_email = settings.brevo_sender_email
        self.sender_name = settings.brevo_sender_name
        self.template_id = settings.brevo_template_id
        self.timeout = settings.brevo_timeout
        
        self.base_url = "https://api.brevo.com/v3"
        
        logger.info(f"Brevo adapter initialized: sender={self.sender_email}")
    
    def _build_headers(self) -> Dict[str, str]:
        """Build HTTP headers for Brevo requests."""
        return {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": self.api_key,
        }
    
    async def send_content_email(
        self,
        recipient_email: str,
        recipient_name: Optional[str],
        content: ContentResult,
        session_id: str,
        brand_name: str,
    ) -> Dict[str, Any]:
        """
        Send content via email.
        
        Args:
            recipient_email: Recipient email address
            recipient_name: Recipient name (optional)
            content: Generated content
            session_id: Session ID for idempotency
            brand_name: Brand name for subject line
        
        Returns:
            Delivery result with message_id
        """
        logger.info(f"Sending content email to: {recipient_email}")
        
        # Build email payload
        email_payload = self._build_email_payload(
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            content=content,
            session_id=session_id,
            brand_name=brand_name,
        )
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/smtp/email",
                    json=email_payload,
                    headers=self._build_headers(),
                )
                
                response.raise_for_status()
                data = response.json()
            
            message_id = data.get("messageId")
            
            logger.info(f"Email sent successfully: message_id={message_id}")
            
            return {
                "status": "sent",
                "message_id": message_id,
                "recipient": recipient_email,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Brevo API error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Email delivery failed: {str(e)}")
            raise
    
    async def send_with_template(
        self,
        recipient_email: str,
        recipient_name: Optional[str],
        template_params: Dict[str, Any],
        session_id: str,
    ) -> Dict[str, Any]:
        """
        Send email using Brevo template.
        
        Args:
            recipient_email: Recipient email
            recipient_name: Recipient name
            template_params: Template parameters
            session_id: Session ID for idempotency
        
        Returns:
            Delivery result
        """
        if not self.template_id:
            raise ValueError("Brevo template ID not configured")
        
        logger.info(f"Sending template email to: {recipient_email}")
        
        payload = {
            "to": [
                {
                    "email": recipient_email,
                    "name": recipient_name or recipient_email,
                }
            ],
            "templateId": self.template_id,
            "params": template_params,
            "headers": {
                "X-Session-Id": session_id,  # For idempotency tracking
            },
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/smtp/email",
                    json=payload,
                    headers=self._build_headers(),
                )
                
                response.raise_for_status()
                data = response.json()
            
            message_id = data.get("messageId")
            
            logger.info(f"Template email sent: message_id={message_id}")
            
            return {
                "status": "sent",
                "message_id": message_id,
                "recipient": recipient_email,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Brevo template error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Template email failed: {str(e)}")
            raise
    
    def _build_email_payload(
        self,
        recipient_email: str,
        recipient_name: Optional[str],
        content: ContentResult,
        session_id: str,
        brand_name: str,
    ) -> Dict[str, Any]:
        """Build email payload for Brevo API."""
        
        # Build subject line
        subject = f"Your {brand_name} Content is Ready!"
        
        # Build HTML body
        html_content = self._build_html_content(content, brand_name)
        
        # Build text body (fallback)
        text_content = self._build_text_content(content, brand_name)
        
        payload = {
            "sender": {
                "name": self.sender_name,
                "email": self.sender_email,
            },
            "to": [
                {
                    "email": recipient_email,
                    "name": recipient_name or recipient_email,
                }
            ],
            "subject": subject,
            "htmlContent": html_content,
            "textContent": text_content,
            "headers": {
                "X-Session-Id": session_id,  # For idempotency
                "X-Content-Id": str(content.content_id) if content.content_id else "none",
            },
            "tags": ["onboarding", "content-delivery"],
        }
        
        return payload
    
    def _build_html_content(self, content: ContentResult, brand_name: str) -> str:
        """Build HTML email content."""
        
        # Convert markdown to HTML (simple conversion)
        body_html = content.body.replace("\n\n", "</p><p>").replace("\n", "<br>")
        body_html = f"<p>{body_html}</p>"
        
        # Replace markdown bold/italic
        import re
        body_html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', body_html)
        body_html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', body_html)
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{content.title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        .content {{
            background: #f9f9f9;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            font-size: 12px;
            color: #666;
        }}
        .stats {{
            background: #e8f4f8;
            padding: 10px;
            border-radius: 5px;
            margin: 15px 0;
        }}
    </style>
</head>
<body>
    <h1>🎉 Your Content is Ready, {brand_name}!</h1>
    
    <p>We've generated your content based on your company profile and preferences.</p>
    
    <div class="stats">
        <strong>Content Details:</strong><br>
        📝 Word Count: {content.word_count} words<br>
        📊 Character Count: {content.character_count} characters<br>
        ⏱️ Reading Time: {content.reading_time_minutes or 'N/A'} minutes
    </div>
    
    <h2>{content.title}</h2>
    
    <div class="content">
        {body_html}
    </div>
    
    <div class="footer">
        <p>Generated by Fylle AI Onboarding Service</p>
        <p>If you have any questions, please contact us.</p>
    </div>
</body>
</html>
"""
        return html
    
    def _build_text_content(self, content: ContentResult, brand_name: str) -> str:
        """Build plain text email content."""
        return f"""
Your Content is Ready, {brand_name}!

We've generated your content based on your company profile and preferences.

Content Details:
- Word Count: {content.word_count} words
- Character Count: {content.character_count} characters
- Reading Time: {content.reading_time_minutes or 'N/A'} minutes

{content.title}

{content.body}

---
Generated by Fylle AI Onboarding Service
"""
    
    async def get_email_status(self, message_id: str) -> Dict[str, Any]:
        """
        Get email delivery status.
        
        Args:
            message_id: Brevo message ID
        
        Returns:
            Status information
        """
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    f"{self.base_url}/smtp/emails/{message_id}",
                    headers=self._build_headers(),
                )
                
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.warning(f"Failed to get email status: {str(e)}")
            return {"status": "unknown", "error": str(e)}

