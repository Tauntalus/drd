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

    # URL validation
    if link:
        link = str(unquote(link))
        try:
            val = urlparse(link)
        except ValueError as e:
            print("Validator: Link is not a valid URL.")
            print("Validator: %(link)s" % {"link": link})
            link_flag = -1
    else:
        print("Validator: No link in form data.")
        link_flag = 1
    # Character ID validation
    if ext:
        ext = str(ext)
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
def handle_post(args, form_data, charset, id_limit, max_fails):
    # TODO: Improve information control on DB schemas
    fail_flag = False

    # Default to 404
    code = 404
    title = "Page Not Found"
    body = "It looks like the page you're looking for doesn't exist."
    inserts = {}

    # Validation of form data
    link_flag, ext_flag = validate_form_data(form_data, charset, id_limit)
    if link_flag < 0:
        code = 308
        body = "link-invalid"

    elif ext_flag < 0:
        code = 308
        body = "id-invalid"

    else:
        if len(args) > 0:
            conn = database.try_connect_db("db/drd.db")
            if conn:
                conn = database.try_create_table(conn, "links", ("id", "link"), True)
                if conn:
                    ret = None
                    link = None
                    link_id = None

                    if not link_flag:
                        link = str(unquote(form_data["link"]))
                    if not ext_flag:
                        link_id = stoid(str(form_data["ext"]), charset)

                    # At this point, we've established that the data is well-ordered,
                    # but requests can still be pointed in the wrong directions or
                    # maliciously omit fields. Moving forward,
                    # the response defaults to "bad request"
                    code = 400
                    title = "Bad POST Request"
                    body = "The form data we received from you doesn't match what we were expecting."

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
                                                                 "SELECT id FROM links",
                                                                 link)

                                # Generate new, unique ID within bounds
                                link_id = randrange(pow(len(charset), id_limit))
                                fails = 0
                                while (link_id,) in ret:
                                    link_id = randrange(pow(len(charset), id_limit))
                                    fails += 1

                                # Too many fails = upgrade DB storage
                                if fails >= max_fails:
                                    id_limit += 1
                                    fail_flag = True
                                    print("POST Handler: Too many fails during DB insertion!")
                                    print("POST Handler: Increased ID length to %(lim)d." % {"lim": id_limit})

                                conn = database.try_insert(conn, "links", (link_id, link))

                                # Finally, build the HTML response
                                link_ext = idtos(link_id, charset, id_limit)

                                code = 201
                                title = "Registration Complete"
                                body = """
                                <h2>Registration Complete!</h2><br>
                                <p>Thank you! Your link <b>(%(link)s)</b> has been registered!</p>
                                <p>Your new short link is 
                                    <a href="%(host)s/%(ext)s" target="_blank"><b>%(host)s/%(ext)s</b></a>
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
                                conn, ret = database.try_insert(conn, "links", (link_id, link))
                                link_ext = idtos(link_id, charset, id_limit)
                                code = 201
                                title = "Registration Complete"
                                body = """
                                <h2>Registration Complete!</h2><br>
                                <p>Thank you! Your link <b>(%(link)s)</b> has been registered with the ID: %(ext)s!</p>
                                <p>Your new short link is 
                                    <a href="%(host)s/%(ext)s" target="_blank"><b>%(host)s/%(ext)s</b></a>
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
                                <h2>Removal Complete!</h2><br>
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
                                link_ext = idtos(link_id, charset, id_limit)
                                code = 201
                                title = "Removal Complete",
                                body = """
                                <h2>Removal Complete!</h2><br>
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
                                    link_ext = idtos(link_id, charset, id_limit)
                                    code = 201
                                    title = "Update Complete"
                                    body = """
                                    <h2>Update Complete!</h2><br>
                                    <p>The link <b>(%(link)s)</b> has been moved to the address 
                                        <a href="%(host)s/%(ext)s" target="_blank"><b>%(host)s/%(ext)s</b></a>
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
                                    link_ext = idtos(link_id, charset, id_limit)
                                    code = 201
                                    title = "Update Complete"
                                    body = """
                                    <p>The link <b>(%(link)s)</b> has been moved to the ID: <b>%(ext)s</b>.</p>
                                    <p>Its new Shortlink is: 
                                        <a href="%(host)s/%(ext)s" target="_blank"><b>%(host)s/%(ext)s</b></a>
                                    </p>"""
                                    inserts["link"] = link
                                    inserts["ext"] = link_ext

                    # Soft Error Pages
                    # These pages handle "soft errors" - not severe enough to crash the server,
                    # but notable enough to deserve a response to the client
                    elif args[0] == "link-registered":
                        pass
                    elif args[0] == "link-not-found":
                        pass
                    elif args[0] == "link-invalid":
                        pass
                    elif args[0] == "id-registered":
                        pass
                    elif args[0] == "id-not-found":
                        pass
                    elif args[0] == "id-invalid":
                        pass
                    elif args[0] == "bad-request":
                        pass

                    # Sanity check - if return is None, DB Query broke and we need to stop
                    if not ret:
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

    return code, title, body, inserts, fail_flag

            if args[0] == "register":
                if self.internal_db.get_id_by_link(link):
                    self.redirect(308, "link-already-registered")
                    return

                link_id = self.internal_db.add_rand(link)
                link_ext = idtos(link_id)

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
                link_id = self.internal_db.add_with_id(link, link_id)
                if link_id >= 0:

                    self.send_page(201, "Registration Complete",
                                   """<h2>Registration Complete!</h2><br>
                                   <p>Thank you! Your link <b>(%(link)s)</b> has been registered with the ID: %(ext)s!</p>
                                   <p>Your new short link is 
                                <a href="%(host)s/%(ext)s" target="_blank"><b>%(host)s/%(ext)s</b></a>
                               </p>"""
                                   % {"link": link, "host": self.get_server_address(), "ext": link_ext})
                    return
                elif link_id == -1:
                    self.redirect(308, "id-taken")
                    return
                elif link_id == -2:
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
                link_id = self.internal_db.update_by_link(link, link_id)
                if link_id >= 0:
                    self.send_page(201, "Update Complete",
                                   """<h2>Update Complete!</h2><br>
                                   <p>The link <b>(%(link)s)</b> has been moved to the address 
                                   <a href=%(addr)s target="_blank"><b>%(addr)s</b></a>.</p>"""
                                   % {"link": link, "addr": self.get_server_address() + "/" + link_ext})
                    return
                elif link_id == -1:
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
                                   % {"link": link, "ext": link_ext,
                                      "addr": self.get_server_address() + "/" + link_ext})
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
