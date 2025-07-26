from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import requests

class IPLoggerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        client_ip = self.client_address[0]

        # Fetch geolocation info
        try:
            response = requests.get(f"https://ipinfo.io/{client_ip}/json")
            data = response.json()
            city = data.get("city", "Unknown")
            region = data.get("region", "Unknown")
            country = data.get("country", "Unknown")
            org = data.get("org", "Unknown ISP")
        except Exception as e:
            city = region = country = org = "Unavailable"

        # Log details
        log_entry = f"IP: {client_ip} | {city}, {region}, {country} | ISP: {org}"
        logging.info(log_entry)
        with open("ips.txt", "a") as f:
            f.write(log_entry + "\n")

        # Fake error page
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
