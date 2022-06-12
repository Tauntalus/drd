from src.server import Server_DRD
from http.server import HTTPServer


# Main Method - kick up server, watch for interrupt
def main():
    name = "localhost"
    port = 8080

    ws = HTTPServer((name, port), Server_DRD)
    print("Server started at http://%s on port %s." % (name, port))

    try:
        ws.serve_forever()
    except KeyboardInterrupt:
        pass

    ws.server_close()
    print("Server shut down.")


if __name__ == "__main__":
    main()
