from http.server import BaseHTTPRequestHandler
import src.stoid
import src.database


# Server_DRD: Custom WebServer for Domain ReDirector
class Server_DRD(BaseHTTPRequestHandler):
    internal_db = src.database.LinkDB()

    # send_page: accepts a response code, page title, and page body
    # then sends a well-formatted HTML response to the requester
    def send_page(self, code, title, page):
        self.send_response(code)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        self.wfile.write(bytes("<html>", "utf-8"))
        self.wfile.write(bytes(
            """<head>
                <title>%s</title>
            </head>""" % title, "utf-8"))
        self.wfile.write(bytes(
            """<body>
                %s
            </body>""" % page, "utf-8"))
        self.wfile.write(bytes("</html>", "utf-8"))
        return

    # do_GET: GET request handler
    # TODO: Move HTML pages to external resource
    def do_GET(self):

        # This line gets the path as a list of arguments,
        # Stripping off the leading slash
        args = self.path[1:].split('/')

        if args[0] == "api" and len(args) > 1:
            return

        if args[0] == '':
            self.send_page(200, "Domain ReDirector - Main Page",

                           """<h1>DRD - Domain ReDirector</h1></br>
                           <p>This is the home page.</p>
                           <p>Thank you for visiting.</p>""")

        elif args[0] == "register":
            self.send_page(200, "Domain ReDirector - Register a Link",

                           """<h1>Register a New Link</h1></br>
                           <form method="POST" action="api/register">
                            <div>
                                <label for="new_link">Link to register: </label>
                                <input type="text" id="new_link" name="new_link" required>
                            </div>
                            <div>
                                <input type=submit value="Register">
                            </div>
                           </form>""")

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

    # do_POST: POST request handler
    # TODO: Move HTML pages to external resource
    def do_POST(self):
        args = self.path[1:].split('/')
        return
