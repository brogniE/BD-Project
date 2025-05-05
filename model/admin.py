from datetime import *

from flask import *
from flask_sqlalchemy import *
from sqlalchemy import *
from werkzeug.security import generate_password_hash

from DB import *
from ORM import *
from datetime import *

db_session = get_session()

blueprint = Blueprint('admin', __name__, url_prefix='/admin')

#funzione per caricare la pagina per l'inserimenro di un nuovo professore
@blueprint.route('/new_professor', methods=['GET', 'POST'])
def new_professor():
    # controlla se è stato effettuato il login
    if session.get('session_id') is None:
        return redirect(url_for('autenticazione.login'))

    return render_template('admin/new_professor.html')

#funzione per l'inserimento di un nuovo professore
@blueprint.route('/conferma_docente', methods=['GET', 'POST'])
def conferma_docente():
    if session.get('session_id') is None:
        return redirect(url_for('autenticazione.login'))

    #query per l'inserimento di un nuovo docente
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        nome = request.form['nome']
        cognome = request.form['cognome']
        datanascita = request.form['data']
        dipartimento = request.form['dipartimento']
        telefono = request.form['telefono']

        try:
            db_session.add(Utenti(email = email, password = generate_password_hash(password), nome = nome, cognome = cognome, telefono=telefono, dataNascita=datanascita, isAdmin=False))
            db_session.add(Docenti(emailD = email, dipartimento= dipartimento))
            db_session.commit()
            flash("docente aggiunto con successo", "success")
        except Exception as e:
            db_session.rollback()
            print(e)
            flash("errore nell'inserimento del docente", "danger")

    return render_template('admin/new_professor.html')

#funzione per caricare la pagina per l'inserimenro di un nuovo studente
@blueprint.route('/new_student', methods=['GET', 'POST'])
def new_student():
    if session.get('session_id') is None:
        return redirect(url_for('autenticazione.login'))

    return render_template('admin/new_student.html')

#funzione per l'inserimento di un nuovo studente
@blueprint.route('/conferma_studente', methods=['GET', 'POST'])
def conferma_studente():
    if session.get('session_id') is None:
        return redirect(url_for('autenticazione.login'))

    #query per l'inserimento di un nuovo studente

    # query per l'inserimento di un nuovo studente
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        nome = request.form['nome']
        cognome = request.form['cognome']
        datanascita = request.form['data']
        telefono = request.form['telefono']
        matricola = request.form['matricola']
        facolta = request.form['facolta']

        try:
            db_session.add(Utenti(email=email, password=generate_password_hash(password), nome=nome, cognome=cognome,
                                  telefono=telefono, dataNascita=datanascita, isAdmin=False))
            db_session.add(
                Studenti(emailS=email, matricola=matricola, facolta=facolta, annoIscrizione=date.today().year))
            db_session.commit()
            flash("studente aggiunto con successo", "success")
        except Exception as e:
            db_session.rollback()
            print(e)
            flash("errore nell'inserimento dello studente", "danger")


    return new_student()