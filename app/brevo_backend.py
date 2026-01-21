import requests
import logging
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings

logger = logging.getLogger(__name__)


class BrevoEmailBackend(BaseEmailBackend):
    """
    Custom email backend for sending emails via Brevo (formerly Sendinblue) API
    """

    def __init__(self, fail_silently=False):
        super().__init__(fail_silently=fail_silently)
        self.api_key = settings.BREVO_API_KEY
        self.api_url = "https://api.brevo.com/v3/smtp/email"

    def send_messages(self, email_messages):
        """
        Send email messages via Brevo API
        """
        if not email_messages:
            return 0

        msg_count = 0
        for message in email_messages:
            try:
                headers = {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "api-key": self.api_key,
                }

                # Handle both single recipient and multiple recipients
                to_list = []
                for recipient in message.to:
                    to_list.append({"email": recipient})

                # Build the payload
                payload = {
                    "sender": {
                        "name": settings.DEFAULT_FROM_EMAIL.split("@")[0],
                        "email": settings.DEFAULT_FROM_EMAIL,
                    },
                    "to": to_list,
                    "subject": message.subject,
                    "textContent": message.body,
                }

                # Add HTML content if available
                if hasattr(message, "alternatives"):
                    for alternative, mimetype in message.alternatives:
                        if mimetype == "text/html":
                            payload["htmlContent"] = alternative
                            break
                else:
                    # Try to get html_message from the message object
                    if hasattr(message, 'extra_headers') and 'html_message' in message.extra_headers:
                        payload["htmlContent"] = message.extra_headers['html_message']

                # Add CC and BCC if present
                if message.cc:
                    payload["cc"] = [{"email": cc} for cc in message.cc]

                if message.bcc:
                    payload["bcc"] = [{"email": bcc} for bcc in message.bcc]

                # Make the API request
                response = requests.post(
                    self.api_url,
                    json=payload,
                    headers=headers,
                    timeout=30
                )

                if response.status_code in [200, 201]:
                    logger.info(f"Email sent successfully via Brevo to {message.to}")
                    msg_count += 1
                else:
                    error_msg = f"Brevo API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    if not self.fail_silently:
                        raise Exception(error_msg)

            except Exception as e:
                logger.error(f"Failed to send email via Brevo: {str(e)}", exc_info=True)
                if not self.fail_silently:
                    raise

        return msg_count
