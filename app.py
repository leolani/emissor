import os

from grmc.endpoint import app

if __name__ == "__main__":
    app_path = os.path.dirname(os.path.realpath(__file__))
    app.debug = True
    app.run(ssl_context=(os.path.join(app_path, 'cert.pem'), os.path.join(app_path, 'key.pem')),
            threaded=False,
            processes=1)
