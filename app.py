from grmc.endpoint import app

if __name__ == "__main__":
    app.debug = True
    app.run(ssl_context=('/Users/tkb/.ssh/flask/cert.pem', '/Users/tkb/.ssh/flask/key.pem'),
            threaded=False,
            processes=1)
