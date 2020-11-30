# GRMC Annotations

## Install

* Install node.js
        
        brew install angular-cli
        ng --version
        cd webapp
        ng server
        
* Setup certificate next to `app.py` 

        openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
        
* Setup python

        python -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt

* Run the webserver

        python app.py
        
  When starting the webserver for the first time, visit `https://localhost:5000/api/scenario` in the browser and accept
  the risk. After this the browser accepts the certificate.
  
* Open the webapp at `https://localhost:4200`
  

