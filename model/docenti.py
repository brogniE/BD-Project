from datetime import *

from faker import Faker
from flask import *
from flask_sqlalchemy import *
from sqlalchemy import *
from sqlalchemy.orm import aliased

from DB import *
from ORM import *
from faker import Faker
from datetime import *
from sqlalchemy.orm import aliased
from model.User import *

db_session = get_session()

blueprint = Blueprint('docenti', __name__, url_prefix='/docenti')

#funzione per caricare la pagina con i dati anagrafici del docente
@blueprint.route('/anagrafica_docente/', methods=['GET', 'POST'])
def anagrafica_docente():
    # controlla se è stato effettuato il login
    if session.get('session_id') is None:
        return redirect(url_for('autenticazione.login'))

    idD = session.get('session_id')
    # query che dato emailD di un docente ne trova i dati anagrafici
    docente = db_session.query(Docenti).\
                join(Utenti, Docenti.emailD == Utenti.email).\
                filter(Docenti.emailD == idD).first()

    return render_template('professor/anagrafica.html', docente=docente)

#funzione per il caricamento della pagina per l'inserimento di un nuovo esame
@blueprint.route('/new_esame/', methods=['GET', 'POST'])
def new_esame():
    if session.get('session_id') is None:
        return redirect(url_for('autenticazione.login'))

    return render_template('professor/new_esame.html')

@blueprint.route('/conferma_esame/', methods=['GET', 'POST'])
def conferma_esame():
    if session.get('session_id') is None:
        return redirect(url_for('autenticazione.login'))

    idD = session.get('session_id')
    # query per l'inserimento di un nuovo esame al DB
    input_corso = request.form['corsoid']
    input_facolta = request.form['facoltaid']
    input_cfu = request.form['cfuid']
    input_idE = 'CT' + str(Faker().unique.random_number(digits=4))
    input_anno = request.form['annoid']

    try:
        db_session.add(Esami(idE=input_idE, 
                             corso=input_corso, 
                             facolta=input_facolta, 
                             cfu=input_cfu, 
                             anno=input_anno))
        db_session.add(GestioneEsami(idE=input_idE, idD=idD))
        db_session.commit()
        flash("Esame inserito con successo", "success")
    except Exception as e:
        print(e)
        db_session.rollback()
        flash("Errore in fase di creazione dell'esame", "danger")
    return new_esame()

#funzione per il caricamento della pagina per l'inserimento di un nuova prova
@blueprint.route('/new_prova/', methods=['GET', 'POST'])
def new_prova():
    if session.get('session_id') is None:
        return redirect(url_for('autenticazione.login'))

    idD = session.get('session_id')
    # query per ottenere la lista degli degli esami del professore
    esami = db_session.query(GestioneEsami).filter(GestioneEsami.idD == idD).all()
    esami = db_session.query(Esami).all()
    return render_template('professor/new_prova.html', esami=esami)

@blueprint.route('/conferma_prova/', methods=['GET', 'POST'])
def conferma_prova():
    if session.get('session_id') is None:
        return redirect(url_for('autenticazione.login'))

    idD = session.get('session_id')
    # query per l'inserimento di una nuova prova al DB
    input_idE = request.form['esameid']
    input_tipo = request.form['tipologiaid']
    input_ric = request.form['ricadutaid']
    input_peso = request.form['pesoid']
    input_idP = 'P' + str(Faker().unique.random_number(digits=4))

    try:
        db_session.add(Prove(idP=input_idP,
                             tipo=input_tipo,
                             ricaduta=input_ric,
                             peso=input_peso if input_peso else None,
                             idE=input_idE, idD=idD))

        docente_reg = db_session.query(GestioneEsami).filter(GestioneEsami.idD == idD,
                                                             GestioneEsami.idE == input_idE).first()
        if docente_reg is None:
            db_session.add(GestioneEsami(idE=input_idE, idD=idD))
        db_session.commit()
        flash("Prova aggiunta con successo", "success")
    except Exception as e:
        print(e)
        db_session.rollback()
        flash("Errore nell'inserimento della prova", "danger")
    return new_prova()

#funzione per il caricamento della pagina per l'inserimento di un nuovo appello al calendario
@blueprint.route('/new_appello/', methods=['GET', 'POST'])
def new_appello():
    if session.get('session_id') is None:
        return redirect(url_for('autenticazione.login'))

    idD = session.get('session_id')
    # query per cercare tutte le prove del professore idD
    prove = db_session.query(Prove).join(Esami, Esami.idE == Prove.idE).filter(Prove.idD == idD).all()

    return render_template('professor/new_appello.html', prove=prove)

#funzione che inserisce l'appello e controlla che non sia già presente
@blueprint.route('/conferma_appello/', methods=['GET', 'POST'])
def conferma_appello():
    if session.get('session_id') is None:
        return redirect(url_for('autenticazione.login'))

    idD = session.get('session_id')
    input_idP = request.form['provaid']
    input_data = request.form['dateStandard']

    result = db_session.query(Appelli).filter(Appelli.data == input_data, Appelli.idP == input_idP).first()

    if result is None:
        try:
            db_session.add(Appelli(idP=input_idP, data=input_data))
            db_session.commit()
            flash("Appello aggiunto con successo", "success")
        except Exception as e:
            print(e)
            db_session.rollback()
            flash("errore crazione dell'appello", "danger")
    else:
        flash("errore crazione dell'appello", "danger")

    return new_appello()

#funzione per caricare la pagina contenete tutti gli esami di cui il professore gestisce almeno una prova
@blueprint.route('/esiti_esami/', methods=['GET', 'POST'])
def esiti_esami():
    if session.get('session_id') is None:
        return redirect(url_for('autenticazione.login'))

    idD = session.get('session_id')

    invalida_prove_scadute()

    # query per ottenere tutti gli esami a cui partecipa il docente
    esami = db_session.query(Esami).join(GestioneEsami, GestioneEsami.idE == Esami.idE).filter(
        GestioneEsami.idD == idD).all()
    return render_template('professor/esiti_esami.html', esami=esami)

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

#funzione per caricare la pagina contenete le prove dell'esame e la lista degli studenti il cui voto può essere registrato
@blueprint.route('/esiti_prove/<string:idE>/', methods=['GET', 'POST'])
def esiti_prove(idE):
    if session.get('session_id') is None:
        return redirect(url_for('autenticazione.login'))

    idD = session.get('session_id')

    # query per ottenere tutti i dati dell'esame
    esame = db_session.query(Esami).filter(Esami.idE == idE).first()

    # query per ottenere tutte le prove con cui il professore idD è associato appartenenti all'esame idE
    prove = db_session.query(Prove).\
            join(Esami, Esami.idE == Prove.idE).\
            filter(Prove.idD == idD, Prove.idE == idE).all()

    # query per ottenere tutti gli studenti il cui voto dell'esame idE può essere registrato
    studenti = studenti_registrabili(idE)

    return render_template('professor/esiti_prove.html', prove=prove, esame=esame, studenti=studenti)


def studenti_registrabili(idE):
    # Query per ottenere tutti gli studenti che hanno prenotato e superato tutte le prove dell'esame idE
    studenti_prenotati_query = db_session.query(StudentiPrenotati.emailS)\
        .join(Appelli, Appelli.idA == StudentiPrenotati.idA)\
        .join(Prove, Prove.idP == Appelli.idP)\
        .filter(Prove.idE == idE, StudentiPrenotati.provaSuperata == True)\
        .group_by(StudentiPrenotati.emailS)\
        .having(func.count(Prove.idP) == db_session.query(Prove).filter(Prove.idE == idE).count())
    
    # Query per ottenere tutti gli studenti che non sono ancora inseriti in EsamiRegistrati per l'esame idE
    studenti_non_registrati_query = db_session.query(Studenti.emailS)\
        .outerjoin(EsamiRegistrati, and_(EsamiRegistrati.idS == Studenti.emailS, EsamiRegistrati.idE == idE))\
        .filter(EsamiRegistrati.idE.is_(None))
    
    # Intersezione delle due query per ottenere gli studenti che hanno prenotato 
    # e superato tutte le prove ma non hanno ancora l'esame registrato
    studenti = db_session.query(Studenti)\
        .filter(Studenti.emailS.in_(studenti_prenotati_query), 
                Studenti.emailS.in_(studenti_non_registrati_query)).all()
    
    return studenti

#funzione per la visualizzazione degli appelli di una prova
@blueprint.route('/esiti_appelli/<string:idP>/', methods=['GET', 'POST'])
def esiti_appelli(idP):
    if session.get('session_id') is None:
        return redirect(url_for('autenticazione.login'))

    idD = session.get('session_id')
    # query per ottenere tutti i dati della prova di idP e la lista dello storico di tutti gli appelli per questa prova
    prova = db_session.query(Prove).join(Esami, Esami.idE == Prove.idE).filter(Prove.idP == idP).first()
    lista_app = db_session.query(Appelli).filter(Appelli.idP == idP).all()
    return render_template('professor/esiti_appelli.html', prova=prova, appelli=lista_app)

#funzione per la visualizzazione degli studenti iscritti ad un appello con il relativo voto se presente
@blueprint.route('/esiti_appello/<int:idA>/', methods=['GET', 'POST'])
def esiti_appello(idA):
    if session.get('session_id') is None:
        return redirect(url_for('autenticazione.login'))

    idD = session.get('session_id')
    # query per ottenere tutti i dati dell'appello (facolta, corso, ricaduta, ecc) e la lista degli studenti che hanno partecipato all'appello
    appello = get_appello(idA)
    studenti_app = get_studenti_appello(idA)
    # se non sono già presenti i voti degli studenti
    for studente_app in studenti_app:
        if studente_app.dataScadenza is None:
            return render_template('professor/esiti_appello_inserimento_voti.html', appello=appello, studenti_app=studenti_app)

        # se sono già presenti i voti degli studenti
    return render_template('professor/esiti_appello.html', appello=appello, studenti_app=studenti_app)

#funzione per la visualizzazione e l'inserimento dei voti degli studenti iscritti ad un appello se il loro voto non è ancora stato salvato 
@blueprint.route('/inserimento_voti_appello/<int:idA>/', methods=['GET', 'POST'])
def inserimento_voti_appello(idA):
    if session.get('session_id') is None:
        return redirect(url_for('autenticazione.login'))

    idD = session.get('session_id')
    # query per inserire i voti dell'appello idA
    studenti_app = get_studenti_appello(idA)
    appello = get_appello(idA)
    ricaduta = appello.prova.ricaduta
    input_data = request.form['dataid']
    try:
        for studente_app in studenti_app:
            matricola = studente_app.studente.matricola
            if ricaduta == "Voto":
                voto = int(request.form.get(f'{matricola}_voto'))
                lode = bool(request.form.get(f'{matricola}_lode'))
                db_session.query(StudentiPrenotati).filter_by(idA=idA, emailS=studente_app.emailS). \
                    update({StudentiPrenotati.provaSuperata: True if voto > 17 else False,
                            StudentiPrenotati.dataScadenza: input_data,
                            StudentiPrenotati.voto: voto,
                            StudentiPrenotati.lode: lode})
            elif ricaduta == "Idoneità":
                idoneo = bool(request.form.get(f'{matricola}_idoneita'))
                db_session.query(StudentiPrenotati).filter_by(idA=idA, emailS=studente_app.emailS). \
                    update({StudentiPrenotati.provaSuperata: idoneo,
                            StudentiPrenotati.dataScadenza: input_data})
            elif ricaduta == "Bonus":
                bonus = int(request.form.get(f'{matricola}_bonus'))
                db_session.query(StudentiPrenotati).filter_by(idA=idA, emailS=studente_app.emailS). \
                    update({StudentiPrenotati.provaSuperata: True if bonus > 0 else False,
                            StudentiPrenotati.dataScadenza: input_data,
                            StudentiPrenotati.bonus: bonus})
            invalida_prova(studente_app.emailS, idA)
            db_session.commit()
        flash("inserimento dei voti avvenuto con successo", "success")
    except Exception as e:
        print(e)
        db_session.rollback()
        flash("errore in fase di inserimento della valutazione", "danger")
    return esiti_prove(appello.prova.idE)

#funzione che invalida la prova precedente svolta dallo studente
def invalida_prova(idS, idA):
    prova_appello = db_session.query(Appelli.idP).filter(Appelli.idA == idA).first()
    result = db_session.query(StudentiPrenotati).\
                join(Appelli, StudentiPrenotati.idA == Appelli.idA).\
                filter(StudentiPrenotati.emailS == idS, 
                       Appelli.idP == prova_appello.idP, 
                       StudentiPrenotati.idA != idA).first()
    
    if result is not None:
        db_session.query(StudentiPrenotati).filter_by(idA=result.idA, emailS=idS).\
                update({StudentiPrenotati.provaSuperata: False})

#funzione che ritorna la lista degli studenti iscritti all'appello
def get_studenti_appello(idA):
    studenti_app = db_session.query(StudentiPrenotati).\
                    join(Studenti, StudentiPrenotati.emailS == Studenti.emailS).\
                    filter(StudentiPrenotati.idA == idA).all()
    return studenti_app

#funzione che ritorna i dati della prova e dell'esame di un appello
def get_appello(idA):
    appello = db_session.query(Appelli).join(Prove, Appelli.idP == Prove.idP).\
                join(Esami,Esami.idE == Prove.idE).filter(Appelli.idA == idA).first()
    return appello

#funzione per la pagina di registrazione del voto dell'esame allo studente
@blueprint.route('/<string:idE>/<string:idS>/registra_voto', methods=['GET', 'POST'])
def registra_voto(idE, idS):
    if session.get('session_id') is None:
        return redirect(url_for('autenticazione.login'))

    idD = session.get('session_id')
    # query per avere i dati dello studente
    studente = db_session.query(Studenti).join(Utenti, Studenti.emailS == Utenti.email).filter(Studenti.emailS == idS).first()

    # query per avere i risultati delle prove valide dello studente idS dell'esame idE
    prove = db_session.query(StudentiPrenotati).join(Appelli, StudentiPrenotati.idA == Appelli.idA). \
        join(Prove, Appelli.idP == Prove.idP). \
        filter(Prove.idE == idE,
               StudentiPrenotati.emailS == idS,
               StudentiPrenotati.provaSuperata).all()

    # calcolo del possibile voto in base alla media
    voto = calcola_voto(prove)
    return render_template('professor/registra_voto.html', studente=studente, prove=prove, voto=voto,
                           idE=idE)

#funzione per il calcolo del possibile voto (modificabile dal docente)
def calcola_voto(prove):
    voto_totale = 0
    bonus_totale = 0
    tot_prove = 0
    tot_prove_ido = 0
    for p in prove:
        if p.provaSuperata:
            tot_prove += 1
            if p.appello.prova.ricaduta == 'Voto':
                voto_totale += (p.voto * p.appello.prova.peso) / 100
            elif p.appello.prova.ricaduta == 'Bonus':
                bonus_totale += p.bonus
            elif p.appello.prova.ricaduta == 'Idoneità':
                tot_prove_ido += 1

    #se tutte le prove sono prove di idoneita' non viene considerato il voto
    if tot_prove == tot_prove_ido:
        voto_finale = -1
    else:
        voto_finale = round(voto_totale + bonus_totale)
    return voto_finale

#funzione per la registrazione di un voto 
@blueprint.route('/<string:idE>/<string:idS>/<int:flag>/conferma_registrazione_voto', methods=['GET', 'POST'])
def conferma_registrazione_voto(idE, idS, flag):
    if session.get('session_id') is None:
        return redirect(url_for('autenticazione.login'))

    idD = session.get('session_id')
    # query per la registrazione del voto dell'esame idE dello sudente idS
    try:
        #riferito alla funzione precedente, se tutte le prove sono di idoneita' non viene considerato il voto
        if flag == -1:
            idoneo = bool(request.form["idoneo"])
            db_session.add(EsamiRegistrati(idE=idE, idS=idS, idoneo=idoneo))
        else:
            voto = int(request.form["voto"])
            lode = False

            if voto > 30:
                voto = 30
                lode = True
            db_session.add(EsamiRegistrati(idE=idE, idS=idS, voto=voto, lode=lode))

        db_session.commit()
        flash("registrazione del voto avvenuta con successo", "success")
    except Exception as e:
        print(e)
        db_session.rollback()
        flash("errore in fase di registrazione del voto", "danger")
    return esiti_prove(idE)