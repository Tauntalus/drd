from urllib.parse import urlparse, unquote
from re import search
from random import randrange

import database
from stoid import stoid, idtos


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

                    # Anyways, with the DB connection established,
                    # it's time to start making queries and building pages!
                    if args[0] == "register":
                        if not link_flag:
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
                                title = "Registration Complete"
                                body = """
                                <h2>Registration Complete!</h2>
                                <br>
                                <p>Thank you! Your link <b>(%(link)s)</b> has been registered!</p>
                                <p>Your new short link is 
                                    <a href="/%(ext)s" target="_blank"><b>%(host)s/%(ext)s</b></a>
                                </p>"""
                                inserts["link"] = link
                                inserts["ext"] = link_ext

                    elif args[0] == "register-id":
                        if not link_flag and not ext_flag:
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
                                title = "Registration Complete"
                                body = """
                                <h2>Registration Complete!</h2>
                                <br>
                                <p>Thank you! Your link <b>(%(link)s)</b> has been registered with the ID: %(ext)s!</p>
                                <p>Your new short link is 
                                    <a href="/%(ext)s" target="_blank"><b>%(host)s/%(ext)s</b></a>
                                </p>"""
                                inserts["link"] = link
                                inserts["ext"] = link_ext

                    elif args[0] == "remove":
                        if not link_flag:
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
                                title= "Removal Complete",
                                body = """
                                <h2>Removal Complete!</h2>
                                <br>
                                <p>The link <b>(%(link)s)</b> has been removed from our database.</p>"""
                                inserts["link"] = link

                    elif args[0] == "remove-id":
                        if not ext_flag:
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
                                title = "Removal Complete",
                                body = """
                                <h2>Removal Complete!</h2>
                                <br>
                                <p>The ID <b>(%(ext)s)</b> has been unregistered from our database.</p>"""
                                inserts["ext"] = link_ext

                    elif args[0] == "update":
                        if not link_flag and not ext_flag:
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
                                    title = "Update Complete"
                                    body = """
                                    <h2>Update Complete!</h2>
                                    <br>
                                    <p>The link <b>(%(link)s)</b> has been moved to the address 
                                        <a href="/%(ext)s" target="_blank"><b>%(host)s/%(ext)s</b></a>
                                    </p>"""
                                    inserts["link"] = link
                                    inserts["ext"] = link_ext

                    elif args[0] == "update-id":
                        if not link_flag and not ext_flag:
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
                                    title = "Update Complete"
                                    body = """
                                    <h2>Update Complete!</h2>
                                    <br>
                                    <p>The Shortlink 
                                        <a href="/%(ext)s" target="_blank"><b>%(host)s/%(ext)s</b></a>
                                    has been moved to the address: <b>%(link)s</b>.</p>"""
                                    inserts["link"] = link
                                    inserts["ext"] = link_ext

                    # Soft Error Pages
                    # These pages handle "soft errors" - not severe enough to crash the server,
                    # but notable enough to deserve a response to the client
                    elif args[0] == "link-registered":
                        if not link_flag:
                            conn, ret = database.try_execute(conn,
                                                             "SELECT * FROM links WHERE link=?",
                                                             link)
                            link_id = ret[0][0]
                            link_ext = idtos(link_id, charset, id_limit)

                            code = 201
                            title = "Link Already Registered"
                            body = """
                            <h2>Your Link Was Already Registered.</h2>
                            <br>
                            <p>Your link <b>(%(link)s)</b> has already been registered in our database.</p>
                            <p>Its short link is 
                                <a href="%(host)s/%(ext)s"><b>%(host)s/%(ext)s</b></a>
                            </p>
                            <button onclick="history.back()">Go Back</button>"""
                            inserts["link"] = link
                            inserts["ext"] = link_ext

                    elif args[0] == "link-not-found":
                        if not link_flag:
                            code = 201
                            title = "Link Not Found"
                            body ="""
                            <h2>Your Link Was Not Found.</h2>
                            <br>
                            <p>The link you are trying to modify <b>(%(link)s)</b> does not appear to be in our database.</p>
                            <button onclick="history.back()">Go Back</button> """
                            inserts["link"] = link

                    elif args[0] == "link-invalid":
                        if not link_flag:
                            code = 201
                            title = "Link Invalid"
                            body = """
                            <h2>Your Link Was Invalid.</h2>
                            <br>
                            <p>Your link was invalid.</p>
                            <button onclick="history.back()">Go Back</button>"""
                            inserts["link"] = link

                    elif args[0] == "id-registered":
                        if not ext_flag:
                            code = 201
                            title = "ID Already Registered"
                            body = """<h2>Your ID Was Already Registered.</h2><br>
                            <p>Your chosen ID <b>(%(ext)s)</b> was already registered
                             in our database. Sorry about that.</p>
                            <button onclick="history.back()">Go Back</button>"""
                            inserts["ext"] = link_ext

                    elif args[0] == "id-not-found":
                        if not ext_flag:
                            code = 201
                            title = "ID Not Found"
                            body = """
                            <h2>Your ID Was Not Found.</h2>
                            <br>
                            <p>The ID you are trying to modify <b>(%(ext)s)</b>
                            doesn't seem to exist in our database.</p>
                            <button onclick="history.back()">Go Back</button>"""

                    elif args[0] == "id-invalid":
                        if not ext_flag:
                            code = 201
                            title = "ID Invalid"
                            body = """
                            <h2>Your ID Was Invalid.</h2>
                            <br>
                            <p>Your chosen ID was invalid. It could be that
                            the ID was too long or short, or contained characters
                            other than letters.</p>
                            <button onclick="history.back()">Go Back</button>"""
                    # Bad path! 404 time
                    else:
                        code = 404
                        title = "Page Not Found"
                        body = "It looks like the page you're looking for doesn't exist."

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

    page = body % inserts
    return code, title, page, fail_flag
