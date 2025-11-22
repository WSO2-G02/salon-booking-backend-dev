"""
HTML Email Templates for Notification Service
Professional email templates for various notifications
"""

# Common styles used across all templates
COMMON_STYLES = """
<style>
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4; }
    .container { max-width: 600px; margin: 0 auto; background-color: #ffffff; }
    .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; }
    .header h1 { color: #ffffff; margin: 0; font-size: 28px; }
    .header p { color: #e0e0e0; margin: 10px 0 0 0; font-size: 14px; }
    .content { padding: 40px 30px; }
    .content h2 { color: #333333; margin-top: 0; }
    .content p { color: #666666; line-height: 1.6; }
    .info-box { background-color: #f8f9fa; border-left: 4px solid #667eea; padding: 20px; margin: 20px 0; border-radius: 4px; }
    .info-box p { margin: 8px 0; color: #333333; }
    .info-box strong { color: #667eea; }
    .button { display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #ffffff; padding: 14px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 20px 0; }
    .button:hover { opacity: 0.9; }
    .footer { background-color: #f8f9fa; padding: 20px 30px; text-align: center; border-top: 1px solid #e0e0e0; }
    .footer p { color: #999999; font-size: 12px; margin: 5px 0; }
    .highlight { color: #667eea; font-weight: bold; }
    .warning { background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 4px; }
    .success { background-color: #d4edda; border-left: 4px solid #28a745; padding: 15px; margin: 20px 0; border-radius: 4px; }
    .cancelled { background-color: #f8d7da; border-left: 4px solid #dc3545; padding: 15px; margin: 20px 0; border-radius: 4px; }
</style>
"""


def get_register_user_template(full_name: str, username: str) -> str:
    """
    Generate HTML template for user registration welcome email
    
    Args:
        full_name: User's full name
        username: User's username
    
    Returns:
        HTML string for the email
    """
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Welcome to Salon Booking</title>
        {COMMON_STYLES}
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✨ Welcome to Salon Booking!</h1>
                <p>Your account has been created successfully</p>
            </div>
            <div class="content">
                <h2>Hello {full_name}! 👋</h2>
                <p>Thank you for registering with our Salon Booking System. We're excited to have you on board!</p>
                
                <div class="info-box">
                    <p><strong>Your Account Details:</strong></p>
                    <p>👤 Username: <span class="highlight">{username}</span></p>
                    <p>📧 This email is your registered email</p>
                </div>
                
                <div class="success">
                    <p>✅ Your account is now active and ready to use!</p>
                </div>
                
                <p>With your new account, you can:</p>
                <ul style="color: #666666; line-height: 2;">
                    <li>📅 Book appointments with our talented staff</li>
                    <li>💇 Browse our wide range of services</li>
                    <li>📱 Manage your bookings anytime</li>
                    <li>⭐ Track your appointment history</li>
                </ul>
                
                <p>Ready to book your first appointment?</p>
                <a href="#" class="button">Book Now</a>
            </div>
            <div class="footer">
                <p>© 2025 Salon Booking System. All rights reserved.</p>
                <p>This is an automated message. Please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """


def get_reset_password_template(full_name: str, reset_token: str, expiry_minutes: int) -> str:
    """
    Generate HTML template for password reset email
    
    Args:
        full_name: User's full name
        reset_token: Password reset token/link
        expiry_minutes: Token expiry time in minutes
    
    Returns:
        HTML string for the email
    """
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Password Reset Request</title>
        {COMMON_STYLES}
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔐 Password Reset Request</h1>
                <p>We received a request to reset your password</p>
            </div>
            <div class="content">
                <h2>Hello {full_name},</h2>
                <p>We received a request to reset the password for your Salon Booking account. If you made this request, use the button below to reset your password.</p>
                
                <div class="warning">
                    <p>⚠️ <strong>This link will expire in {expiry_minutes} minutes.</strong></p>
                </div>
                
                <div style="text-align: center;">
                    <a href="{reset_token}" class="button">Reset My Password</a>
                </div>
                
                <p>Or copy and paste this link into your browser:</p>
                <div class="info-box">
                    <p style="word-break: break-all; font-size: 12px;">{reset_token}</p>
                </div>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e0e0e0;">
                    <p><strong>Didn't request this?</strong></p>
                    <p style="color: #999999;">If you didn't request a password reset, you can safely ignore this email. Your password will remain unchanged.</p>
                </div>
            </div>
            <div class="footer">
                <p>© 2025 Salon Booking System. All rights reserved.</p>
                <p>For security reasons, this link will expire in {expiry_minutes} minutes.</p>
            </div>
        </div>
    </body>
    </html>
    """


def get_create_staff_template(full_name: str, position: str, username: str, temporary_password: str = None) -> str:
    """
    Generate HTML template for new staff member notification email
    
    Args:
        full_name: Staff full name
        position: Staff position
        username: Staff username
        temporary_password: Temporary password if generated
    
    Returns:
        HTML string for the email
    """
    password_section = ""
    if temporary_password:
        password_section = f"""
        <div class="warning">
            <p>🔑 <strong>Temporary Password:</strong> {temporary_password}</p>
            <p style="font-size: 12px;">Please change this password after your first login.</p>
        </div>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Welcome to Our Team!</title>
        {COMMON_STYLES}
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 Welcome to the Team!</h1>
                <p>Your staff account has been created</p>
            </div>
            <div class="content">
                <h2>Welcome aboard, {full_name}! 👋</h2>
                <p>Congratulations! You have been added as a staff member to our Salon Booking System. We're thrilled to have you join our team!</p>
                
                <div class="info-box">
                    <p><strong>Your Staff Account Details:</strong></p>
                    <p>👤 Name: <span class="highlight">{full_name}</span></p>
                    <p>💼 Position: <span class="highlight">{position}</span></p>
                    <p>🔐 Username: <span class="highlight">{username}</span></p>
                </div>
                
                {password_section}
                
                <div class="success">
                    <p>✅ Your staff account is now active!</p>
                </div>
                
                <p>As a staff member, you can:</p>
                <ul style="color: #666666; line-height: 2;">
                    <li>📅 View your appointment schedule</li>
                    <li>👥 Manage client bookings</li>
                    <li>📊 Track your performance</li>
                    <li>💬 Communicate with clients</li>
                </ul>
                
                <a href="#" class="button">Access Staff Portal</a>
            </div>
            <div class="footer">
                <p>© 2025 Salon Booking System. All rights reserved.</p>
                <p>If you have any questions, please contact your administrator.</p>
            </div>
        </div>
    </body>
    </html>
    """


def get_create_appointment_template(
    customer_name: str,
    service_name: str,
    staff_name: str,
    appointment_datetime: str,
    duration_minutes: int,
    price: float,
    appointment_id: int
) -> str:
    """
    Generate HTML template for appointment confirmation email
    
    Args:
        customer_name: Customer's name
        service_name: Name of the service
        staff_name: Staff member's name
        appointment_datetime: Formatted datetime string
        duration_minutes: Duration of service
        price: Service price
        appointment_id: Appointment reference ID
    
    Returns:
        HTML string for the email
    """
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Appointment Confirmed!</title>
        {COMMON_STYLES}
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📅 Appointment Confirmed!</h1>
                <p>Your booking has been successfully created</p>
            </div>
            <div class="content">
                <h2>Hello {customer_name}! 👋</h2>
                <p>Great news! Your appointment has been successfully booked. Here are the details:</p>
                
                <div class="info-box">
                    <p><strong>Appointment Details:</strong></p>
                    <p>🎫 Booking ID: <span class="highlight">#{appointment_id}</span></p>
                    <p>💇 Service: <span class="highlight">{service_name}</span></p>
                    <p>👤 Stylist: <span class="highlight">{staff_name}</span></p>
                    <p>📅 Date & Time: <span class="highlight">{appointment_datetime}</span></p>
                    <p>⏱️ Duration: <span class="highlight">{duration_minutes} minutes</span></p>
                    <p>💰 Price: <span class="highlight">${price:.2f}</span></p>
                </div>
                
                <div class="success">
                    <p>✅ Your appointment is confirmed!</p>
                </div>
                
                <p><strong>Important Reminders:</strong></p>
                <ul style="color: #666666; line-height: 2;">
                    <li>📍 Please arrive 10 minutes before your appointment</li>
                    <li>📱 Bring this confirmation email or your booking ID</li>
                    <li>❌ If you need to cancel, please do so at least 24 hours in advance</li>
                </ul>
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="#" class="button">View My Appointment</a>
                </div>
            </div>
            <div class="footer">
                <p>© 2025 Salon Booking System. All rights reserved.</p>
                <p>Need to make changes? Log in to your account or contact us.</p>
            </div>
        </div>
    </body>
    </html>
    """


def get_update_appointment_template(
    customer_name: str,
    service_name: str,
    staff_name: str,
    old_datetime: str,
    new_datetime: str,
    appointment_id: int,
    change_reason: str = None
) -> str:
    """
    Generate HTML template for appointment update notification email
    
    Args:
        customer_name: Customer's name
        service_name: Name of the service
        staff_name: Staff member's name
        old_datetime: Previous appointment datetime
        new_datetime: New appointment datetime
        appointment_id: Appointment reference ID
        change_reason: Optional reason for the change
    
    Returns:
        HTML string for the email
    """
    reason_section = ""
    if change_reason:
        reason_section = f"""
        <div class="warning">
            <p>📝 <strong>Reason for change:</strong> {change_reason}</p>
        </div>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Appointment Updated</title>
        {COMMON_STYLES}
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔄 Appointment Updated</h1>
                <p>Your booking details have been changed</p>
            </div>
            <div class="content">
                <h2>Hello {customer_name},</h2>
                <p>Your appointment has been updated. Please review the new details below:</p>
                
                <div class="info-box">
                    <p><strong>Updated Appointment Details:</strong></p>
                    <p>🎫 Booking ID: <span class="highlight">#{appointment_id}</span></p>
                    <p>💇 Service: <span class="highlight">{service_name}</span></p>
                    <p>👤 Stylist: <span class="highlight">{staff_name}</span></p>
                </div>
                
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <tr>
                        <td style="padding: 15px; background-color: #f8d7da; border-radius: 5px 0 0 5px;">
                            <p style="margin: 0; color: #721c24; font-size: 12px;">PREVIOUS</p>
                            <p style="margin: 5px 0 0 0; color: #721c24; font-weight: bold;">📅 {old_datetime}</p>
                        </td>
                        <td style="padding: 15px; text-align: center; font-size: 24px;">➡️</td>
                        <td style="padding: 15px; background-color: #d4edda; border-radius: 0 5px 5px 0;">
                            <p style="margin: 0; color: #155724; font-size: 12px;">NEW</p>
                            <p style="margin: 5px 0 0 0; color: #155724; font-weight: bold;">📅 {new_datetime}</p>
                        </td>
                    </tr>
                </table>
                
                {reason_section}
                
                <div class="success">
                    <p>✅ Your appointment has been successfully rescheduled!</p>
                </div>
                
                <p><strong>Please note:</strong> Make sure to update your calendar with the new appointment time.</p>
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="#" class="button">View Updated Appointment</a>
                </div>
            </div>
            <div class="footer">
                <p>© 2025 Salon Booking System. All rights reserved.</p>
                <p>Questions? Contact us or log in to your account.</p>
            </div>
        </div>
    </body>
    </html>
    """


def get_cancel_appointment_template(
    customer_name: str,
    service_name: str,
    staff_name: str,
    appointment_datetime: str,
    appointment_id: int,
    cancellation_reason: str = None
) -> str:
    """
    Generate HTML template for appointment cancellation email
    
    Args:
        customer_name: Customer's name
        service_name: Name of the service
        staff_name: Staff member's name
        appointment_datetime: Original appointment datetime
        appointment_id: Appointment reference ID
        cancellation_reason: Optional reason for cancellation
    
    Returns:
        HTML string for the email
    """
    reason_section = ""
    if cancellation_reason:
        reason_section = f"""
        <div class="info-box">
            <p>📝 <strong>Cancellation reason:</strong> {cancellation_reason}</p>
        </div>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Appointment Cancelled</title>
        {COMMON_STYLES}
    </head>
    <body>
        <div class="container">
            <div class="header" style="background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);">
                <h1>❌ Appointment Cancelled</h1>
                <p>Your booking has been cancelled</p>
            </div>
            <div class="content">
                <h2>Hello {customer_name},</h2>
                <p>We're sorry to inform you that your appointment has been cancelled. Here are the details of the cancelled booking:</p>
                
                <div class="cancelled">
                    <p><strong>Cancelled Appointment Details:</strong></p>
                    <p>🎫 Booking ID: #{appointment_id}</p>
                    <p>💇 Service: {service_name}</p>
                    <p>👤 Stylist: {staff_name}</p>
                    <p>📅 Original Date & Time: {appointment_datetime}</p>
                </div>
                
                {reason_section}
                
                <p>We understand that plans change, and we hope to see you again soon!</p>
                
                <div class="success">
                    <p>💡 <strong>Ready to rebook?</strong> We'd love to have you back!</p>
                </div>
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="#" class="button">Book New Appointment</a>
                </div>
            </div>
            <div class="footer">
                <p>© 2025 Salon Booking System. All rights reserved.</p>
                <p>We hope to see you again soon!</p>
            </div>
        </div>
    </body>
    </html>
    """