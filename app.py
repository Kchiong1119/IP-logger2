from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import json
import urllib.request

class IPLoggerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        client_ip = self.client_address[0]

        # Get geolocation data
        try:
            with urllib.request.urlopen(f"http://ip-api.com/json/{client_ip}") as url:
                geo_data = json.loads(url.read().decode())
                location_info = f"{geo_data.get('city', 'Unknown')}, {geo_data.get('country', 'Unknown')} | ISP: {geo_data.get('isp', 'Unknown')}"
        except:
            location_info = "Location lookup failed"

        # Log to file
        logging.info(f"Visitor IP: {client_ip} | {location_info}")
        with open("ips.txt", "a") as f:
            f.write(f"{client_ip} - {location_info}\n")

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
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, IPLoggerHandler)
    print("Server running on port 8080...")
    httpd.serve_forever()
