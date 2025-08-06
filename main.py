import socket
import threading
import json
import urllib.parse
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import mimetypes
from pymongo import MongoClient
import multiprocessing

# MongoDB connection
def get_mongo_client():
    """Get MongoDB client connection"""
    try:
        client = MongoClient('mongodb://mongo:27017/')
        return client
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        return None

def save_to_mongodb(data):
    """Save message data to MongoDB"""
    try:
        client = get_mongo_client()
        if client:
            db = client['messages_db']
            collection = db['messages']
            
            # Create document with timestamp
            document = {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                "username": data.get('username', ''),
                "message": data.get('message', '')
            }
            
            collection.insert_one(document)
            print(f"Message saved to MongoDB: {document}")
            client.close()
        else:
            print("Failed to connect to MongoDB")
    except Exception as e:
        print(f"Error saving to MongoDB: {e}")

class SocketServer:
    """UDP Socket Server for handling form data"""
    
    def __init__(self, host='0.0.0.0', port=5001):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
        
    def start(self):
        """Start the socket server"""
        print(f"Socket server listening on {self.host}:{self.port}")
        
        while True:
            try:
                data, addr = self.sock.recvfrom(1024)
                print(f"Received data from {addr}: {data}")
                
                # Convert bytes to string and parse JSON
                json_data = json.loads(data.decode('utf-8'))
                print(f"Parsed data: {json_data}")
                
                # Save to MongoDB
                save_to_mongodb(json_data)
                
            except Exception as e:
                print(f"Socket server error: {e}")

class WebHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler"""
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            if self.path == '/':
                self.serve_file('front-init/index.html', 'text/html')
            elif self.path == '/message.html':
                self.serve_file('front-init/message.html', 'text/html')
            elif self.path == '/style.css':
                self.serve_file('front-init/style.css', 'text/css')
            elif self.path == '/logo.png':
                self.serve_file('front-init/logo.png', 'image/png')
            else:
                self.serve_404()
        except Exception as e:
            print(f"GET request error: {e}")
            self.serve_404()
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            if self.path == '/message':
                # Get form data
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                
                # Parse form data
                parsed_data = urllib.parse.parse_qs(post_data.decode('utf-8'))
                
                # Extract username and message
                username = parsed_data.get('username', [''])[0]
                message = parsed_data.get('message', [''])[0]
                
                # Prepare data for socket
                data_to_send = {
                    'username': username,
                    'message': message
                }
                
                # Send to socket server
                self.send_to_socket_server(data_to_send)
                
                # Redirect to home page
                self.send_response(302)
                self.send_header('Location', '/')
                self.end_headers()
            else:
                self.serve_404()
        except Exception as e:
            print(f"POST request error: {e}")
            self.serve_404()
    
    def send_to_socket_server(self, data):
        """Send data to socket server via UDP"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            json_data = json.dumps(data).encode('utf-8')
            sock.sendto(json_data, ('localhost', 5001))
            sock.close()
            print(f"Data sent to socket server: {data}")
        except Exception as e:
            print(f"Error sending to socket server: {e}")
    
    def serve_file(self, filename, content_type):
        """Serve static files"""
        try:
            if os.path.exists(filename):
                self.send_response(200)
                self.send_header('Content-type', content_type)
                self.end_headers()
                
                if content_type.startswith('text'):
                    with open(filename, 'r', encoding='utf-8') as f:
                        self.wfile.write(f.read().encode('utf-8'))
                else:
                    with open(filename, 'rb') as f:
                        self.wfile.write(f.read())
            else:
                self.serve_404()
        except Exception as e:
            print(f"File serving error: {e}")
            self.serve_404()
    
    def serve_404(self):
        """Serve 404 error page"""
        try:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            if os.path.exists('front-init/error.html'):
                with open('front-init/error.html', 'r', encoding='utf-8') as f:
                    self.wfile.write(f.read().encode('utf-8'))
            else:
                self.wfile.write(b'<h1>404 Not Found</h1>')
        except Exception as e:
            print(f"404 serving error: {e}")

def run_web_server():
    """Run HTTP web server"""
    server = HTTPServer(('0.0.0.0', 3000), WebHandler)
    print("Web server running on port 3000")
    server.serve_forever()

def run_socket_server():
    """Run socket server"""
    socket_server = SocketServer()
    socket_server.start()

if __name__ == '__main__':
    # Start both servers in separate processes
    web_process = multiprocessing.Process(target=run_web_server)
    socket_process = multiprocessing.Process(target=run_socket_server)
    
    web_process.start()
    socket_process.start()
    
    try:
        web_process.join()
        socket_process.join()
    except KeyboardInterrupt:
        print("Shutting down servers...")
        web_process.terminate()
        socket_process.terminate()
        web_process.join()
        socket_process.join()
