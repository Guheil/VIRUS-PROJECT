# GCash OTP Email System

This is a simple implementation of an OTP (One-Time Password) email system for the GCash web interface. It sends a verification code to the user's email address when they submit their PIN.

## Files

- `index.html` - The main HTML file for the GCash login interface
- `script.js` - JavaScript code for handling form submissions and UI interactions
- `styles.css` - CSS styles for the GCash interface
- `send_otp_email.py` - Python script for sending OTP emails
- `server.py` - Simple HTTP server for handling OTP email requests

## How to Run

1. Start the server:
   ```
   python server.py
   ```

2. Open the GCash login page in your browser:
   ```
   http://localhost:8000
   ```

3. Enter a phone number and email address, then proceed through the login flow.

## OTP Email Flow

1. User enters phone number and email address
2. User enters 4-digit PIN
3. System sends a 6-digit OTP code to the user's email
4. User enters the OTP code to verify their identity
5. Upon successful verification, user sees the success screen

## Notes

- For demonstration purposes, the OTP code is fixed as "092422"
- The email is sent using the SMTP configuration in `send_otp_email.py`
- The server handles CORS to allow requests from any origin