from handler import Handler
from http.server import HTTPServer
import configparser

# Main Method - kick up server, watch for interrupt
def main():
    # Get server info from .ini file
    cfg = configparser.ConfigParser()
    cfg.read("settings.ini")
    host = cfg["site"]["host"]
    port = int(cfg["site"]["port"])

    ws = HTTPServer((host, port), Handler)
    print("Server started at http://%(host)s on port %(port)s." % {"host": host, "port": port})

    try:
        ws.serve_forever()
    except KeyboardInterrupt:
        pass

    ws.server_close()
    print("Server shut down.")


if __name__ == "__main__":
    main()
