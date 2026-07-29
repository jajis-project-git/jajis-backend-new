from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_order_success_email(user, order, order_items):
    subject = f"Order Confirmation – Order #{order.id}"

    # -------- Plain text fallback (important) --------
    text_message = f"""
Hello {user.get_full_name() or user.username},

Your payment was successful.

Order ID: {order.id}
Total Amount: ₹{order.total_amount}

Thank you for shopping with us.
"""

    # -------- Build items HTML --------
    items_html = ""
    for item in order_items:
        items_html += f"""
        <tr>
            <td style="padding:10px 0;">{item.variant.product.title}<br>
                <span style="color:#6b7280;font-size:13px;">
                    {item.variant.quantity_label}
                </span>
            </td>
            <td style="text-align:center;">{item.quantity}</td>
            <td style="text-align:right;">₹{item.total_price}</td>
        </tr>
        """

    # -------- Premium HTML email --------
    html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Order Confirmation</title>
</head>
<body style="margin:0;padding:0;background-color:#f4f6f8;font-family:Arial,Helvetica,sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0">
<tr>
<td align="center" style="padding:40px 15px;">

    <!-- Card -->
    <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;padding:30px;box-shadow:0 10px 30px rgba(0,0,0,0.08);">

        <!-- Header -->
        <tr>
            <td style="text-align:center;padding-bottom:25px;">
                <h1 style="margin:0;font-size:26px;color:#111827;">
                    Payment Successful 🎉
                </h1>
                <p style="margin:8px 0 0;color:#6b7280;">
                    Thank you for your purchase
                </p>
            </td>
        </tr>

        <!-- Divider -->
        <tr><td style="border-top:1px solid #e5e7eb;"></td></tr>

        <!-- Order Info -->
        <tr>
            <td style="padding:25px 0;">
                <h3 style="margin:0 0 12px;color:#111827;">Order Details</h3>
                <table width="100%">
                    <tr><td>Order ID</td><td align="right">#{order.id}</td></tr>
                    <tr><td>Payment ID</td><td align="right">{order.transaction_id}</td></tr>
                    <tr><td>Payment Method</td><td align="right">{order.payment_method}</td></tr>
                    <tr><td>Status</td><td align="right" style="color:#16a34a;font-weight:bold;">Paid</td></tr>
                    <tr><td><strong>Total</strong></td><td align="right"><strong>₹{order.total_amount}</strong></td></tr>
                </table>
            </td>
        </tr>

        <!-- Divider -->
        <tr><td style="border-top:1px solid #e5e7eb;"></td></tr>

        <!-- Shipping -->
        <tr>
            <td style="padding:25px 0;">
                <h3 style="margin:0 0 12px;color:#111827;">Shipping Address</h3>
                <p style="margin:0;color:#374151;line-height:1.6;">
                    {user.get_full_name() or user.username}<br>
                    {order.shipping_address.line1}<br>
                    {order.shipping_address.line2}<br>
                    {order.shipping_address.city}, {order.shipping_address.state}<br>
                    {order.shipping_address.postal_code}<br>
                    Phone: {order.shipping_address.phone}
                </p>
            </td>
        </tr>

        <!-- Divider -->
        <tr><td style="border-top:1px solid #e5e7eb;"></td></tr>

        <!-- Items -->
        <tr>
            <td style="padding:25px 0;">
                <h3 style="margin:0 0 15px;color:#111827;">Items Purchased</h3>
                <table width="100%" style="border-collapse:collapse;">
                    <tr style="border-bottom:1px solid #e5e7eb;font-weight:bold;">
                        <td>Product</td>
                        <td align="center">Qty</td>
                        <td align="right">Price</td>
                    </tr>
                    {items_html}
                </table>
            </td>
        </tr>

        <!-- Footer -->
        <tr>
            <td style="padding-top:30px;text-align:center;">
                <p style="margin:0;color:#6b7280;font-size:14px;">
                    We will notify you once your order is shipped.
                </p>
                <p style="margin:15px 0 0;font-size:13px;color:#9ca3af;">
                    © {settings.DEFAULT_FROM_EMAIL}
                </p>
                <p style="margin:15px 0 0;font-size:13px;color:#9ca3af;">
                    <a href="https://www.jajisinnovation.com" style="color:#9ca3af;text-decoration:none;">Visit www.jajisinnovation.com to see more</a>
                </p>
            </td>
        </tr>

    </table>

</td>
</tr>
</table>

</body>
</html>
"""

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email, settings.DEFAULT_FROM_EMAIL],
        )
        msg.attach_alternative(html_message, "text/html")
        msg.send(fail_silently=False)
        logger.info(f"Order confirmation email sent to {user.email} for order #{order.id}")
    except Exception as e:
        logger.error(f"Failed to send order confirmation email to {user.email}: {str(e)}", exc_info=True)


def send_password_reset_otp_email(user, otp):
    subject = "Password Reset OTP - Jaji's"

    text_message = f"""
Hello {user.get_full_name() or user.username},

Your username is: {user.username}

You requested a password reset. Your OTP is: {otp}

This OTP will expire in 10 minutes.

If you didn't request this, please ignore this email.
"""

    html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Password Reset OTP</title>
</head>
<body style="margin:0;padding:0;background-color:#f4f6f8;font-family:Arial,Helvetica,sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0">
<tr>
<td align="center" style="padding:40px 15px;">

    <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;padding:30px;box-shadow:0 10px 30px rgba(0,0,0,0.08);">
    <tr>
    <td>
        <h1 style="color:#1f2937;margin:0 0 20px 0;">Password Reset Request</h1>
        <p style="color:#6b7280;margin:0 0 15px 0;">Hello {user.get_full_name() or user.username},</p>
        <p style="color:#6b7280;margin:0 0 15px 0;">Your username is: <strong>{user.username}</strong></p>
        <p style="color:#6b7280;margin:0 0 15px 0;">You requested a password reset. Your OTP is:</p>
        <div style="background:#f3f4f6;padding:20px;text-align:center;border-radius:8px;margin:20px 0;">
            <span style="font-size:24px;font-weight:bold;color:#1f2937;">{otp}</span>
        </div>
        <p style="color:#6b7280;margin:0 0 15px 0;">This OTP will expire in 10 minutes.</p>
        <p style="color:#6b7280;margin:0;">If you didn't request this, please ignore this email.</p>
    </td>
    </tr>
    </table>

</td>
</tr>
</table>

</body>
</html>
"""

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        msg.attach_alternative(html_message, "text/html")
        msg.send(fail_silently=False)
        logger.info(f"Password reset OTP email sent to {user.email}")
    except Exception as e:
        logger.error(f"Failed to send password reset OTP email to {user.email}: {str(e)}", exc_info=True)


def send_event_hall_user_email(event_hall):
    subject = "Event Hall Booking Request Received - Jaji's"
    event_type_label = dict(event_hall.type_choice).get(event_hall.event_type, event_hall.event_type)
    category_label = dict(event_hall.category_choice).get(event_hall.category, event_hall.category)
    date_str = event_hall.event_date.strftime("%B %d, %Y") if hasattr(event_hall.event_date, 'strftime') else str(event_hall.event_date)

    text_message = f"""
Hello {event_hall.name},

Thank you for your interest in Jaji's Event Hall! We have received your booking enquiry.

Here are your submitted details:
- Name: {event_hall.name}
- Phone: {event_hall.phone}
- Email: {event_hall.email}
- Event Type: {event_type_label}
- Category: {category_label}
- Requested Event Date: {date_str}

Our team will review your request and get in touch with you soon to confirm your booking.

Best regards,
Jaji's Team
"""

    html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Event Hall Booking Request Received</title>
</head>
<body style="margin:0;padding:0;background-color:#f4f6f8;font-family:Arial,Helvetica,sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0">
<tr>
<td align="center" style="padding:40px 15px;">

    <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;padding:30px;box-shadow:0 10px 30px rgba(0,0,0,0.08);">
        <tr>
            <td style="text-align:center;padding-bottom:20px;">
                <h1 style="margin:0;font-size:24px;color:#111827;">Booking Enquiry Received 🎉</h1>
                <p style="margin:8px 0 0;color:#6b7280;">Thank you for reaching out to Jaji's Event Hall</p>
            </td>
        </tr>
        <tr><td style="border-top:1px solid #e5e7eb;"></td></tr>
        <tr>
            <td style="padding:25px 0;">
                <h3 style="margin:0 0 15px;color:#111827;">Enquiry Details</h3>
                <table width="100%" style="border-collapse:collapse;font-size:14px;color:#374151;">
                    <tr style="border-bottom:1px solid #f3f4f6;"><td style="padding:8px 0;"><strong>Name:</strong></td><td align="right">{event_hall.name}</td></tr>
                    <tr style="border-bottom:1px solid #f3f4f6;"><td style="padding:8px 0;"><strong>Phone:</strong></td><td align="right">{event_hall.phone}</td></tr>
                    <tr style="border-bottom:1px solid #f3f4f6;"><td style="padding:8px 0;"><strong>Email:</strong></td><td align="right">{event_hall.email}</td></tr>
                    <tr style="border-bottom:1px solid #f3f4f6;"><td style="padding:8px 0;"><strong>Event Type:</strong></td><td align="right">{event_type_label}</td></tr>
                    <tr style="border-bottom:1px solid #f3f4f6;"><td style="padding:8px 0;"><strong>Category:</strong></td><td align="right">{category_label}</td></tr>
                    <tr><td style="padding:8px 0;"><strong>Requested Event Date:</strong></td><td align="right" style="color:#2563eb;font-weight:bold;">{date_str}</td></tr>
                </table>
            </td>
        </tr>
        <tr><td style="border-top:1px solid #e5e7eb;"></td></tr>
        <tr>
            <td style="padding-top:25px;text-align:center;color:#6b7280;font-size:14px;">
                <p style="margin:0;">Our event coordinator will contact you shortly to confirm the availability and discuss details.</p>
                <p style="margin:15px 0 0;font-size:13px;color:#9ca3af;">© Jaji's Innovation</p>
            </td>
        </tr>
    </table>

</td>
</tr>
</table>

</body>
</html>
"""

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[event_hall.email],
        )
        msg.attach_alternative(html_message, "text/html")
        msg.send(fail_silently=False)
        logger.info(f"Event hall confirmation email sent to user {event_hall.email}")
    except Exception as e:
        logger.error(f"Failed to send event hall email to user {event_hall.email}: {str(e)}", exc_info=True)


def send_event_hall_admin_email(event_hall):
    admin_email = "managingdirector@jajis.in"
    subject = f"New Event Hall Booking Enquiry - {event_hall.name}"
    event_type_label = dict(event_hall.type_choice).get(event_hall.event_type, event_hall.event_type)
    category_label = dict(event_hall.category_choice).get(event_hall.category, event_hall.category)
    date_str = event_hall.event_date.strftime("%B %d, %Y") if hasattr(event_hall.event_date, 'strftime') else str(event_hall.event_date)

    text_message = f"""
New Event Hall Booking Enquiry Received!

Details:
- Customer Name: {event_hall.name}
- Phone: {event_hall.phone}
- Email: {event_hall.email}
- Event Type: {event_type_label}
- Category: {category_label}
- Event Date: {date_str}

Please log in to the admin panel to review and manage this lead.
"""

    html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>New Event Hall Enquiry</title>
</head>
<body style="margin:0;padding:0;background-color:#f4f6f8;font-family:Arial,Helvetica,sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0">
<tr>
<td align="center" style="padding:40px 15px;">

    <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;padding:30px;box-shadow:0 10px 30px rgba(0,0,0,0.08);">
        <tr>
            <td style="text-align:center;padding-bottom:20px;">
                <h1 style="margin:0;font-size:24px;color:#111827;">New Event Hall Lead 📩</h1>
                <p style="margin:8px 0 0;color:#6b7280;">Enquiry submitted on website</p>
            </td>
        </tr>
        <tr><td style="border-top:1px solid #e5e7eb;"></td></tr>
        <tr>
            <td style="padding:25px 0;">
                <h3 style="margin:0 0 15px;color:#111827;">Customer & Booking Details</h3>
                <table width="100%" style="border-collapse:collapse;font-size:14px;color:#374151;">
                    <tr style="border-bottom:1px solid #f3f4f6;"><td style="padding:8px 0;"><strong>Customer Name:</strong></td><td align="right">{event_hall.name}</td></tr>
                    <tr style="border-bottom:1px solid #f3f4f6;"><td style="padding:8px 0;"><strong>Phone Number:</strong></td><td align="right"><a href="tel:{event_hall.phone}" style="color:#2563eb;">{event_hall.phone}</a></td></tr>
                    <tr style="border-bottom:1px solid #f3f4f6;"><td style="padding:8px 0;"><strong>Email Address:</strong></td><td align="right"><a href="mailto:{event_hall.email}" style="color:#2563eb;">{event_hall.email}</a></td></tr>
                    <tr style="border-bottom:1px solid #f3f4f6;"><td style="padding:8px 0;"><strong>Event Type:</strong></td><td align="right">{event_type_label}</td></tr>
                    <tr style="border-bottom:1px solid #f3f4f6;"><td style="padding:8px 0;"><strong>Category:</strong></td><td align="right">{category_label}</td></tr>
                    <tr><td style="padding:8px 0;"><strong>Requested Event Date:</strong></td><td align="right" style="color:#dc2626;font-weight:bold;">{date_str}</td></tr>
                </table>
            </td>
        </tr>
        <tr><td style="border-top:1px solid #e5e7eb;"></td></tr>
        <tr>
            <td style="padding-top:25px;text-align:center;color:#6b7280;font-size:14px;">
                <p style="margin:0;">This lead is saved in the e-commerce admin panel.</p>
            </td>
        </tr>
    </table>

</td>
</tr>
</table>

</body>
</html>
"""

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[admin_email],
        )
        msg.attach_alternative(html_message, "text/html")
        msg.send(fail_silently=False)
        logger.info(f"Event hall admin notification email sent to {admin_email}")
    except Exception as e:
        logger.error(f"Failed to send event hall email to admin {admin_email}: {str(e)}", exc_info=True)

