from http.server import BaseHTTPRequestHandler
from do_get import handle_get
from do_post import handle_post

from database import DBInfo


# Handler: Custom HTTP Request Handler
class Handler(BaseHTTPRequestHandler):
    # TODO: BIG TODO!
    # TODO: Make constants pull from a config file!
    name = "Domain ReDirector"
    server_address = "http://drd.buzz"

    db_info = DBInfo("db/links.db", "links", ("id", "link",))
    id_limit = 3

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

    # TODO: Look into dynamic resolution of server address
    def get_server_address(self):
        return self.server_address

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

    # redirect - Redirects the user to a given location
    def redirect(self, code, link):
        self.send_response(code)
        self.send_header("location", link)
        self.end_headers()
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

    def interpret_http_code(self, code, title, body):
        # TODO: Improve responses to different codes
        # Information responses (not implemented)
        if 100 <= code < 200:
            return
        # OK responses
        elif 200 <= code < 300:
            self.send_page(code, title, body)
            return
        # Redirect responses - body contains linked resource
        elif 300 <= code < 400:
            self.redirect(code, body)
            return
        # Client Error responses
        elif 400 <= code < 500:
            self.send_error(code, title, body)
            return
        # Server Error responses
        elif 500 <= code < 600:
            self.send_error(code, title, body)
            return
        # Illegal responses
        else:
            self.send_error(500, "Unknown Error",
                            """Something has gone very, very wrong on our end. 
                            We're working on sorting it out, try checking back later.""")
            return

    # do_GET: GET request handler
    # TODO: Move HTML pages to external resource
    def do_GET(self):
        # This line gets the path as a list of arguments,
        # Stripping off the leading slash
        args = str(self.path)[1:].split('/')

        code, title, body, inserts = handle_get(args)

        # Additional inserts that are only available outside the handler
        # Don't want to have to send more arguments into the function than necessary
        inserts["addr"] = self.server_address
        inserts["lim"] = self.id_limit
        page = body % inserts

        self.interpret_http_code(code, title, page)
        return

    # do_POST: POST request handler
    # TODO: Move HTML pages to external resource
    def do_POST(self):
        args = self.path[1:].split('/')
        form_data = self.process_form()

        code, title, body, inserts = handle_post(args, form_data, self.db_info, self.id_limit)

        # TODO: Potential extra inserts
        page = body % inserts

        self.interpret_http_code(code, title, page)
        return
