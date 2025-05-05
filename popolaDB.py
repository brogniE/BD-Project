from werkzeug.security import *
from ORM import *

class DatabasePopulator:
    # Funzione che crea un Utente Admin per mettere l'accesso alla piattaforma
    # per successivamente creare gli altri utenti Studenti e Docenti
    def create_admin(self, num_users):
        for _ in range(num_users):
            user = Utenti(
                email='admin@unive.it',
                password=generate_password_hash("test1234"),
                nome='Admin',
                cognome='UNIVE',
                telefono='0000000000',
                dataNascita='2023-09-18',
                isAdmin=True
            )
            db_session.add(user)
        db_session.commit()
        db_session.close()