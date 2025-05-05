from flask_login import *

class User(UserMixin):

    def __init__(self, email, psw):
            self.email = email
            self.psw = psw

    def to_json(self):
        return {"email": self.email,
                "psw": self.psw}
    def is_authenticated(self):
        return True

    def is_active(self):
       return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.email)