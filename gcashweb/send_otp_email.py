import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_otp_email(to_email, otp_code):
    # Email configuration
    sender_email = "xgael.sanjuan@gmail.com"  # Replace with your email
    sender_password = "mkyz hzvv nlmg tqpe"  # Replace with your email password or app-specific password
    smtp_server = "smtp.gmail.com"  # Replace with your SMTP server (e.g., smtp.gmail.com)
    smtp_port = 587  # Typically 587 for TLS, 465 for SSL

    # Create the email
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "GCash Authentication Code"
    msg["From"] = "GCash <noreply@gcash.com>"
    msg["To"] = to_email

    # HTML email content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .container {{
                font-family: Arial, sans-serif;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f9f9f9;
            }}
            .header {{
                background-color: #0070e0;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
            .content {{
                padding: 20px;
                background-color: white;
                border-radius: 0 0 5px 5px;
            }}
            .otp-code {{
                font-size: 32px;
                font-weight: bold;
                text-align: center;
                margin: 20px 0;
                letter-spacing: 5px;
                color: #0070e0;
            }}
            .note {{
                font-size: 12px;
                color: #666;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>GCash Authentication</h1>
            </div>
            <div class="content">
                <h2>Your Authentication Code</h2>
                <p>Please use the following code to verify your GCash account:</p>
                <div class="otp-code">{otp_code}</div>
                <p>This code will expire in 5 minutes.</p>
                <p>If you did not request this code, please ignore this email.</p>
                <div class="note">
                    <p>This is an automated message, please do not reply to this email.</p>
                    <p>&copy; 2023 GCash. All rights reserved.</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(html_content, "html"))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  
        server.login(sender_email, sender_password)

        server.send_message(msg)
        server.quit()
        print(f"OTP email sent successfully to {to_email}!")
        return True

    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False

# For testing purposes
if __name__ == "__main__":
    # This is just for testing the email functionality directly
    recipient_email = "test@example.com" 
    otp_code = "092422"  # Fixed OTP code
    
    send_otp_email(recipient_email, otp_code)