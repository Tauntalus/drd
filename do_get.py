import database
from stoid import stoid
from os.path import isfile

# Dictionary for easy editing of page titles
titles = {
    "index": "Main Page",
    "register": "Register A Link",
    "register-id": "Register A Shortlink",
    "remove": "Remove A Link",
    "remove-id": "Remove A Shortlink",
    "update": "Update A Link",
    "update-id": "Update A Shortlink",
    "teapot": "I'm a Teapot!"
}

# handle_get: Accepts args[] representing a split URL and returns
# a HTTP response <code>, a page <title>, and a page <body>
# TODO: Move HTML pages to external resource
def handle_get(args, context):
    name = context["name"]
    host = context["host"]
    id_limit = context["id_limit"]

    db_file = context["db_file"]
    db_table = context["db_table"]
    db_schema = context["db_schema"]

    charset = context["charset"]
    inserts = {"name": name, "host": host, "lim": id_limit}

    # Default to 404
    code = 404
    title = "Page Not Found"
    body = "It looks like the page you're looking for doesn't exist."

    if len(args) > 0:
        if args[0] in ('', "main", "index"):
            args[0] = "index"
        
        if args[0] in titles.keys():
            code = 200
            title = titles[args[0]]
            body = open("resources/get/" + args[0] + ".html", "r").read()

            #Teapot :D
            if args[0] == "teapot":
                code = 418

        elif args[0].isalpha() and len(args[0]) <= id_limit:
            conn = database.try_connect_db(db_file)
            if conn:
                conn = database.try_create_table(conn, db_table, db_schema, True)
                if conn:
                    ext = args[0].upper()
                    id = stoid(ext, charset)

                    conn, ret = database.try_execute(conn,
                                                     "SELECT * FROM links WHERE id=?",
                                                     id)
                    if len(ret) <= 0:
                        pass
                    elif len(ret) == 1:
                        code = 301
                        body = ret[0][1]
                    else:
                        code = 500
                        title = "Internal Error - Invalid Database Response"
                        body = """The database we use is responding erratically. We've logged what happened and
                                   are looking into why it did."""
                else:
                    code = 500
                    title = "Internal Error - Database Table Inaccessible"
                    body = "We failed to access our database table. We can't do anything without that!"
                conn = database.close(conn)  # Only commit to the DB if operations completed successfully
            else:
                code = 500
                title = "Internal Error - Database Failed To Initialize"
                body = "The connection to our database failed to initialize. We can't do anything without that!"

        # If trying to get a resource, shortcut the system
        else:
            # rebuild filepath
            file_path = ""
            for e in args:
                file_path += e + "/"
            file_path = file_path[:-1]
            print(file_path)
            if isfile("./"+ file_path):
                code = 200
                title = file_path
                body = open(file_path, "r").read()
                return code, title, body

    page = body % inserts
    return code, title, page
