import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_invitation_email(to_email, claim_link):
    # Email configuration
    sender_email = "xgael.sanjuan@gmail.com"  # Replace with your email
    sender_password = "mkyz hzvv nlmg tqpe"  # Replace with your email password or app-specific password
    smtp_server = "smtp.gmail.com"  # Replace with your SMTP server (e.g., smtp.gmail.com)
    smtp_port = 587  # Typically 587 for TLS, 465 for SSL

    # Create the email
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "You're Invited to Cyberpunk 2077 Playtest!"
    msg["From"] = "Cyberpunk Playtest <noreply@yourdomain.com>"
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
                background-color: #ff0055;
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
            .button {{
                display: inline-block;
                padding: 15px 30px;
                background-color: #00ffcc;
                color: #000000;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
                margin: 20px 0;
            }}
            .button:hover {{
                background-color: #00e6b8;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Cyberpunk 2077 Playtest Invitation</h1>
            </div>
            <div class="content">
                <h2>Hello, Night City Resident!</h2>
                <p>You’ve been exclusively selected to join the upcoming Cyberpunk 2077 playtest. Experience the neon-lit streets, intense action, and immersive story before anyone else!</p>
                <p>Claim your spot now and dive into the future:</p>
                <a href="{claim_link}" class="button">Claim Your Copy Now</a>
                <p>Hurry! Slots are limited, and this is your chance to be among the first to explore Night City.</p>
                <p>See you in 2077,<br>The Cyberpunk Team</p>
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
        print("Invitation email sent successfully!")
        return True

    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False

# Example usage
if __name__ == "__main__":
    recipient_email = "xaviergael.sanjuan@lorma.edu" 
    claim_link = "google.com"  
    
    send_invitation_email(recipient_email, claim_link)