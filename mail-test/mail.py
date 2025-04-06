import tkinter as tk
from tkinter import messagebox
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_invitation_email(to_email):
    # Email configuration
    sender_email = "xgael.sanjuan@gmail.com"  # Replace with your email
    sender_password = "mkyz hzvv nlmg tqpe"  # Replace with your email password or app-specific password
    smtp_server = "smtp.gmail.com"  
    smtp_port = 587  
    claim_link = "https://cyberpunk-playtest.vercel.app"  # Fixed claim link

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
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False

def send_email_from_gui():
    recipient_email = email_entry.get()
    
    if not recipient_email:
        messagebox.showerror("Error", "Please enter an email address!")
        return
    
    success = send_invitation_email(recipient_email)
    if success:
        messagebox.showinfo("Success", "Email sent successfully!")
        email_entry.delete(0, tk.END)
    else:
        messagebox.showerror("Error", "Failed to send email. Check console for details.")

# Create the Tkinter window
root = tk.Tk()
root.title("Cyberpunk 2077 Playtest Email Sender")
root.geometry("400x200")
root.configure(bg="#1a1a1a")

# Email label and entry
email_label = tk.Label(root, text="Recipient Email:", bg="#1a1a1a", fg="white", font=("Arial", 12))
email_label.pack(pady=20)
email_entry = tk.Entry(root, width=40, font=("Arial", 10))
email_entry.pack(pady=10)

# Send button
send_button = tk.Button(root, text="Send Invitation", command=send_email_from_gui, 
                       bg="#ff0055", fg="white", font=("Arial", 12, "bold"), 
                       activebackground="#00ffcc", activeforeground="black")
send_button.pack(pady=20)

# Start the Tkinter event loop
if __name__ == "__main__":
    root.mainloop()