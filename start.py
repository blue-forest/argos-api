import os
import json
import argostranslate.package
import argostranslate.translate
import http.server
import socketserver

LANGUAGES = os.getenv("ARGOS_LANGUAGES").split(",")

if not LANGUAGES or len(LANGUAGES) < 2:
  print("ARGOS_LANGUAGES environment variable is not set or has less than 2 languages.")
  print("Please set the ARGOS_LANGUAGES environment variable to a comma-separated list of language codes.")
  print("Example: ARGOS_LANGUAGES=en,fr")
  print("Exiting...")
  exit(1)

argostranslate.package.update_package_index()
available_packages = argostranslate.package.get_available_packages()

for from_code in LANGUAGES:
  for to_code in LANGUAGES:
    if from_code == to_code: continue
    try:
      package_to_install = next(filter(lambda x: x.from_code == from_code and x.to_code == to_code, available_packages))
      argostranslate.package.install_from_path(package_to_install.download())
      print(f"{from_code} --> {to_code} ✅")
    except:
      print(f"{from_code} --> {to_code} ❌")

TOKEN = os.getenv("ARGOS_TOKEN", "")

class CustomHandler(http.server.SimpleHTTPRequestHandler):
  def do_GET(self):
    self.send_response(404)
    self.end_headers()
    self.wfile.write(b"Not Found")
    return

  def do_POST(self):
    if len(TOKEN) != 0:
      auth_header = self.headers.get('Authorization')
      if not auth_header or not auth_header.startswith("Bearer "):
        self.send_response(401)
        self.end_headers()
        self.wfile.write(b"Unauthorized")
        return

      token = auth_header.split("Bearer ")[1]
      if token != TOKEN:
        self.send_response(403)
        self.end_headers()
        self.wfile.write(b"Forbidden")
        return

    content_length = int(self.headers['Content-Length'])
    post_data = self.rfile.read(content_length)

    try:
      data = json.loads(post_data)

      query = data.get("q")
      if not query: raise ValueError("Missing required query: q")
      origin = data.get("o")
      if not origin: raise ValueError("Missing required origin: o")
      target = data.get("t")
      if not target: raise ValueError("Missing required target: t")

      translation = argostranslate.translate.translate(query, origin, target)

      self.send_response(200)
      self.send_header('Content-Type', 'text/plain; charset=utf-8')
      self.send_header('Access-Control-Allow-Origin', '*')
      self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
      self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
      self.send_header('Access-Control-Allow-Credentials', 'true')
      self.send_header('Access-Control-Max-Age', '86400')
      self.send_header('Content-Length', str(len(translation)))
      self.send_header('X-Content-Type-Options', 'nosniff')
      self.send_header('X-Frame-Options', 'DENY')
      self.send_header('X-XSS-Protection', '1; mode=block')
      self.send_header('Referrer-Policy', 'no-referrer')
      self.end_headers()

      self.wfile.write(translation.encode('utf-8'))

    except Exception as e:
      self.send_response(400)
      self.end_headers()
      self.wfile.write(f"Bad Request: {str(e)}".encode('utf-8'))

  def do_OPTIONS(self):
    self.send_response(200)
    self.send_header('Access-Control-Allow-Origin', '*')
    self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
    self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    self.send_header('Access-Control-Allow-Credentials', 'true')
    self.send_header('Access-Control-Max-Age', '86400')
    self.end_headers()

PORT = int(os.getenv("ARGOS_PORT", 8080))

with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
  print(f"Serving at port {PORT}")
  try:
    httpd.serve_forever()
  except KeyboardInterrupt:
    print("Exiting...")
    httpd.server_close()
    exit(0)
  except Exception as e:
    print(f"Error: {str(e)}")
    httpd.server_close()
    exit(1)
  finally:
    print("Server stopped")
