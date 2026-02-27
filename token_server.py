"""
Basit token sunucusu — test.html için LiveKit erişim token'ı üretir.
Kullanım: python token_server.py
Adres:    http://localhost:8080/token?room=test-room&identity=user-1&language=en
"""

import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
from livekit.api import AccessToken, VideoGrants

load_dotenv()


class TokenHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/token":
            query = parse_qs(parsed.query)
            identity = query.get("identity", ["user-1"])[0]
            room = query.get("room", ["test-room"])[0]
            language = query.get("language", ["en"])[0]

            token = (
                AccessToken(
                    api_key=os.environ["LIVEKIT_API_KEY"],
                    api_secret=os.environ["LIVEKIT_API_SECRET"],
                )
                .with_identity(identity)
                .with_name(identity)
                .with_grants(VideoGrants(room_join=True, room=room))
                .with_attributes({"language": language})
                .to_jwt()
            )

            response = json.dumps(
                {"token": token, "url": os.environ["LIVEKIT_URL"]}
            ).encode()

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(response)

        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Gereksiz log çıktısını bastır


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    httpd = HTTPServer(("0.0.0.0", port), TokenHandler)
    print(f"Token sunucusu çalışıyor → http://localhost:{port}/token")
    print("Durdurmak için Ctrl+C")
    httpd.serve_forever()
