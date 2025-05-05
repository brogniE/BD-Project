from datetime import *

from flask import *
from flask_sqlalchemy import *
from sqlalchemy import *

from DB import *
from ORM import *

db_session = get_session()

blueprint = Blueprint('studenti', __name__, url_prefix='/studenti')

#funzione per caricare la pagina con i dati anagrafici dello studente
@blueprint.route('/studenti_id/', methods=['GET', 'POST'])
def studenti_id():
    # controlla se è stato effettuato il login
    if session.get('session_id') is None:
        return redirect(url_for('autenticazione.login'))

    idS = session.get('session_id')
    # query che dato emailS di uno studente ne trova i dati anagrafici
    studente = db_session.query(Studenti).join(Utenti, Studenti.emailS == Utenti.email).filter(
        Studenti.emailS == idS).first()

    return render_template('student/anagrafica.html', student=studente)

#funzione per caricare la pagina con gli appelli della stessa facoltà dello studente disponibili
@blueprint.route('/appelli_studente/', methods=['GET', 'POST'])
def appelli_studente():
    if session.get('session_id') is None:
        return redirect(url_for('autenticazione.login'))

    idS = session.get('session_id')
    # query che trova tutti gli appelli dato uno studente emailS che fanno parte del corso (FACOLTA') di cui lo studente fa parte ma di cui non è ancora iscritto  
    iscrizioni = db_session.query(StudentiPrenotati.idA).filter(StudentiPrenotati.emailS == idS).all()
    iscrizioni = [row[0] for row in iscrizioni]
    facoltaStudente = db_session.query(Studenti.facolta).filter(Studenti.emailS == idS)
    lista_appelli = db_session.query(Appelli).\
                    join(Prove, Appelli.idP == Prove.idP).\
                    join(Esami, Prove.idE == Esami.idE).\
                    filter(Esami.facolta == facoltaStudente).\
                    filter(~Appelli.idA.in_(iscrizioni)).all()
    
    
    #lista appelli deve essere una lista contenete oggetti di tipo appello contenenti i campi di appello
    return render_template('student/appelli.html', appelli=lista_appelli)

#funzione per caricare la pagina per la ricerca di un appello tra tutti quelli disponibili
@blueprint.route('/ricerca_appelli/', methods=['GET', 'POST'])
def ricerca_appelli():
    if session.get('session_id') is None:
        return redirect(url_for('autenticazione.login'))

    idS = session.get('session_id')
    # query che trova tutti gli appelli di esami di altre facolà per cui lo studente id non si è ancora iscritto
    iscrizioni = db_session.query(StudentiPrenotati.idA).filter(StudentiPrenotati.emailS == idS).all()
    iscrizioni = [row[0] for row in iscrizioni]
    facoltaStudente = db_session.query(Studenti.facolta).filter(Studenti.emailS == idS)
    lista_appelli = db_session.query(Appelli).\
                    join(Prove, Appelli.idP == Prove.idP).\
                    join(Esami, Prove.idE == Esami.idE).\
                    filter(Esami.facolta != facoltaStudente).\
                    filter(~Appelli.idA.in_(iscrizioni)).all()

    #lista appelli deve essere una lista contenete oggetti di tipo appello contenenti i campi di appello
    return render_template('student/ricerca_appelli.html', appelli=lista_appelli)

#funzione per caricare la pagina per la ricerca di un appello tra tutti quelli disponibili grazie l'uso di una barra di ricerca 
@blueprint.route('/ricerca_appelli_id/', methods=['GET', 'POST'])
def ricerca_appelli_id():
    if session.get('session_id') is None:
        return redirect(url_for('autenticazione.login'))

    idS = session.get('session_id')
    input_value = request.form['searchid']
    searchid = "%{}%".format(input_value)
    iscrizioni = db_session.query(StudentiPrenotati.idA).filter(StudentiPrenotati.emailS == idS).all()
    iscrizioni = [row[0] for row in iscrizioni]
    # query che trova tutti gli appelli di esami di altre facolà per cui lo studente id non si è ancora iscritto che coincidono con la variabile inserita nell'input searchid
    facoltaStudente = db_session.query(Studenti.facolta).filter(Studenti.emailS == idS).scalar_subquery()
    
    result_idE = db_session.query(Appelli).\
                    join(Prove, Appelli.idP == Prove.idP).\
                    join(Esami, Prove.idE == Esami.idE).\
                    filter(Esami.idE.like(searchid), Esami.facolta != facoltaStudente).\
                    filter(~Appelli.idA.in_(iscrizioni)).all()
    
    result_idP = db_session.query(Appelli).\
                    join(Prove, Appelli.idP == Prove.idP).\
                    join(Esami, Prove.idE == Esami.idE).\
                    filter(Prove.idP.like(searchid), Esami.facolta != facoltaStudente).\
                    filter(~Appelli.idA.in_(iscrizioni)).all()
    
    result_corso = db_session.query(Appelli).\
                    join(Prove, Appelli.idP == Prove.idP).\
                    join(Esami, Prove.idE == Esami.idE).\
                    filter(Esami.corso.like(searchid), Esami.facolta != facoltaStudente).\
                    filter(~Appelli.idA.in_(iscrizioni)).all()
    
    result_facolta = db_session.query(Appelli).\
                    join(Prove, Appelli.idP == Prove.idP).\
                    join(Esami, Prove.idE == Esami.idE).\
                    filter(Esami.facolta.like(searchid), Esami.facolta != facoltaStudente).\
                    filter(~Appelli.idA.in_(iscrizioni)).all()
    
    result_tipo = db_session.query(Appelli).\
                    join(Prove, Appelli.idP == Prove.idP).\
                    join(Esami, Prove.idE == Esami.idE).\
                    filter(Prove.tipo.like(searchid), Esami.facolta != facoltaStudente).\
                    filter(~Appelli.idA.in_(iscrizioni)).all()
    
    result_prof = db_session.query(Appelli).\
                    join(Prove, Appelli.idP == Prove.idP).\
                    join(Esami, Prove.idE == Esami.idE).\
                    filter(Prove.idD.like(searchid), Esami.facolta != facoltaStudente).\
                    filter(~Appelli.idA.in_(iscrizioni)).all()

    lista_appelli = result_corso.__add__(result_tipo).\
                                    __add__(result_prof).\
                                    __add__(result_idE).\
                                    __add__(result_idP).\
                                    __add__(result_facolta)
    
    
    if lista_appelli is None:
        lista_appelli = db_session.query(Appelli).\
                        join(Prove, Appelli.idP == Prove.idP).\
                        join(Esami, Prove.idE == Esami.idE).\
                        filter(Esami.facolta != facoltaStudente).all()
  
    #lista appelli deve essere una lista contenete oggetti di tipo appello contenenti i campi di appello
    return render_template('student/ricerca_appelli.html', appelli=lista_appelli)

#funzione per caricare la pagina per la conferma all'iscrizione dell'appello
@blueprint.route('/conferma_appello/<int:idAppello>/', methods=['GET', 'POST'])
def conferma_appello(idAppello):
    if session.get('session_id') is None:
        return redirect(url_for('autenticazione.login'))

    idS = session.get('session_id')
    
    # query che dato l'id di un appello ne restituisce i dati
    app = db_session.query(Appelli).\
            join(Prove, Appelli.idP == Prove.idP).\
            join(Esami, Prove.idE == Esami.idE).\
            filter(Appelli.idA == idAppello).first()
    
    # appello è un oggetto di tipo appello contenente i campi di appello
    return render_template('student/conferma_appello.html', appello=app)


@blueprint.route('/iscrivi_stud_appello/<int:idAppello>/', methods=['GET', 'POST'])
def iscrivi_stud_appello(idAppello):
    if session.get('session_id') is None:
        return redirect(url_for('autenticazione.login'))

    idS = session.get('session_id')
    try:
        db_session.add(StudentiPrenotati(emailS=idS, idA=idAppello, provaSuperata=False))
        db_session.commit()
        flash("iscrizione avvenuta con successo", "success")
    except Exception as e:
        print(e)
        db_session.rollback()
        flash("errore in fase di iscrizione", "danger")
    return appelli_studente()
    

#funzione per caricare la pagina contenente gli appelli a cui lo studente è iscritto
@blueprint.route('/bacheca_prenotazioni/', methods=['GET', 'POST'])
def bacheca_prenotazioni():
    if session.get('session_id') is None:
        return redirect(url_for('autenticazione.login'))

    idS = session.get('session_id')

    # query per ottenere la lista delgi appelli prenotati dallo studente idS
    iscrizioni = db_session.query(StudentiPrenotati.idA).\
                    filter(StudentiPrenotati.emailS == idS, StudentiPrenotati.dataScadenza.is_(None)).all()
    iscrizioni = [row[0] for row in iscrizioni]
    lista_appelli = db_session.query(Appelli).\
                    join(Prove, Appelli.idP == Prove.idP).\
                    join(Esami, Prove.idE == Esami.idE).\
                    filter(Appelli.idA.in_(iscrizioni)).all()

    return render_template('student/bacheca_prenotazioni.html', appelli=lista_appelli)

#funzione per visualizzare lo storico degli esami, divisi nel libretto, quindi gli esami già registrati, e negli esami che non ha ancora passato
@blueprint.route('/storico_esami/', methods=['GET', 'POST'])
def storico_esami():
    if session.get('session_id') is None:
        return redirect(url_for('autenticazione.login'))

    idS = session.get('session_id')

    invalida_prove_scadute()

    # query che trova tutti gli esami di cui lo studente idS ha tentato almeno una prova
    prove_sostenute = db_session.query(Prove.idE).\
                        join(Appelli, Prove.idP == Appelli.idP).\
                        join(StudentiPrenotati, Appelli.idA == StudentiPrenotati.idA).\
                        filter(StudentiPrenotati.emailS == idS, StudentiPrenotati.dataScadenza != None).all()
    
    prove_sostenute = [row[0] for row in prove_sostenute]

    #query che trova gli esami registrati dello studente
    esami_reg = db_session.query(EsamiRegistrati).\
                join(Esami, EsamiRegistrati.idE == Esami.idE).\
                filter(EsamiRegistrati.idS == idS).all()
    
    esami_registrati_idS = set([esame.idE for esame in esami_reg])

    #query che ritorna la lista degli esami ancora non registrati dello sudente
    lista_esami = db_session.query(Esami).\
                    filter(Esami.idE.in_(prove_sostenute), 
                           ~Esami.idE.in_(esami_registrati_idS)).all()
    
    media = calcola_media_ponderata(idS)
    #lista_esami è una lista contenente oggetti di tipo esame, quindi contenete i campi di esame come facoltà corso ed ecc
    return render_template('student/esami.html', esami=lista_esami, media=media, libretto=esami_reg)

#funzione che invalida le prove si esami non registrati che sono scadute
def invalida_prove_scadute():
    studenti_p = db_session.query(StudentiPrenotati).all()

    for row in studenti_p:
        # Se la dataScadenza è inferiore alla data corrente
        if row.dataScadenza is not None:
            if row.dataScadenza < date.today():
                # Controllo se l'esame è già registrato
                is_registered = db_session.query(exists().where(EsamiRegistrati.idE == Prove.idE 
                                                                and EsamiRegistrati.idS == row.emailS 
                                                                and Appelli.idP == Prove.idP 
                                                                and Appelli.idA == row.idA)).scalar()
                
                # se non è registrato faccio l'update
                if not is_registered:
                    
                    db_session.query(StudentiPrenotati).\
                        filter_by(idA=row.idA, emailS=row.emailS).\
                        update({StudentiPrenotati.provaSuperata: False})
    db_session.commit()

#funzione per visualizzare le prove valide di un esame 
@blueprint.route('/corsi/<string:idE>/', methods=['GET', 'POST'])
def corsi(idE):
    if session.get('session_id') is None:
        return redirect(url_for('autenticazione.login'))

    idS = session.get('session_id')
    
    #query che trova tutte le prove dell'esame idE dello studente idS
    prove = db_session.query(StudentiPrenotati).\
            join(Appelli, StudentiPrenotati.idA == Appelli.idA).\
            join(Prove, Appelli.idP == Prove.idP).\
            filter(Prove.idE == idE, StudentiPrenotati.emailS == idS, 
                   StudentiPrenotati.dataScadenza != None).all()
    
    esame = db_session.query(Esami).filter(Esami.idE == idE).first()
    
    # esame contiene i campi dell'esame e una lista prove contenete tutte le prove validE e i suoi campi
    return render_template('student/corsi.html', prove=prove, esame=esame)

def calcola_media_ponderata(idS):

    esami_registrati = db_session.query(EsamiRegistrati.voto, Esami.cfu).join(Esami, EsamiRegistrati.idE == Esami.idE).filter(EsamiRegistrati.idS == idS).all()

    somma_pesata = sum(voto * cfu for voto, cfu in esami_registrati)
    somma_cfu = sum(cfu for _, cfu in esami_registrati)
    media_ponderata = somma_pesata / somma_cfu if somma_cfu != 0 else 0
    media_ponderata = round(media_ponderata, 2)
    return media_ponderata