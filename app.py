from grmc.endpoint import app

if __name__ == "__main__":
    app.debug = True
    app.run(ssl_context='adhoc')