import jwt
from datetime import datetime, time
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import app, db, login


class TimestampMixin(object):
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)


class User(TimestampMixin, UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return f'User {self.username}'

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


class DrugCategory(TimestampMixin, db.Model):
    """
    paracetamol
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))

    def __repr__(self):
        return f'DrugCategory {self.name}'


class Drug(TimestampMixin, db.Model):
    """
    drug
    """
    id = db.Column(db.Integer, primary_key=True)
    drug_category = db.Column(db.Integer, db.ForeignKey('drug_category.id'))
    name = db.Column(db.String(64), index=True, unique=True)

    def __repr__(self):
        drug_category = DrugCategory.query.filter_by(id=self.drug_category).first()
        return f'Drug {self.name} of {drug_category} category'


class Dosage(TimestampMixin, db.Model):
    """
    dosage
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    drug_id = db.Column(db.Integer, db.ForeignKey('drug.id'))
    no_of_times = db.Column(db.Integer)
    frequency = db.Column(db.Integer)

    def __repr__(self):
        user = User.query.filter_by(id=self.user_id).first()
        drug = Drug.query.filter_by(id=self.drug_id).first()
        return f'{drug.name} has been prescribed to {user.first_name} {user.last_name}'

    def get_user(self):
        user = User.query.filter_by(id=self.user_id).first()
        return user.get_full_name()

    def get_drug(self):
        drug = Drug.query.filter_by(id=self.drug_id).first()
        return drug.name

    def get_interval(self):
        user = User.query.filter_by(id=self.user_id).first()
        drug = Drug.query.filter_by(id=self.drug_id).first()
        return f'{user.get_full_name()} take {drug.name}  {drug.no_of_times} * {drug.frequency} times a day'


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
