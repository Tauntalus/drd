from http.server import BaseHTTPRequestHandler
from do_get import handle_get
from do_post import handle_post
import configparser

# Handler: Custom HTTP Request Handler
class Handler(BaseHTTPRequestHandler):
    cfg = configparser.ConfigParser()
    cfg.read("settings.ini")

    # This object contains all the relevant context
    # needed for dynamic request responses.
    context = {
        "name": cfg["site"]["name"],
        "host": cfg["site"]["host"],

        "charset": cfg["database"]["charset"],
        "id_limit": int(cfg["database"]["id_limit"]),
        "fail_limit": int(cfg["database"]["fail_limit"]),

        "db_file": cfg["database"]["db_file"],
        "db_table": cfg["database"]["db_table"],
        "db_schema": ("id", "link")
    }

    error_message_format = """
    <head>
        <title>{} - Error %(code)d</title>
    </head>
    <body>
        <h2>%(message)s</h2>
        <p>%(explain)s</p>
        <a href="/">Main Page</a>
    </body>""".format(context["name"])

    default_format = """
    <html>
        <head>
            <style>%(css)s</style>
            <title>{} - %(title)s</title>
        </head>
        <body>
            <div class="page">
                <a href="/" class="no-style"><h1>%(name)s</h1></a>
                <hr>
                %(body)s
                <br>
                <a href="/" class="button">Main Page</a>
            </div>
        </body>
    </html>""".format(context["name"])

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
        return self.context["server_address"]

    # send_page: accepts a response code, page title, and page body
    # then sends a well-formatted HTML response to the requester
    # TODO: Improve header information
    def send_page(self, code, title, body):
        page = self.default_format % {"css": self.css_format,
                                      "title": title,
                                      "name": self.context["name"],
                                      "body": body}

        self.send_response(code)
        self.send_header("Content-type", "text/html")
        self.send_header('Connection', 'close')
        self.send_header('Content-Length', int(len(page)))
        self.end_headers()
        if self.command != 'HEAD' and code >= 200 and code not in (204, 304):
            self.wfile.write(bytes(page, "utf-8"))
        return

    # redirect - Redirects the user to a given location
    def redirect(self, code, link):
        self.send_response(code)
        self.send_header("location", str(link))
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

    # do_HEAD: HEAD request handler
    def do_HEAD(self):
        self.do_GET()
        return

    # do_GET: GET request handler
    def do_GET(self):
        # This line gets the path as a list of arguments,
        # Stripping off the leading slash
        args = str(self.path)[1:].split('/')

        code, title, body = handle_get(args, self.context)

        self.interpret_http_code(code, title, body)
        return

    # do_POST: POST request handler

    def do_POST(self):
        args = self.path[1:].split('/')
        form_data = self.process_form()

        code, title, body, fail_flag = handle_post(args, form_data, self.context)

        # If during a random insertion, we fail to add an ID a certain amount of times,
        # we permanently increase the length of URLs in the database.
        if fail_flag:
            self.context["id_limit"] += 1

        self.interpret_http_code(code, title, body)
        return
