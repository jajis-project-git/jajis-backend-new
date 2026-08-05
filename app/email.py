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


def send_franchise_user_email(enquiry):
    subject = "Thank You for Your Jaji’s Franchise Enquiry"

    text_message = f"""
Dear {enquiry.full_name},

Thank you for your interest in becoming a Jaji’s franchise partner.

Our franchise development team will review your application details for {enquiry.preferred_city} and contact shortlisted applicants for an initial discussion.

Submission of this form does not constitute a franchise agreement or guarantee franchise approval.

Best regards,
Jaji’s Innovation Pvt. Ltd.
www.jajisinnovation.com
"""

    html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Franchise Enquiry Confirmation</title>
</head>
<body style="margin:0;padding:0;background-color:#f4f6f8;font-family:Arial,Helvetica,sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0">
<tr>
<td align="center" style="padding:40px 15px;">

    <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;padding:30px;box-shadow:0 10px 30px rgba(0,0,0,0.08);">
        <tr>
            <td style="text-align:center;padding-bottom:20px;">
                <h1 style="margin:0;font-size:24px;color:#111827;">Thank You for Your Enquiry! ✨</h1>
                <p style="margin:8px 0 0;color:#6b7280;">Jaji’s Official Partner Program</p>
            </td>
        </tr>
        <tr><td style="border-top:1px solid #e5e7eb;"></td></tr>
        <tr>
            <td style="padding:25px 0;">
                <p style="margin:0 0 15px;color:#374151;font-size:15px;line-height:1.6;">
                    Dear <strong>{enquiry.full_name}</strong>,
                </p>
                <p style="margin:0 0 15px;color:#374151;font-size:15px;line-height:1.6;">
                    Thank you for expressing your interest in joining the Jaji’s franchise network. We have received your application for <strong>{enquiry.preferred_city}, {enquiry.state}</strong>.
                </p>
                <p style="margin:0 0 15px;color:#374151;font-size:15px;line-height:1.6;">
                    Our franchise development team will review your application details and reach out to shortlisted applicants for an initial discussion.
                </p>
            </td>
        </tr>
        <tr><td style="border-top:1px solid #e5e7eb;"></td></tr>
        <tr>
            <td style="padding-top:25px;text-align:center;color:#6b7280;font-size:13px;">
                <p style="margin:0;font-weight:bold;color:#111827;">Jaji’s Innovation Pvt. Ltd.</p>
                <p style="margin:4px 0 0;">Growing together. Creating successful beauty businesses.</p>
                <p style="margin:12px 0 0;">
                    <a href="https://www.jajisinnovation.com" style="color:#2563eb;text-decoration:none;">www.jajisinnovation.com</a>
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
            to=[enquiry.email],
        )
        msg.attach_alternative(html_message, "text/html")
        msg.send(fail_silently=False)
        logger.info(f"Franchise confirmation email sent to user {enquiry.email}")
    except Exception as e:
        logger.error(f"Failed to send franchise email to user {enquiry.email}: {str(e)}", exc_info=True)


def send_franchise_admin_email(enquiry):
    admin_email = "managingdirector@jajis.in"
    subject = f"New Franchise Partner Enquiry - {enquiry.full_name} ({enquiry.preferred_city})"

    text_message = f"""
New Franchise Partner Enquiry Received!

Personal Details:
- Full Name: {enquiry.full_name}
- Mobile Number: {enquiry.mobile_number}
- WhatsApp Number: {enquiry.whatsapp_number or 'N/A'}
- Email: {enquiry.email}
- Age Group: {enquiry.age_group}
- Current Location: {enquiry.current_city_district}, {enquiry.state}

Business Information:
- Current Occupation: {enquiry.occupation}
- Previous Business Exp: {enquiry.has_business_exp}
- Business Exp Details: {enquiry.business_exp_details or 'N/A'}
- Salon/Beauty Industry Exp: {enquiry.has_salon_exp}
- Applicant Type: {enquiry.applicant_type}

Proposed Location:
- Preferred City/Town: {enquiry.preferred_city}
- Preferred Area: {enquiry.preferred_area}
- Commercial Property Status: {enquiry.has_commercial_property}
- Property Size: {enquiry.property_size or 'N/A'}
- Property Map Link: {enquiry.property_location_link or 'N/A'}

Investment Details:
- Available Budget: {enquiry.investment_budget}
- Investment Source: {enquiry.investment_source}
- Start Timeline: {enquiry.plan_to_start}
- Daily Operations Involvement: {enquiry.daily_operations_involvement}
"""

    html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>New Franchise Enquiry</title>
</head>
<body style="margin:0;padding:0;background-color:#f4f6f8;font-family:Arial,Helvetica,sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0">
<tr>
<td align="center" style="padding:40px 15px;">

    <table width="650" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;padding:30px;box-shadow:0 10px 30px rgba(0,0,0,0.08);">
        <tr>
            <td style="text-align:center;padding-bottom:20px;">
                <h1 style="margin:0;font-size:24px;color:#111827;">New Franchise Lead 🤝</h1>
                <p style="margin:8px 0 0;color:#6b7280;">Enquiry submitted on website</p>
            </td>
        </tr>
        <tr><td style="border-top:1px solid #e5e7eb;"></td></tr>

        <!-- Personal Details -->
        <tr>
            <td style="padding:20px 0;">
                <h3 style="margin:0 0 12px;color:#111827;font-size:16px;">1. Personal Details</h3>
                <table width="100%" style="border-collapse:collapse;font-size:14px;color:#374151;">
                    <tr style="border-bottom:1px solid #f3f4f6;"><td style="padding:6px 0;"><strong>Full Name:</strong></td><td align="right">{enquiry.full_name}</td></tr>
                    <tr style="border-bottom:1px solid #f3f4f6;"><td style="padding:6px 0;"><strong>Mobile:</strong></td><td align="right"><a href="tel:{enquiry.mobile_number}" style="color:#2563eb;">{enquiry.mobile_number}</a></td></tr>
                    <tr style="border-bottom:1px solid #f3f4f6;"><td style="padding:6px 0;"><strong>WhatsApp:</strong></td><td align="right">{enquiry.whatsapp_number or 'N/A'}</td></tr>
                    <tr style="border-bottom:1px solid #f3f4f6;"><td style="padding:6px 0;"><strong>Email:</strong></td><td align="right"><a href="mailto:{enquiry.email}" style="color:#2563eb;">{enquiry.email}</a></td></tr>
                    <tr style="border-bottom:1px solid #f3f4f6;"><td style="padding:6px 0;"><strong>Age Group:</strong></td><td align="right">{enquiry.age_group}</td></tr>
                    <tr><td style="padding:6px 0;"><strong>Current City & State:</strong></td><td align="right">{enquiry.current_city_district}, {enquiry.state}</td></tr>
                </table>
            </td>
        </tr>
        <tr><td style="border-top:1px solid #e5e7eb;"></td></tr>

        <!-- Business Info -->
        <tr>
            <td style="padding:20px 0;">
                <h3 style="margin:0 0 12px;color:#111827;font-size:16px;">2. Business Information</h3>
                <table width="100%" style="border-collapse:collapse;font-size:14px;color:#374151;">
                    <tr style="border-bottom:1px solid #f3f4f6;"><td style="padding:6px 0;"><strong>Current Occupation:</strong></td><td align="right">{enquiry.occupation}</td></tr>
                    <tr style="border-bottom:1px solid #f3f4f6;"><td style="padding:6px 0;"><strong>Business Experience:</strong></td><td align="right">{enquiry.has_business_exp}</td></tr>
                    {"<tr style='border-bottom:1px solid #f3f4f6;'><td style='padding:6px 0;'><strong>Business Details:</strong></td><td align='right'>" + enquiry.business_exp_details + "</td></tr>" if enquiry.business_exp_details else ""}
                    <tr style="border-bottom:1px solid #f3f4f6;"><td style="padding:6px 0;"><strong>Salon/Beauty Exp:</strong></td><td align="right">{enquiry.has_salon_exp}</td></tr>
                    <tr><td style="padding:6px 0;"><strong>Applicant Type:</strong></td><td align="right">{enquiry.applicant_type}</td></tr>
                </table>
            </td>
        </tr>
        <tr><td style="border-top:1px solid #e5e7eb;"></td></tr>

        <!-- Location -->
        <tr>
            <td style="padding:20px 0;">
                <h3 style="margin:0 0 12px;color:#111827;font-size:16px;">3. Proposed Franchise Location</h3>
                <table width="100%" style="border-collapse:collapse;font-size:14px;color:#374151;">
                    <tr style="border-bottom:1px solid #f3f4f6;"><td style="padding:6px 0;"><strong>Preferred City:</strong></td><td align="right" style="font-weight:bold;color:#111827;">{enquiry.preferred_city}</td></tr>
                    <tr style="border-bottom:1px solid #f3f4f6;"><td style="padding:6px 0;"><strong>Preferred Area:</strong></td><td align="right">{enquiry.preferred_area}</td></tr>
                    <tr style="border-bottom:1px solid #f3f4f6;"><td style="padding:6px 0;"><strong>Commercial Property:</strong></td><td align="right">{enquiry.has_commercial_property}</td></tr>
                    <tr style="border-bottom:1px solid #f3f4f6;"><td style="padding:6px 0;"><strong>Property Size:</strong></td><td align="right">{enquiry.property_size or 'N/A'}</td></tr>
                    {"<tr><td style='padding:6px 0;'><strong>Location Link:</strong></td><td align='right'><a href='" + enquiry.property_location_link + "' style='color:#2563eb;'>View Link</a></td></tr>" if enquiry.property_location_link else ""}
                </table>
            </td>
        </tr>
        <tr><td style="border-top:1px solid #e5e7eb;"></td></tr>

        <!-- Investment -->
        <tr>
            <td style="padding:20px 0;">
                <h3 style="margin:0 0 12px;color:#111827;font-size:16px;">4. Investment Details</h3>
                <table width="100%" style="border-collapse:collapse;font-size:14px;color:#374151;">
                    <tr style="border-bottom:1px solid #f3f4f6;"><td style="padding:6px 0;"><strong>Investment Budget:</strong></td><td align="right" style="color:#16a34a;font-weight:bold;">{enquiry.investment_budget}</td></tr>
                    <tr style="border-bottom:1px solid #f3f4f6;"><td style="padding:6px 0;"><strong>Source of Funds:</strong></td><td align="right">{enquiry.investment_source}</td></tr>
                    <tr style="border-bottom:1px solid #f3f4f6;"><td style="padding:6px 0;"><strong>Start Timeline:</strong></td><td align="right">{enquiry.plan_to_start}</td></tr>
                    <tr><td style="padding:6px 0;"><strong>Daily Involvement:</strong></td><td align="right">{enquiry.daily_operations_involvement}</td></tr>
                </table>
            </td>
        </tr>
        <tr><td style="border-top:1px solid #e5e7eb;"></td></tr>

        <tr>
            <td style="padding-top:20px;text-align:center;color:#6b7280;font-size:13px;">
                <p style="margin:0;">This lead is registered in the Jaji’s admin system.</p>
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
        logger.info(f"Franchise admin notification email sent to {admin_email}")
    except Exception as e:
        logger.error(f"Failed to send franchise email to admin {admin_email}: {str(e)}", exc_info=True)


