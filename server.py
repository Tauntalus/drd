from http.server import BaseHTTPRequestHandler
import time


# Server_DRD: Custom WebServer for Domain ReDirector
class Server_DRD(BaseHTTPRequestHandler):
    def do_GET(self): # TODO: Transform into a link lookup

        # Successful GET, inform browser. Incoming!
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        # Send HTML Page response
        self.wfile.write(bytes(
            """<html>
                <head>
                    <title>Domain ReDirector - Main Page</title>
                </head>
                <body>
                    <p>This request was made to the path %s</p>
                    <p>Thank you for visiting.</p>
                </body>
            </html>""" % self.path, "utf-8"))