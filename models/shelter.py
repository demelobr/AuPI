from email.policy import default
from sql_alchemy import db

class ShelterModel(db.Model):
    __tablename__ = 'shelters'

    shelter_id = db.Column(db.Integer, primary_key=True)
    shelter_name = db.Column(db.String(40), nullable=False, unique=True)
    shelter_accountable = db.Column(db.String(40), nullable=False)
    shelter_email = db.Column(db.String(80), nullable=False, unique=True)
    shelter_phone_number = db.Column(db.String(20), nullable=False)
    shelter_address = db.Column(db.String(100), nullable=False)
    shelter_country = db.Column(db.String(20), nullable=False)
    shelter_state = db.Column(db.String(20), nullable=False)
    shelter_city = db.Column(db.String(20), nullable=False)
    shelter_verified = db.Column(db.Boolean, default=False)
    shelter_dogs = db.relationship('DogModel')

    def __init__(self, shelter_name, shelter_accountable, shelter_email, shelter_phone_number, shelter_address, shelter_country, shelter_state, shelter_city):
        self.shelter_name = shelter_name
        self.shelter_accountable = shelter_accountable
        self.shelter_email = shelter_email
        self.shelter_phone_number = shelter_phone_number
        self.shelter_address = shelter_address
        self.shelter_country = shelter_country
        self.shelter_state = shelter_state
        self.shelter_city = shelter_city
    
    def json(self):
        return{
            'shelter_name': self.shelter_name,
            'shelter_accountable': self.shelter_accountable,
            'shelter_email': self.shelter_email,
            'shelter_phone_number': self.shelter_phone_number,
            'shelter_address': self.shelter_address,
            'shelter_country': self.shelter_country,
            'shelter_state': self.shelter_state,
            'shelter_city': self.shelter_city,
            'shelter_verified': self.shelter_verified,
            'shelter_dogs': [dog.json() for dog in self.shelter_dogs]
        }
    
    @classmethod
    def find_shelter_by_name(cls, shelter_name):
        shelter = cls.query.filter_by(shelter_name=shelter_name).first()
        if shelter:
            return shelter
        return False

    def verified_shelter(self):
        self.shelter_verified = True

        try:
            self.save_shelter()
        except:
            return {'message': "An internal error ocurred trying to save shelter location."}, 500

    def save_shelter(self):
        db.session.add(self)
        db.session.commit()
    
    def update_shelter(self, shelter_name, shelter_accountable, shelter_email, shelter_phone_number, shelter_address, shelter_country, shelter_state, shelter_city):
        self.shelter_name = shelter_name
        self.shelter_accountable = shelter_accountable
        self.shelter_email = shelter_email
        self.shelter_phone_number = shelter_phone_number
        self.shelter_address = shelter_address
        self.shelter_country = shelter_country
        self.shelter_state = shelter_state
        self.shelter_city = shelter_city

    def delete_shelter(self):
        [dog.delete_dog() for dog in self.shelter_dogs]
        db.session.delete(self)
        db.session.commit()