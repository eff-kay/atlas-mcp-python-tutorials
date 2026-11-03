"""Two independent HTTP fixture endpoints; no external requests or real addresses."""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def provider_server(kind, port):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            try:
                data = json.loads(
                    self.rfile.read(int(self.headers.get("Content-Length", "0")))
                )
                if (
                    kind == "address"
                    and self.path == "/route"
                    and data.get("address_ref") == "demo-home"
                ):
                    status, result = (
                        200,
                        {"distance_km": 12, "provider": "GeoRoute (local fixture)"},
                    )
                elif (
                    kind == "delivery"
                    and self.path == "/quote"
                    and data.get("distance_km") == 12
                    and data.get("product_id") == "blue-carryon"
                ):
                    status, result = (
                        200,
                        {
                            "shipping_cents": 1200,
                            "eta": "Friday (fixture estimate)",
                            "provider": "ParcelQuote (local fixture)",
                        },
                    )
                else:
                    status, result = 422, {"error": "Unsupported fixture input"}
            except (ValueError, TypeError, AttributeError):
                status, result = 400, {"error": "Invalid JSON request"}
            payload = json.dumps(result).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def start_providers(address_port, delivery_port):
    servers = []
    try:
        for kind, port in [("address", address_port), ("delivery", delivery_port)]:
            server = provider_server(kind, port)
            threading.Thread(target=server.serve_forever, daemon=True).start()
            servers.append(server)
    except Exception:
        for server in servers:
            server.shutdown()
            server.server_close()
        raise
    return servers
