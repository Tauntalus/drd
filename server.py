from http.server import BaseHTTPRequestHandler
import src.stoid


# Server_DRD: Custom WebServer for Domain ReDirector
class Server_DRD(BaseHTTPRequestHandler):
    internal_db = {}
    def send_ok_header(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    # send_head_html: Send the header information for the HTML page.
    def send_head_html(self, name):
        self.wfile.write(bytes(
            """<head>
                <title>%s</title>
            </head>""" % name, "utf-8"))

    def send_home_page(self):
        self.send_ok_header()

        self.wfile.write(bytes("<html>", "utf-8"))
        self.send_head_html("Domain ReDirector - Main Page")
        self.wfile.write(bytes(
            """<body>
                <p>This is the home page.</p>
                <p>Thank you for visiting.</p>
            </body>""", "utf-8"))
        self.wfile.write(bytes("<html>", "utf-8"))

    def do_GET(self): # TODO: Transform into a link lookup

        # This line gets the path as a list of arguments,
        # Stripping off the leading slash
        args = self.path[1:].split('/')

        if args[0] == '' and len(args) == 1:
            self.send_home_page()

        elif args[0] == "stoid" and len(args) == 2:
            self.send_ok_header()
            self.wfile.write(bytes("<html>", "utf-8"))
            self.send_head_html("Domain ReDirector - String Convertor")

            # Process string
            s = args[1]
            if s.isalpha():
                num = src.stoid.stoid(s.upper())

                self.wfile.write(bytes(
                    """<body>
                        <p>Your string: %s</p>
                        <p>Its ID: %d</p>
                    </body>""" % (s.upper(), int(num)), "utf-8"))


            else:
                self.wfile.write(bytes(
                    """<body>
                        <p>The given string is not valid.</p>
                    </body>""", "utf-8"))

            self.wfile.write(bytes("</html>", "utf-8"))

        elif args[0] == "idtos" and len(args) == 2:
            self.send_ok_header()
            self.wfile.write(bytes("<html>", "utf-8"))
            self.send_head_html("Domain ReDirector - ID Convertor")

            # Process ID
            num = args[1]
            if num.isdigit():
                s = src.stoid.idtos(int(num))

                self.wfile.write(bytes(
                    """<body>
                        <p>Your ID: %d</p>
                        <p>Its string: %s</p>
                    </body>""" % (int(num), s.upper()), "utf-8"))
            else:
                self.wfile.write(bytes(
                    """<body>
                        <p>The given ID is not valid.</p>
                    </body>""", "utf-8"))

            self.wfile.write(bytes("</html>", "utf-8"))

        else:
            self.send_ok_header()
            self.wfile.write(bytes("<html>", "utf-8"))
            self.send_head_html("Domain ReDirector - Other")
            self.wfile.write(bytes(
                """<body>
                    <p>This page does nothing.</p>
                </body>""", "utf-8"))
            self.wfile.write(bytes("</html>", "utf-8"))
