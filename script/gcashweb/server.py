import http.server
import socketserver
import json
import os
import sys
import importlib.util
from urllib.parse import urlparse, parse_qs
import socket

# Handle imports differently when running as executable vs script
try:
    from send_otp_email import send_otp_email
except ImportError:
    # If running from executable, the module might be in a different location
    try:
        # Get the base path - works for both script and executable
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
            
        # Try to import from the gcashweb directory
        module_path = os.path.join(base_path, 'gcashweb', 'send_otp_email.py')
        if not os.path.exists(module_path):
            module_path = os.path.join(base_path, 'send_otp_email.py')
            
        spec = importlib.util.spec_from_file_location("send_otp_email", module_path)
        send_otp_email_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(send_otp_email_module)
        send_otp_email = send_otp_email_module.send_otp_email
    except Exception as e:
        print(f"Error importing send_otp_email: {e}")
        def send_otp_email(to_email, otp_code):
            print(f"Failed to send OTP {otp_code} to {to_email}")
            return False

PORT = 8000

class OTPHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/send_otp':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                email = data.get('email')
                otp = data.get('otp')
                
                if email and otp:
                    success = send_otp_email(email, otp)
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = {'success': success}
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                else:
                    self.send_error(400, 'Missing email or OTP')
            except json.JSONDecodeError:
                self.send_error(400, 'Invalid JSON data')
        else:
            super().do_POST()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("", port))
            return False
        except OSError:
            return True

def run_server(port=PORT):
    # Get the base path - works for both script and executable
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
        gcashweb_path = os.path.join(base_path, 'gcashweb')
        os.chdir(gcashweb_path if os.path.exists(gcashweb_path) else base_path)
    else:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Check if port is in use and try alternatives if necessary
    max_attempts = 10
    current_port = port
    for i in range(max_attempts):
        if not is_port_in_use(current_port):
            break
        current_port = port + i + 1
        print(f"Port {port + i} in use, trying {current_port}...")
    else:
        raise OSError(f"Could not find an available port after {max_attempts} attempts")

    # Create the server
    handler = OTPHandler
    httpd = socketserver.TCPServer(("", current_port), handler)
    
    print(f"Server running at http://localhost:{current_port}")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped.")
        httpd.server_close()

if __name__ == "__main__":
    run_server()