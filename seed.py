"""Seed database with sample data from CSV Files."""

from csv import DictReader
from app import db
from models import User, Message, Follows
from app import app

with app.app_context():
    db.drop_all()
    db.create_all()

with open('generator/users.csv') as users:
    with app.app_context():
        db.session.bulk_insert_mappings(User, DictReader(users))

with open('generator/messages.csv') as messages:
    with app.app_context():
        db.session.bulk_insert_mappings(Message, DictReader(messages))

with open('generator/follows.csv') as follows:
    with app.app_context():
        db.session.bulk_insert_mappings(Follows, DictReader(follows))

with app.app_context():
    db.session.commit()
