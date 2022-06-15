from server import Server_DRD
from http.server import HTTPServer


# Main Method - kick up server, watch for interrupt
def main():
    host = "localhost"
    port = 8080

    ws = HTTPServer((host, port), Server_DRD)
    print("Server started at http://%(host)s on port %(port)s." % {"host": host, "port": port})

    try:
        ws.serve_forever()
    except KeyboardInterrupt:
        pass

    ws.server_close()
    print("Server shut down.")


if __name__ == "__main__":
    main()
