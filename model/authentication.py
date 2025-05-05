from flask import *
from werkzeug.security import *
from ORM import *
from model.studenti import *
from model.docenti import *
from model.admin import *
from flask_login import *
from model.User import *
from model.docenti import *
from model.studenti import *

# Dichiarazione del blueprint
blueprint = Blueprint('autenticazione', __name__, url_prefix='/autenticazione')

# Funzione per caricare la pagina di login
@blueprint.route('/index', methods=['GET', 'POST'])
def autentication_index():
    return render_template('main/login.html')

# Funzione che permette di effettuare il login, verificando che l'utente sia presente nel database e che la password sia corretta
# Inoltre salva in sessione l'id dell'utente che ha effettuato il login e fa il redirect alla pagina corretta in base al tipo di utente
@blueprint.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        utente = db_session.query(Utenti).filter(Utenti.email == email).first()

        if utente is not None and check_password_hash(utente.password, password):
            user = User(email, password)
            login_user(user)

            user_typeS = db_session.query(Utenti).join(Studenti, Utenti.email == Studenti.emailS).filter(Utenti.email == email).first()
            user_typeD = db_session.query(Utenti).join(Docenti, Utenti.email == Docenti.emailD).filter(Utenti.email == email).first()

            if utente.isAdmin is True:

                session.clear()
                session['session_id'] = User.get_id(user)

                return new_student()
            else:

                if user_typeS is not None:

                    session.clear()
                    session['session_id'] = User.get_id(user)

                    return studenti_id()

                elif user_typeD is not None:

                    session.clear()
                    session['session_id'] = User.get_id(user)

                    return anagrafica_docente()

        else:

            flash("Email e/o Password errati", "danger")

    return autentication_index()

# Funzione per effettuare il logout
# Inoltre cancella la sessione e fa il redirect alla pagina di login
@blueprint.route('/logout')
def logout():
    logout_user()
    session.clear()
    return autentication_index()
