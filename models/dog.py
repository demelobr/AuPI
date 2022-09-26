from datetime import datetime
from email.policy import default
from models.shelter import ShelterModel
from sql_alchemy import db

class DogModel(db.Model):
    __tablename__ = 'dogs'

    dog_id = db.Column(db.Integer, primary_key=True)
    dog_name = db.Column(db.String(20), nullable=False)
    dog_shelter = db.Column(db.String(40), db.ForeignKey('shelters.shelter_name'), nullable=False)
    dog_birth_date = db.Column(db.String(10), nullable=False)
    dog_gender = db.Column(db.String(1), nullable=False)
    dog_country = db.Column(db.String(20))
    dog_state = db.Column(db.String(20))
    dog_city = db.Column(db.String(20))
    dog_verified = db.Column(db.Boolean, default=False)

    def __init__(self, dog_name, dog_shelter, dog_birth_date, dog_gender):
        self.dog_name = dog_name
        self.dog_shelter = dog_shelter
        self.dog_birth_date = dog_birth_date
        self.dog_gender = dog_gender
    
    def json(self):
        return{
            'dog_id': self.dog_id,
            'dog_name': self.dog_name,
            'dog_shelter': self.dog_shelter,
            'dog_birth_date': self.dog_birth_date,
            'dog_gender': self.dog_gender,
            'dog_country': self.dog_country,
            'dog_state': self.dog_state,
            'dog_city': self.dog_city,
            'dog_verified': self.dog_verified
        }
    
    @classmethod
    def find_dog_by_id(cls, dog_id):
        dog = cls.query.filter_by(dog_id=dog_id).first()
        if dog:
            return dog
        return False  

    def is_date(self):
        format_date = "%d/%m/%Y"
        try:
            return bool(datetime.strptime(self.dog_birth_date, format_date))
        except ValueError:
            return False

    def verified_dog(self):
        self.dog_verified = True

        try:
            self.save_dog()
        except:
            return {'message': "An internal error ocurred trying to save dog location."}, 500

    def set_dog_location(self):
        shelter = ShelterModel.find_shelter_by_name(self.dog_shelter)

        if shelter:
            self.dog_country = shelter.shelter_country
            self.dog_state = shelter.shelter_state
            self.dog_city = shelter.shelter_city

            try:
                self.save_dog()
            except:
                return {'message': "An internal error ocurred trying to save dog location."}, 500
    
    def save_dog(self):
        db.session.add(self)
        db.session.commit()

    def update_dog(self, dog_name, dog_shelter, dog_birth_date, dog_gender):
        self.dog_name = dog_name
        self.dog_shelter = dog_shelter
        self.dog_birth_date = dog_birth_date
        self.dog_gender = dog_gender
    
    def delete_dog(self):
        db.session.delete(self)
        db.session.commit()