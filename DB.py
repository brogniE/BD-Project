import ORM
from popolaDB import DatabasePopulator

# Funzione che crea il database droppeando le tabelle e ricreandole
def set_DB():
    db = get_DB()
    ORM.Base.metadata.drop_all(db)
    ORM.Base.metadata.create_all(db)

# Funzione per inizializzare il database e aggiungere l'utente admin
def lancia_inizializzazione():
    set_DB()
    popolatore = DatabasePopulator()
    popolatore.create_admin(1)

# Funzione per ottenere la sessione del database
def get_session():
    return ORM.db_session

#Funzione per ottenere il motore del database
def get_DB():
    return ORM.engine
