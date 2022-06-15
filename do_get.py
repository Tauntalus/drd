

# handle_get: Accepts args[] representing a split URL and returns
# a HTTP response <code>, a page <title>, and a page <body>
# TODO: Move HTML pages to external resource
def handle_get(args):
    # Default to 404
    code = 404
    title = "Page Not Found"
    body = "It looks like the page you're looking for doesn't exist."
    inserts = {}

    if len(args) > 0:
        if args[0] == '':
            code = 200
            title = "Main Page"
            body = """
            <h2>Welcome to the Domain ReDirector!</h2><br>
            <div>
                <div>
                    <a href="/register" class="button">Create a New Shortlink</a>
                    <a href="/remove-id" class="button">Remove an Existing Shortlink</a>
                </div>
                <div>
                    <a href="/update" class="button">Update a Shortlink's Destination</a>
                    <a href="/update-id" class="button">Change a Link's Shortlink</a>
                </div>
            </div>"""

        elif args[0] == "register":
            code = 200
            title = "Register a Link"

            body = """
            <h2>Register a New Link</h2><br>
            <form method="POST" action="register">
                <div>
                    <label for="link">Link to register: </label>
                    <input type="url" id="link" name="link" required>
                </div>
                <div>
                    <input type=submit value="Register">
                </div>
            </form>"""

        elif args[0] == "register-id":
            code = 200
            title = "Register A Link"

            body = """
            <h2>Register a New Link With An ID</h2><br>
            <form method="POST" action="register-id">
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
            </form>"""

        elif args[0] == "remove":
            code = 200
            title = "Remove A Link"

            body = """
            <h2>Remove An Existing Link</h2><br>
            <div>
                <p>Please understand that any short links for this link will
                no longer work after removal.</p>
            </div>
            <form method="POST" action="remove">
                <div>
                    <label for="link">Link to remove: </label>
                    <input type="url" id="link" name="link" required>
                </div>
                <div>
                    <input type=submit value="Remove">
                </div>
            </form>"""

        elif args[0] == "remove-id":
            code = 200
            title = "Remove A Shortlink"

            body = """
            <h2>Remove An Existing Shortlink</h2><br>
            <div>
                <p>Please understand that the Shortlink <b>%(addr)s</b> will
                no longer work after removal.</p>
            </div>
            <form method="POST" action="remove-id">
                <div>
                    <label for="ext">%(lim)d-letter ID: </label>
                    <input type="text" id="ext" name="ext" 
                    minlength=%(lim)d maxlength=%(lim)d pattern="[A-Za-z]{%(lim)d}" required>
                </div>
                <div>
                    <input type=submit value="Remove">
                </div>
            </form>"""

        elif args[0] == "update":
            code = 200
            title = "Update A Link"

            body = """
            <h2>Update An Existing Link</h2><br>
            <div>
                <p>Please understand that any Shortlinks for this link will
                no longer work after update.</p>
            </div>
            <form method="POST" action="update">
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

        elif args[0] == "update-id":
            code = 200
            title = "Update A Shortlink"

            body = """
            <h2>Update An Existing Shortlink</h2><br>
            <div>
                <p>Please understand that the Shortlink <b>%(addr)s</b> will
                point to the new location after update.</p>
            </div>
            <form method="POST" action="update-id">
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

        elif args[0] == "teapot":
            code = 418
            title = "I'm a teapot!"
            body = "Short and stout!"

    return code, title, body, inserts
