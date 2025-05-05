from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, create_engine, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

engine = create_engine('postgresql+psycopg2://postgres:Password01!@localhost:5432/DB23_Temp', echo=False)
Session = sessionmaker(bind=engine)
db_session = Session()

Base = declarative_base()

class Utenti(Base):
    __tablename__ = 'utenti'
    email = Column(String, primary_key=True)
    password = Column(String, nullable=False)
    nome = Column(String, nullable=False)
    cognome = Column(String, nullable=False)
    telefono = Column(String, nullable=False)
    dataNascita = Column(Date, nullable=False)
    isAdmin = Column(Boolean, nullable=False)

class Docenti(Base):
    __tablename__ = 'docenti'
    emailD = Column(String, ForeignKey('utenti.email'), primary_key=True)
    dipartimento = Column(String, nullable=False)

    utente = relationship('Utenti', foreign_keys=[emailD])

class Studenti(Base):
    __tablename__ = 'studenti'
    emailS = Column(String, ForeignKey('utenti.email'), primary_key=True)
    matricola = Column(String, nullable=False)
    facolta = Column(String, nullable=False)
    annoIscrizione = Column(Integer, nullable=False)

    utente = relationship('Utenti', foreign_keys=[emailS])

class Esami(Base):
    __tablename__ = 'esami'
    idE = Column(String, primary_key=True)
    corso = Column(String, nullable=False)
    facolta = Column(String, nullable=False)
    cfu = Column(Integer, CheckConstraint("cfu > 0"), nullable=False)
    anno = Column(Integer, nullable=False)

class GestioneEsami(Base):
    __tablename__ = 'gestione_esami'
    idE = Column(String, ForeignKey('esami.idE'), primary_key=True)
    idD = Column(String, ForeignKey('docenti.emailD'), primary_key=True)

class Prove(Base):
    __tablename__ = 'prove'
    idP = Column(String, primary_key=True)
    tipo = Column(String, nullable=False)
    ricaduta = Column(String, nullable=False)
    peso = Column(Integer)
    idE = Column(String, ForeignKey('esami.idE'))
    idD = Column(String, ForeignKey('docenti.emailD'))

    esame = relationship('Esami', foreign_keys=[idE])
    docente = relationship('Docenti', foreign_keys=[idD])

    __table_args__ = (
        CheckConstraint("ricaduta <> 'Voto' OR peso IS NOT NULL"),
    )


class EsamiRegistrati(Base):
    __tablename__ = 'esami_registrati'
    idE = Column(String, ForeignKey('esami.idE'), primary_key=True)
    idS = Column(String, ForeignKey('studenti.emailS'), primary_key=True)
    voto = Column(Integer)
    idoneo = Column(Boolean)
    lode = Column(Boolean)

    studente = relationship('Studenti', foreign_keys=[idS])
    esame = relationship('Esami', foreign_keys=[idE])
    
    __table_args__ = (
        CheckConstraint("NOT lode OR voto = 30"),
    )

class Appelli(Base):
    __tablename__ = 'appelli'
    idA = Column(Integer, primary_key=True)
    idP = Column(String, ForeignKey('prove.idP'), nullable=False)
    data = Column(Date, nullable=False)

    prova = relationship('Prove', foreign_keys=[idP])

class StudentiPrenotati(Base):
    __tablename__ = 'studenti_prenotati'
    idA = Column(Integer,ForeignKey('appelli.idA'), primary_key=True)
    emailS = Column(String, ForeignKey('studenti.emailS'), primary_key=True)
    provaSuperata = Column(Boolean, nullable=False)
    dataScadenza = Column(Date)
    voto = Column(Integer)
    bonus = Column(Integer)
    lode = Column(Boolean)

    studente = relationship('Studenti', foreign_keys=[emailS])
    appello = relationship('Appelli', foreign_keys=[idA])

    __table_args__ = (
        CheckConstraint("NOT lode OR voto = 30"),
    )


Base.metadata.create_all(bind=engine)
