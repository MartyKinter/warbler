from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Message, Follows, Likes



from app import app

with app.app_context():
    db.create_all()

class UserModelTestCase(TestCase):
    """Test views for messages"""
    def setUp(self):
        """Create test client with sample data"""
        with app.app_context():
            db.drop_all()
            db.create_all()

            self.uid = 94566
            u = User.signup("testing", "testing@test.com", "password", None)
            u.id = self.uid
            db.session.commit()

            self.u = User.query.get(self.uid)
            self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        with app.app_context():
            db.session.rollback()
        return res

    def test_message_model(self):
        """Test if basic model works"""
        msg = Message(
            text = "test message",
            user_id = self.uid 
        )
        with app.app_context():
            db.session.add(msg)
            db.session.commit()

            self.u = User.query.get(self.uid)

            self.assertEqual(len(self.u.messages), 1)
            self.assertEqual(self.u.messages[0].text, "test message")

    def test_message_likes(self):
        msg1 = Message(
            text="test message",
            user_id=self.uid
        )

        msg2 = Message(
            text="second test message",
            user_id=self.uid
        )

        with app.app_context():

            u = User.signup("anothertest", "test2@test.com", "password", None)
            uid = 888
            u.id = uid
            
            db.session.add_all([msg1, msg2, u])
            db.session.commit()

            u.likes.append(msg1)

            db.session.commit()

            likes = Likes.query.filter(Likes.user_id == uid).all()
            self.assertEqual(len(likes), 1)
            self.assertEqual(likes[0].message_id, msg1.id)