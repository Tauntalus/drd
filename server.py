from http.server import BaseHTTPRequestHandler
import src.stoid


# Server_DRD: Custom WebServer for Domain ReDirector
class Server_DRD(BaseHTTPRequestHandler):
    def do_GET(self): # TODO: Transform into a link lookup

        # This line gets the path as a list of arguments,
        # Stripping off the leading slash
        args = self.path[1:].split('/')

        if args[0] == '' and len(args) == 1:
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
                        <p>This is the home page.</p>
                        <p>Thank you for visiting.</p>
                    </body>
                </html>""", "utf-8"))
        elif args[0] == "stoid" and len(args) == 2:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            # Send HTML Page response
            self.wfile.write(bytes(
                """<html>
                    <head>
                        <title>Domain ReDirector - String Convertor</title>
                    </head>
                    <body>
                        <p>This page converts strings.</p>
                    </body>
                </html>""", "utf-8"))
        elif args[0] == "idtos" and len(args) == 2:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            # Send HTML Page response
            self.wfile.write(bytes(
                """<html>
                    <head>
                        <title>Domain ReDirector - ID Convertor</title>
                    </head>
                    <body>
                        <p>This page converts IDs.</p>
                    </body>
                </html>""", "utf-8"))
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            # Send HTML Page response
            self.wfile.write(bytes(
                """<html>
                    <head>
                        <title>Domain ReDirector - Other</title>
                    </head>
                    <body>
                        <p>This page does nothing.</p>
                    </body>
                </html>""", "utf-8"))
