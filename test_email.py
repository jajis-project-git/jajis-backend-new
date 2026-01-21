
"""
Email Configuration Test Script
Run this on Railway to verify email setup:
python test_email.py
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Jajis_project.settings")
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.conf import settings
from django.core.mail import send_mail, get_connection
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_email_settings():
    print("\n" + "="*60)
    print("EMAIL CONFIGURATION TEST")
    print("="*60)
    
    print(f"\n✓ EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"✓ EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"✓ EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"✓ EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"✓ EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"✓ DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    
    # Test connection
    print("\n" + "="*60)
    print("TESTING CONNECTION...")
    print("="*60)
    
    try:
        connection = get_connection()
        connection.open()
        print("✓ Connection successful!")
        connection.close()
    except Exception as e:
        print(f"✗ Connection failed: {str(e)}")
        return False
    
    # Test sending email
    print("\n" + "="*60)
    print("SENDING TEST EMAIL...")
    print("="*60)
    
    try:
        send_mail(
            subject="Jaji's Email Test",
            message="This is a test email to verify SMTP configuration.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            html_message="<h2>Jaji's Email Test</h2><p>This is a test email to verify SMTP configuration is working correctly.</p>",
            fail_silently=False,
        )
        print("✓ Test email sent successfully!")
        return True
    except Exception as e:
        print(f"✗ Test email failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_email_settings()
    print("\n" + "="*60)
    if success:
        print("✓ EMAIL CONFIGURATION IS WORKING CORRECTLY")
    else:
        print("✗ EMAIL CONFIGURATION HAS ISSUES - CHECK LOGS ABOVE")
    print("="*60 + "\n")
    sys.exit(0 if success else 1)
