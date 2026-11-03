"""Independent loopback fixture API. No geocoding, addresses or couriers are contacted."""

import json, os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"fixture ready")

    def do_POST(self):
        data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))))
        mode = os.environ["PROVIDER"]
        if (
            mode == "address"
            and self.path == "/route"
            and data.get("address_ref") == "demo-home"
        ):
            result = {
                "route_id": "route-demo",
                "distance_km": 12,
                "destination_zone": "demo-zone",
                "provider": "GeoRoute (fixture)",
            }
            status = 200
        elif (
            mode == "delivery"
            and self.path == "/quote"
            and data.get("distance_km") == 12
        ):
            result = {
                "shipping_cents": 1200,
                "eta": "Friday (fixture estimate)",
                "provider": "ParcelQuote (fixture)",
            }
            status = 200
        else:
            result = {"error": "Unsupported fixture input"}
            status = 422
        payload = json.dumps(result).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(payload)


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", int(os.environ["PORT"])), Handler).serve_forever()
