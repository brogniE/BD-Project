from flask import *
from flask_login import *
from model.User import *
from model.studenti import *
from model.docenti import *
from model.admin import *
from model.authentication import *
from ORM import *

app = Flask(__name__)

from model import studenti, docenti, admin, authentication
app.register_blueprint(studenti.blueprint)
app.register_blueprint(docenti.blueprint)
app.register_blueprint(admin.blueprint)
app.register_blueprint(authentication.blueprint)
app.secret_key = "Sachin"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'autenticazione.login'

@login_manager.user_loader
def load_user(user_id):
    return User(user_id,None)

@app.route('/')
def index():
    return autentication_index()

if __name__=='__main__':
    app.run()
