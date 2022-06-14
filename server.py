from http.server import BaseHTTPRequestHandler
from src.stoid import stoid, idtos
from src.database import LinkDB
from urllib.parse import unquote

# Server_DRD: Custom WebServer for Domain ReDirector
class Server_DRD(BaseHTTPRequestHandler):
    internal_db = LinkDB()

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

    def process_form(self):
        res_len = int(self.headers["Content-Length"])
        form_raw = self.rfile.read(res_len)
        form_processed = form_raw.decode("utf-8").split('&')

        form_dict = {}
        for entry in form_processed:
            kvp = entry.split('=')
            form_dict[kvp[0]] = kvp[1]

        return form_dict

    # redirect - Redirects the user to a given location
    def redirect(self, link):
        self.send_response(308)
        self.send_header("location", link)
        self.end_headers()
        return

    # do_GET: GET request handler
    # TODO: Move HTML pages to external resource
    def do_GET(self):

        # This line gets the path as a list of arguments,
        # Stripping off the leading slash
        args = self.path[1:].split('/')

        if args[0] == '':
            self.send_page(200, "Domain ReDirector - Main Page",

                           """<h1>DRD - Domain ReDirector</h1></br>
                           <p>This is the home page.</p>
                           <p>Thank you for visiting.</p>""")
            return

        elif args[0] == "register":
            self.send_page(200, "Domain ReDirector - Register a Link",

                           """<h1>Register a New Link</h1></br>
                           <form method="POST" action="register-complete">
                            <div>
                                <label for="link">Link to register: </label>
                                <input type="url" id="link" name="link" required>
                            </div>
                            <div>
                                <input type=submit value="Register">
                            </div>
                           </form>""")
            return

        elif args[0] == "register-id":
            self.send_page(200, "Domain ReDirector - Register A Link",

                           """<h1>Register a New Link With An ID</h1></br>
                           <form method="POST" action="register-id-complete">
                            <div>
                                <label for="link">Link to register: </label>
                                <input type="url" id="link" name="link" required>
                            </div>
                            <div>
                                <label for="ext">5-letter ID: </label>
                                <input type="text" id="ext" name="ext" 
                                minlength=%d maxlength=%d pattern="[A-Za-z]{5}" required>
                            </div>
                            <div>
                                <input type=submit value="Register">
                            </div>
                           </form>""" % (self.internal_db.char_limit, self.internal_db.char_limit))
            return

        elif args[0] == "stoid" and len(args) == 2:

            # Process string
            s = args[1]
            if s.isalpha():
                num = stoid(s.upper())

                self.send_page(200, "Domain ReDirector - String Converter",
                               """<p>Your string: %s</p>
                               <p>Its ID: %d</p>""" % (s.upper(), int(num)))
                return

            else:
                self.send_page(200, "Domain ReDirector - String Conversion Error",
                               """<p>The given string is not valid.</p>""")
                return

        elif args[0] == "idtos" and len(args) == 2:

            # Process ID
            num = args[1]
            if num.isdigit():
                s = idtos(int(num))

                self.send_page(200, "Domain ReDirector - ID Converter",
                               """<p>Your ID: %d</p>
                               <p>Its string: %s</p>""" % (int(num), s.upper()))
                return
            else:
                self.send_page(200, "Domain ReDirector - ID Conversion Error",
                               """<p>The given ID is not valid.</p>""")
                return

    # do_POST: POST request handler
    # TODO: Move HTML pages to external resource
    def do_POST(self):
        args = self.path[1:].split('/')

        if args[0] == "register-complete":
            form_dict = self.process_form()
            link = form_dict["link"]

            if self.internal_db.get_id_by_link(link):
                self.redirect("already-registered")
                return

            new_id = self.internal_db.add_rand(link)
            new_ext = idtos(new_id)

            self.send_page(201, "Domain ReDirector - Registration Complete",
                           """<h1>Registration Complete!</h1></br>
                           <p>Thank you! Your link (%s) has been registered!</p>
                           <p>Your new short link is 
                            <a href="localhost:8080/%s">localhost:8080/%s</a>
                           </p>""" % (link, new_ext, new_ext))
            return
        elif args[0] == "register-id-complete":
            form_dict = self.process_form()
            link = str(unquote(form_dict["link"]))
            link_ext = str(form_dict["ext"])

            if self.internal_db.get_id_by_link(link):
                self.redirect("already-registered")
                return

            link_id = stoid(link_ext)
            new_id = self.internal_db.add_with_id(link, link_id)
            if new_id >= 0:

                self.send_page(201, "Domain ReDirector - Registration Complete",
                               """<h1>Registration Complete!</h1></br>
                               <p>Thank you! Your link (%s) has been registered with the ID: %s!</p>
                               <p>Your new short link is 
                                <a href="localhost:8080/%s">localhost:8080/%s</a>
                               </p>""" % (link, link_ext, link_ext, link_ext))
                return
            else:
                self.redirect("id-taken")
                return

        # Soft Error Pages
        # These pages handle "soft errors" - not sever enough to crash, but
        elif args[0] == "already-registered":
            form_dict = self.process_form()
            link = str(unquote(form_dict["link"]))
            cur_id = self.internal_db.get_id_by_link(link)
            cur_ext = idtos(cur_id)

            self.send_page(201, "Domain ReDirector - Link Already Registered",
                           """<h1>Your Link was Already Registered.</h1></br>
                           <p>Your link (%s) has already been registered in our database.</p>
                           <p>Its short link is 
                            <a href="localhost:8080/%s">localhost:8080/%s</a>
                           </p>""" % (link, cur_ext, cur_ext))
            return

        elif args[0] == "id-taken":
            form_dict = self.process_form()
            cur_ext = str(form_dict["ext"])

            self.send_page(201, "Domain ReDirector - ID Taken",
                           """<h1>Your ID Was Already Taken.</h1></br>
                           <p>Your chosen ID (%s) was already registered in our database.</p>""" % (cur_ext))
            return