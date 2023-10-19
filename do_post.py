from urllib.parse import urlparse, unquote
from re import search
from random import randrange

import database
from stoid import stoid, idtos

# titles dictionary for easy editing
titles = {
    "register": "Registration Complete",
    "register-id": "Registration Complete",
    "remove": "Removal Complete",
    "remove-id": "Removal Complete",
    "update": "Update Complete",
    "update-id": "Update Complete",
    "link-registered": "Link Already Registered",
    "link-not-found": "Link Not Found",
    "link-invalid": "Link Invalid",
    "id-registered": "ID Already Registered",
    "id-not-found": "ID Not Found",
    "id-invalid": "ID Invalid"
}

# validate_form_data: Checks that the data is formatted properly for processing
def validate_form_data(form_data, charset, ext_limit):
    link = form_data.get("link")
    ext = form_data.get("ext")

    link_flag = 0
    ext_flag = 0

    # regexes for validating URLs
    scheme_regex = r'[A-Za-z0-9\-\_\.]+'    # TODO: Make more discerning
    netloc_regex = r'[A-Za-z0-9\-\.]+'      # TODO: Make more discerning
    path_regex = r'[A-Za-z0-9\-\_\/]*'      # TODO: Make more discerning
    # URL validation
    if link:
        link = str(unquote(link))
        try:
            val = urlparse(link)
            test = all([val.scheme, val.netloc])
            if not test:
                raise ValueError
            else:
                t_scheme = search(scheme_regex, val.scheme)
                t_netloc = search(netloc_regex, val.netloc)
                t_path = True
                if val.path:
                    t_path = search(path_regex, val.path)

                if not t_scheme or not t_netloc or not t_path:
                    raise ValueError
        except ValueError as e:
            print("Validator: Link is not a valid URL.")
            print("Validator: %(link)s" % {"link": link})
            link_flag = -1
    else:
        print("Validator: No link in form data.")
        link_flag = 1
    # Character ID validation
    if ext:
        ext = str(ext).upper()
        regex = "[" + charset + "]+"
        if not search(regex, ext) or 0 >= len(ext) > ext_limit:
            print("Validator: Extension is not a valid character sequence.")
            print("Validator: %(ext)s" % {"ext": ext})
            ext_flag = -1
    else:
        print("Validator: No extension in form data.")
        ext_flag = 1
    return link_flag, ext_flag


# TODO: Move HTML pages to external resource
def handle_post(args, form_data, context):
    name = context["name"]
    host = context["host"]

    charset = context["charset"]
    id_limit = context["id_limit"]
    fail_limit = context["fail_limit"]

    db_file = context["db_file"]
    db_table = context["db_table"]
    db_schema = context["db_schema"]

    fail_flag = False

    inserts = {"name": name, "host": host, "lim": id_limit}

    # Validation of form data
    link_flag, ext_flag = validate_form_data(form_data, charset, id_limit)
    if link_flag < 0:
        code = 400
        title = "Invalid Link"
        body = "The link you sent us was not a valid URL."

    elif ext_flag < 0:
        code = 400
        title = "Invalid ID"
        body = "The ID you sent us was not a valid %(lim)d-character ID." % {"lim": id_limit}

    else:
        if len(args) > 0:
            conn = database.try_connect_db(db_file)
            if conn:
                conn = database.try_create_table(conn, db_table, db_schema, True)
                if conn:
                    ret = []
                    link = None
                    link_id = None
                    link_ext = None

                    if not link_flag:
                        link = str(unquote(form_data["link"]))
                    if not ext_flag:
                        link_ext = str(form_data["ext"]).upper()
                        link_id = stoid(link_ext, charset)

                    # At this point, we've established that the data is well-ordered,
                    # but requests can still be pointed in the wrong directions or
                    # maliciously omit fields. Moving forward,
                    # the response defaults to "bad request"
                    code = 400
                    title = "Bad Request"
                    body = "The data we received from you doesn't match what we were expecting."
                    
                    #TODO: lotta boilerplate here, maybe a way to reduce it?
                    # If there is any DB work we need to do, these if statements check for it and run it
                    if args[0] in titles.keys():
                        if args[0] == "register":
                            if not link_flag:
                                conn, ret, code, body, link_ext, fail_flag = register(conn, ret, context, link)

                        elif args[0] == "register-id":
                            if not link_flag and not ext_flag:
                                conn, ret, code, body = register_id(conn, ret, context, link, link_id)

                        elif args[0] == "remove":
                            if not link_flag:
                                conn, ret, code, body = remove(conn, ret, link)

                        elif args[0] == "remove-id":
                            if not ext_flag:
                                conn, ret, code, body = remove_id(conn, ret, link_id)

                        elif args[0] == "update":
                            if not link_flag and not ext_flag:
                                conn, ret, code, body = update(conn, ret, link, link_id)

                        elif args[0] == "update-id":
                            if not link_flag and not ext_flag:
                                conn, ret, code, body = update_id(conn, ret, link, link_id)

                        # Soft Error Pages
                        # These pages handle "soft errors" - not severe enough to crash the server,
                        # but notable enough to deserve a response to the client
                        elif args[0] == "link-registered":
                            if not link_flag:
                                conn, ret, code, body, link_ext = link_registered(conn, ret, context, link)

                        elif args[0] in ("link-not-found", "link-invalid"):
                            if not link_flag:
                                code = 201

                        elif args[0] in ("id-registered", "id-not-found", "id-invalid"):
                            if not ext_flag:
                                code = 201

                    # Bad path! 404 time
                    else:
                        code = 404
                        title = "Page Not Found"
                        body = "It looks like the page you're looking for doesn't exist."

                    # fetch title and body information provided we are returning something via a 2xx code
                    if 200 <= code < 300:
                        title = titles[args[0]]
                        body = open("resources/post/" + args[0] + ".html", "r").read()

                    # Sanity check - if return is None, DB Query broke and we need to stop
                    if ret is None:
                        code = 500
                        title = "Internal Error - Invalid Database Response"
                        body = """The database we use is responding erratically. We've logged what happened and
                               are looking into why it did."""
                    else:
                        conn = database.close(conn)  # Only commit to the DB if operations completed successfully
                else:
                    code = 500
                    title = "Internal Error - Database Table Inaccessible"
                    body = "We failed to access our database table. We can't do anything without that!"
            else:
                code = 500
                title = "Internal Error - Database Failed To Initialize"
                body = "The connection to our database failed to initialize. We can't do anything without that!"
    
    inserts["link"] = link
    inserts["ext"] = link_ext
    page = body % inserts
    return code, title, page, fail_flag

# register: called when /register is given an appropriate POST request.
# takes a context and a link, and registers the link into the shortener database
def register(conn, ret, context, link):
    charset = context["charset"]
    id_limit = context["id_limit"]
    fail_limit = context["fail_limit"]
    db_table = context["db_table"]

    code = 500
    body = None
    link_ext = None
    fail_flag = False

    conn, ret = database.try_execute(conn,
                                        "SELECT * FROM links WHERE link=?",
                                        link)
    if len(ret) > 0:
        code = 308
        body = "link-registered"
    else:
        conn, ret = database.try_execute(conn,
                                            "SELECT id FROM links")

        # Generate new, unique ID within bounds
        link_id = randrange(pow(len(charset), id_limit))
        fails = 0
        while (link_id,) in ret:
            link_id = randrange(pow(len(charset), id_limit))
            fails += 1

        # Too many fails = upgrade DB storage
        if fails >= fail_limit:
            id_limit += 1
            fail_flag = True
            print("POST Handler: Too many fails during DB insertion!")
            print("POST Handler: Increased ID length to %(lim)d." % {"lim": id_limit})
        conn, ret = database.try_insert(conn, db_table, (link_id, link))

        # Finally, build the HTML response
        link_ext = idtos(link_id, charset, id_limit)
        code = 201

    return conn, ret, code, body, link_ext, fail_flag

def register_id(conn, ret, context, link, link_id):
    db_table = context["db_table"]

    code = 500
    body = None

    conn, ret = database.try_execute(conn,
                                        "SELECT * FROM links WHERE link=? OR id=?",
                                        (link, link_id))
    if len(ret) > 0:
        code = 308
        # Because of the bijective flag during DB creation,
        # this check is encompassing.
        # We deliberately prioritize link errors over ID errors.
        if ret[0][1] == link or len(ret) > 1:
            body = "link-registered"
        else:
            body = "id-registered"
    else:
        conn, ret = database.try_insert(conn, db_table, (link_id, link))
        code = 201

    return conn, ret, code, body

def remove(conn, ret, link):
    code = 500
    body = None

    conn, ret = database.try_execute(conn,
                                    "SELECT * FROM links WHERE link=?",
                                    link)
    if len(ret) <= 0:
        code = 308
        body = "link-not-found"
    else:
        conn, ret = database.try_execute(conn,
                                        "DELETE FROM links WHERE link=?",
                                        link)
        code = 201
    
    return conn, ret, code, body

def remove_id(conn, ret, link_id):
    conn, ret = database.try_execute(conn,
                                    "SELECT * FROM links WHERE id=?",
                                    link_id)
    if len(ret) <= 0:
        code = 308
        body = "id-not-found"
    else:
        conn, ret = database.try_execute(conn,
                                        "DELETE FROM links WHERE id=?",
                                        link_id)
        code = 201
    
    return conn, ret, code, body

def update(conn, ret, link, link_id):
    code = 500
    body = None

    conn, ret = database.try_execute(conn,
                                    "SELECT * FROM links WHERE link=? OR id=?",
                                    (link, link_id))
    if len(ret) <= 0:
            code = 308
            body = "link-not-found"
    else:
        if ret[0][0] == link_id or len(ret) > 1:
            code = 308
            body = "id-registered"
        else:
            conn, ret = database.try_execute(conn,
                                            "UPDATE links SET id=?, link=? WHERE link=?",
                                            (link_id, link, link))
            code = 201

    return conn, ret, code, body

def update_id(conn, ret, link, link_id):
    code = 500
    body = None

    conn, ret = database.try_execute(conn,
                                    "SELECT * FROM links WHERE link=? OR id=?",
                                    (link, link_id))
    if len(ret) <= 0:
        code = 308
        body = "id-not-found"
    else:
        if ret[0][1] == link or len(ret) > 1:
            code = 308
            body = "link-registered"
        else:
            conn, ret = database.try_execute(conn,
                                            "UPDATE links SET id=?, link=? WHERE id=?",
                                            (link_id, link, link_id))
            code = 201
    
    return conn, ret, code, body

def link_registered(conn, ret, context, link):
    charset = context["charset"]
    id_limit = context["id_limit"]

    code = 500
    body = None
    conn, ret = database.try_execute(conn,
                                    "SELECT * FROM links WHERE link=?",
                                    link)
    link_id = ret[0][0]
    link_ext = idtos(link_id, charset, id_limit)

    code = 201

    return conn, ret, code, body, link_ext
