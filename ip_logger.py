from http.server import BaseHTTPRequestHandler, HTTPServer
import logging

class IPLoggerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        client_ip = self.client_address[0]
        logging.info(f"Visitor IP: {client_ip}")
        with open("ips.txt", "a") as f:
            f.write(f"{client_ip}\n")

        # Fake "blog error" page
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html = """
        <html>
        <head><title>My Everyday Blog</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1>Oops!</h1>
            <p>Sorry, something went wrong loading this page.</p>
            <p><small>Try again later.</small></p>
        </body>
        </html>
        """
        self.wfile.write(html.encode('utf-8'))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    server_address = ('', 8080)  # Runs on port 8080
    httpd = HTTPServer(server_address, IPLoggerHandler)
    print("Server running on port 8080...")
    httpd.serve_forever()
