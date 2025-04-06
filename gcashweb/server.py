import http.server
import socketserver
import json
import os
import sys
import importlib.util
from urllib.parse import urlparse, parse_qs

# Handle imports differently when running as executable vs script
try:
    from send_otp_email import send_otp_email
except ImportError:
    # If running from executable, the module might be in a different location
    try:
        # Get the base path - works for both script and executable
        if getattr(sys, 'frozen', False):
            # If the application is run as a bundle (executable)
            base_path = os.path.dirname(sys.executable)
        else:
            # If the application is run as a script
            base_path = os.path.dirname(os.path.abspath(__file__))
            
        # Try to import from the gcashweb directory
        module_path = os.path.join(base_path, 'gcashweb', 'send_otp_email.py')
        if not os.path.exists(module_path):
            # Try parent directory
            module_path = os.path.join(base_path, 'send_otp_email.py')
            
        spec = importlib.util.spec_from_file_location("send_otp_email", module_path)
        send_otp_email_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(send_otp_email_module)
        send_otp_email = send_otp_email_module.send_otp_email
    except Exception as e:
        print(f"Error importing send_otp_email: {e}")
        # Fallback function that just returns False
        def send_otp_email(to_email, otp_code):
            print(f"Failed to send OTP {otp_code} to {to_email}")
            return False

PORT = 8000

class OTPHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        # Handle POST requests for sending OTP emails
        if self.path == '/send_otp':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            email = data.get('email')
            otp = data.get('otp')
            
            if email and otp:
                # Send OTP email
                success = send_otp_email(email, otp)
                
                # Send response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {'success': success}
                self.wfile.write(json.dumps(response).encode('utf-8'))
            else:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {'error': 'Missing email or OTP'}
                self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            # Serve static files
            super().do_POST()
    
    def do_OPTIONS(self):
        # Handle CORS preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

def run_server():
    # Get the base path - works for both script and executable
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle (executable)
        base_path = os.path.dirname(sys.executable)
        # Try to find the gcashweb directory
        gcashweb_path = os.path.join(base_path, 'gcashweb')
        if os.path.exists(gcashweb_path):
            os.chdir(gcashweb_path)
        else:
            # If gcashweb directory doesn't exist, use the executable directory
            os.chdir(base_path)
    else:
        # If the application is run as a script
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Create the server
    handler = OTPHandler
    httpd = socketserver.TCPServer(("", PORT), handler)
    
    print(f"Server running at http://localhost:{PORT}")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped.")
        httpd.server_close()

if __name__ == "__main__":
    run_server()