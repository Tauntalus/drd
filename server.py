from http.server import BaseHTTPRequestHandler
from src.stoid import stoid, idtos
from src.database import LinkDB
from urllib.parse import unquote


# Server_DRD: Custom WebServer for Domain ReDirector
class Server_DRD(BaseHTTPRequestHandler):
    internal_db = LinkDB()
    name = "Domain ReDirector"
    server_address = "http://%(host)s:%(port)s"

    error_message_format = """
    <head>
        <title>{} - Error %(code)d</title>
    </head>
    <body>
        <h2>%(message)s</h2>
        <p>%(explain)s</p>
        <a href="/">Main Page</a>
    </body>""".format(name)

    css_format = """
    body {
        background-color: #D6D6FF;
        margin: 1%;
    }
    
    div {
        padding: 1%;
    }
    
    form {
        align: right;
        margin: auto;
        width: 30%;
    }
    
    .page {
        background-color: #E6E6FF;
        margin: auto;
        width: 90%;
        text-align: center;
    }
    
    .grid {
        display: flex;
        flex-direction: row;
        width: 35%;
        align-self: center;
        justify-content: space-between;
    }
    
    .no-style {
        color: initial;
        text-decoration: none;
    }
    
    .button {
        text-decoration: none;
        color: initial;
        
        border: 0.25em solid #D0D0D0;
        border-radius: 0.25em;
        
        padding: 0.1em 0.25em;
        background-color: #E6E6E6;
    }
    
    :hover {
        cursor: pointer;
    }
    
    :active {
        background-color: #D6D6D6;
        border: 0.3em solid #C6C6C6;
    }
    
    :invalid {
    }
    """

    # TODO: Look into better way to resolve server address
    def get_server_address(self):
        return "http://drd.buzz"
        # host = self.server.server_name
        # port = self.server.server_port
        # return self.server_address % {"host": host, "port": port}

    # send_page: accepts a response code, page title, and page body
    # then sends a well-formatted HTML response to the requester
    # TODO: Improve header information
    def send_page(self, code, title, page):
        self.send_response(code)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        self.wfile.write(bytes("<html>", "utf-8"))
        self.wfile.write(bytes(
            """<head>
                <style>%(css)s</style>
                <title>%(name)s - %(title)s</title>
            </head>"""
            % {"css": self.css_format, "name": self.name, "title": title}, "utf-8"))
        self.wfile.write(bytes(  # TODO: Header link may need a revisit
            """<body>
                <div class="page">
                    <a href="/" class="no-style"><h1>%(name)s</h1></a><hr>
                    %(body)s"""
            % {"name": self.name, "body": page}, "utf-8"))

        if title != "Main Page":
            self.wfile.write(bytes(
                    """<div>
                        <a href="/" class="button">Home Page</a>
                    </div>""", "utf-8"))

        self.wfile.write(bytes(
                """</div>
            </body>""", "utf-8"))

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
    def redirect(self, code, link):
        self.send_response(code)
        self.send_header("location", link)
        self.end_headers()
        return

    # do_GET: GET request handler
    # TODO: Move HTML pages to external resource
    def do_GET(self):
        # This line gets the path as a list of arguments,
        # Stripping off the leading slash
        args = str(self.path)[1:].split('/')

        if args[0] == '':
            self.send_page(200, "Main Page",

                           """<h2>Welcome to the Domain ReDirector!</h2><br>
                           <div>
                            <div>
                                <a href="/register" class="button">Create a New Shortlink</a>
                                <a href="/remove-id" class="button">Remove an Existing Shortlink</a>
                            </div>
                            <div>
                                <a href="/update" class="button">Update a Shortlink's Destination</a>
                                <a href="/update-id" class="button">Change a Link's Shortlink</a>
                            </div>
                           </div>
                           """)
            return

        elif args[0] == "register":
            self.send_page(200, "Register a Link",

                           """<h2>Register a New Link</h2><br>
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
            self.send_page(200, "Register A Link",

                           """<h2>Register a New Link With An ID</h2><br>
                           <form method="POST" action="register-id-complete">
                            <div>
                                <label for="link">Link to register: </label>
                                <input type="url" id="link" name="link" required>
                            </div>
                            <div>
                                <label for="ext">%(lim)d-letter ID: </label>
                                <input type="text" id="ext" name="ext" 
                                minlength=%(lim)d maxlength=%(lim)d pattern="[A-Za-z]{%(lim)d}" required>
                            </div>
                            <div>
                                <input type=submit value="Register">
                            </div>
                           </form>""" % {"lim": self.internal_db.char_limit})
            return

        elif args[0] == "remove":
            self.send_page(200, "Remove A Link",

                           """<h2>Remove An Existing Link</h2><br>
                           <div>
                            <p>Please understand that any short links for this link will
                            no longer work after removal.</p>
                           </div>
                           <form method="POST" action="remove-complete">
                            <div>
                                <label for="link">Link to remove: </label>
                                <input type="url" id="link" name="link" required>
                            </div>
                            <div>
                                <input type=submit value="Remove">
                            </div>
                           </form>""")
            return

        elif args[0] == "remove-id":
            self.send_page(200, "Remove A Shortlink",

                           """<h2>Remove An Existing Shortlink</h2><br>
                           <div>
                            <p>Please understand that the Shortlink <b>%(link)s</b> will
                            no longer work after removal.</p>
                           </div>
                           <form method="POST" action="remove-id-complete">
                            <div>
                                <label for="ext">%(lim)d-letter ID: </label>
                                <input type="text" id="ext" name="ext" 
                                minlength=%(lim)d maxlength=%(lim)d pattern="[A-Za-z]{%(lim)d}" required>
                            </div>
                            <div>
                                <input type=submit value="Remove">
                            </div>
                           </form>"""
                           % {"link": self.get_server_address() + "/&lt;ID&gt;", "lim": self.internal_db.char_limit})
            return

        elif args[0] == "update":
            self.send_page(200, "Update A Link",

                           """<h2>Update An Existing Link</h2><br>
                           <div>
                            <p>Please understand that any Shortlinks for this link will
                            no longer work after update.</p>
                           </div>
                           <form method="POST" action="update-complete">
                            <div>
                                <label for="link">Link to update: </label>
                                <input type="url" id="link" name="link" required>
                            </div>
                            <div>
                                <label for="ext">New %(lim)d-letter ID: </label>
                                <input type="text" id="ext" name="ext" 
                                minlength=%(lim)d maxlength=%(lim)d pattern="[A-Za-z]{%(lim)d}" required>
                            </div>
                            <div>
                                <input type=submit value="Update">
                            </div>
                           </form>"""
                           % {"lim": self.internal_db.char_limit})
            return

        elif args[0] == "update-id":
            self.send_page(200, "Update A Shortlink",

                           """<h2>Update An Existing Shortlink</h2><br>
                           <div>
                            <p>Please understand that the Shortlink <b>%(link)s</b> will
                            point to the new location after update.</p>
                           </div>
                           <form method="POST" action="update-id-complete">
                            <div>
                                <label for="ext">%(lim)d-letter ID: </label>
                                <input type="text" id="ext" name="ext" 
                                minlength=%(lim)d maxlength=%(lim)d pattern="[A-Za-z]{%(lim)d}" required>
                            </div>
                            <div>
                                <label for="link">New link: </label>
                                <input type="url" id="link" name="link" required>
                            </div>
                            <div>
                                <input type=submit value="Update">
                            </div>
                           </form>"""
                           % {"link": self.get_server_address() + "/<ID>", "lim": self.internal_db.char_limit})
            return

        elif args[0] == "teapot":
            self.send_error(418,
                            "I'm a teapot!",
                            "Short and stout!")
            return

        # Redirection handler
        # If this is a valid short link, and the link exists,
        # Redirect to the target website
        elif args[0].isalpha() and len(args[0]) <= self.internal_db.char_limit:
                link_id = stoid(args[0])
                link = self.internal_db.get_link_by_id(link_id)
                if link:
                    self.redirect(301, link)
                    return

        # If nothing catches a wayward request, send it to the 404 page.
        self.send_error(404,
                        "Page Not Found",
                        "It looks like the page you're looking for doesn't exist.")
        return

    # do_POST: POST request handler
    # TODO: Move HTML pages to external resource
    def do_POST(self):
        args = self.path[1:].split('/')

        if args[0] == "register-complete":
            form_dict = self.process_form()
            link = str(unquote(form_dict["link"]))

            if self.internal_db.get_id_by_link(link):
                self.redirect(308, "link-already-registered")
                return

            new_id = self.internal_db.add_rand(link)
            link_ext = idtos(new_id)

            self.send_page(201, "Registration Complete",
                           """<h2>Registration Complete!</h2><br>
                           <p>Thank you! Your link <b>(%(link)s)</b> has been registered!</p>
                           <p>Your new short link is 
                            <a href="%(host)s/%(ext)s" target="_blank"><b>%(host)s/%(ext)s</b></a>
                           </p>"""
                           % {"link": link, "host": self.get_server_address(), "ext": link_ext})
            return
        elif args[0] == "register-id-complete":
            form_dict = self.process_form()
            link = str(unquote(form_dict["link"]))
            link_ext = str(form_dict["ext"]).upper()
            if self.internal_db.get_id_by_link(link):
                self.redirect(308, "link-already-registered")
                return

            link_id = stoid(link_ext)
            new_id = self.internal_db.add_with_id(link, link_id)
            if new_id >= 0:

                self.send_page(201, "Registration Complete",
                               """<h2>Registration Complete!</h2><br>
                               <p>Thank you! Your link <b>(%(link)s)</b> has been registered with the ID: %(ext)s!</p>
                               <p>Your new short link is 
                            <a href="%(host)s/%(ext)s" target="_blank"><b>%(host)s/%(ext)s</b></a>
                           </p>"""
                            % {"link": link, "host": self.get_server_address(), "ext": link_ext})
                return
            elif new_id == -1:
                self.redirect(308, "id-taken")
                return
            elif new_id == -2:
                self.redirect(308, "id-invalid")
                return
            # TODO: Add 500 server error catch

        elif args[0] == "remove-complete":
            form_dict = self.process_form()
            link = str(unquote(form_dict["link"]))
            link_id = self.internal_db.remove_by_link(link)

            if link_id >= 0:
                self.send_page(201, "Removal Complete",
                               """<h2>Removal Complete!</h2><br>
                               <p>The link <b>(%(link)s)</b> has been removed from our database.</p>"""
                               % {"link": link})
                return
            else:
                self.redirect(308, "link-not-found")
                return

        elif args[0] == "remove-id-complete":
            form_dict = self.process_form()
            link_ext = str(form_dict["ext"]).upper()

            link_id = stoid(link_ext)
            old_id = self.internal_db.remove_by_id(link_id)
            if old_id >= 0:
                self.send_page(201, "Removal Complete",
                               """<h2>Removal Complete!</h2><br>
                               <p>The ID <b>(%(ext)s)</b> has been unregistered from our database.</p>"""
                               % {"ext": link_ext})
                return
            elif old_id == -1:
                self.redirect(308, "id-not-found")
                return
            elif old_id == -2:
                self.redirect(308, "id-invalid")
                return
            # TODO: Add 500 server error catch

        elif args[0] == "update-complete":
            form_dict = self.process_form()
            link = str(unquote(form_dict["link"]))
            link_ext = str(form_dict["ext"]).upper()
            link_id = stoid(link_ext)
            new_id = self.internal_db.update_by_link(link, link_id)
            if new_id >= 0:
                self.send_page(201, "Update Complete",
                               """<h2>Update Complete!</h2><br>
                               <p>The link <b>(%(link)s)</b> has been moved to the address 
                               <a href=%(addr)s target="_blank"><b>%(addr)s</b></a>.</p>"""
                               % {"link": link, "addr": self.get_server_address() + "/" + link_ext})
                return
            elif new_id == -1:
                self.redirect(308, "id-taken")
                return
            elif link_id == -2:
                self.redirect(308, "id-invalid")
                return
            elif link_id == -3:
                self.redirect(308, "link-not-found")
                return

        elif args[0] == "update-id-complete":
            form_dict = self.process_form()
            link = str(unquote(form_dict["link"]))
            link_ext = str(form_dict["ext"]).upper()
            link_id = stoid(link_ext)
            old_id = self.internal_db.update_by_link(link, link_id)
            if old_id >= 0:
                self.send_page(201, "Update Complete",
                               """<h2>Update Complete!</h2><br>
                               <p>The link <b>(%(link)s)</b> has been moved to the ID: <b>%(ext)s</b>.</p>
                               <p>Its new Shortlink is: 
                               <a href="%(addr)s" target="blank"><b>%(addr)s</b></a>.</p>"""
                               % {"link": link, "ext": link_ext, "addr": self.get_server_address() + "/" + link_ext})
                return
            elif old_id == -1:
                self.redirect(308, "id-not-found")
                return
            elif old_id == -2:
                self.redirect(308, "id-invalid")
                return
            # TODO: Add 500 server error catch

        # Soft Error Pages
        # These pages handle "soft errors" - not severe enough to crash the server,
        # but notable enough to deserve a response to the client
        elif args[0] == "link-already-registered":
            form_dict = self.process_form()
            link = str(unquote(form_dict["link"]))
            link_id = self.internal_db.get_id_by_link(link)
            link_ext = idtos(link_id)

            self.send_page(201, "Link Already Registered",
                           """<h2>Your Link Was Already Registered.</h2><br>
                           <p>Your link <b>(%(link)s)</b> has already been registered in our database.</p>
                           <p>Its short link is 
                            <a href="%(host)s/%(ext)s"><b>%(host)s/%(ext)s</b></a>
                           </p>
                           <button onclick="history.back()">Go Back</button>
                            """
                           % {"link": link, "host": self.get_server_address(), "ext": link_ext})
            return

        elif args[0] == "link-not-found":
            form_dict = self.process_form()
            link = str(unquote(form_dict["link"]))

            self.send_page(201, "Link Not Found",
                           """<h2>Your Link Was Not Found.</h2><br>
                           <p>The link you are trying to modify <b>(%(link)s)</b> does not appear to be in our database.</p>
                           <button onclick="history.back()">Go Back</button>
                            """
                           % {"link": link})
            return

        elif args[0] == "id-taken":
            form_dict = self.process_form()
            link_ext = str(form_dict["ext"]).upper()

            self.send_page(201, "ID Taken",
                           """<h2>Your ID Was Already Registered.</h2><br>
                           <p>Your chosen ID <b>(%(ext)s)</b> was already registered
                           in our database. Sorry about that.</p>
                           <button onclick="history.back()">Go Back</button>
                            """
                           % {"ext": link_ext})
            return

        elif args[0] == "id-not-found":
            form_dict = self.process_form()
            link_ext = str(unquote(form_dict["ext"])).upper()

            self.send_page(201, "ID Not Found",
                           """<h2>Your ID Was Not Found.</h2><br>
                           <p>The ID you are trying to modify <b>(%(ext)s)</b>
                            doesn't seem to exist in our database.</p>
                           <button onclick="history.back()">Go Back</button>
                            """
                           % {"ext": link_ext})
            return

        elif args[0] == "id-invalid":
            form_dict = self.process_form()
            link_ext = str(form_dict["ext"]).upper()
            self.send_page(201, "ID Invalid",
                           """<h2>Your ID Was Invalid.</h2><br>
                           <p>Your chosen ID <b>(%(ext)s)</b> was invalid. It could be that
                            the ID was too long or short, or contained characters
                            other than letters.</p>
                            <button onclick="history.back()">Go Back</button>
                            """
                           % {"ext": link_ext})
            return

        # If nothing catches a wayward request, send it to the 404 page.
        self.send_error(404,
                        "Page Not Found",
                        "It looks like the page you're looking for doesn't exist.")
        return
