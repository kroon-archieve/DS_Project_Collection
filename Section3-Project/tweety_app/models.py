from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from embedding_as_service_client import EmbeddingClient

db = SQLAlchemy()
migrate = Migrate()

en = EmbeddingClient(host='54.180.124.154', port=8989)

# db 테이블 생성
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Integer, nullable=False)
    full_name = db.Column(db.String, nullable=False, unique=True)
    followers = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String, nullable=False)
    # tweet_id = db.Column(db.Integer, db.ForeignKey('Tweets.id'))
    # tweet = db.relationship('Tweets', backref='users', lazy=True)
    
    def __repr__(self):
        return f"<User{self.id} {self.username}>"

class Tweets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, nullable=False)
    embedding = db.Column(db.PickleType)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'))
    users = db.relationship('Users', backref='tweets', lazy=True)
    
    def __repr__(self):
        return f"<Tweets {self.id} {self.text}>"


def parse_records(db_records):
    parsed_list = []
    for record in db_records:
        parsed_record = record.__dict__
        print(parsed_record)
        del parsed_record["_sa_instance_state"]
        parsed_list.append(parsed_record)

    return parsed_list

def get_all_data():
    return Users.query.all()
