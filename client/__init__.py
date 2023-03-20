from flask import Flask
##from flask_login import LoginManager

app = Flask(__name__)

### Configuration για τα Secret Key, WTF CSRF Secret Key
## Το όνομα του αρχείου της βάσης δεδομένων θα πρέπει να είναι 'flask_movies_database.db'

## using secrets.token_hex(16)
app.config["SECRET_KEY"] = "96fdb43f231194a90fac710e5f88455f"
app.config['WTF_CSRF_SECRET_KEY'] = "11c948b1f966c6a4d21c0397d13ea5b2"

## Αρχικοποίηση της Βάσης, και άλλων εργαλείων
'''
login_manager = LoginManager(app)

login_manager.login_view = "login"
login_manager.login_message_category = "primary"
login_manager.login_message = "Sign in to view this page."
'''
from client import routes
