import os
from unittest import TestCase

from models import db, connect_db, Message, User

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

with app.app_context():
    db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        with app.app_context():

            db.drop_all()
            db.create_all()

            self.client = app.test_client()

            self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

            self.testuser_id = 8989
            self.testuser.id = self.testuser_id

            db.session.add(self.testuser)
            db.session.commit()

            self.u = User(
                id=111,
                email="test2@test.com",
                username="testuser2",
                password="HASHED_PASSWORD"
            )
            db.session.add(self.u)
            db.session.commit()

            self.m = Message(
                id=1234,
                text="a test message",
                user_id=self.testuser_id
            )

            db.session.add(self.m)
            db.session.commit()




    def test_add_message(self):
        with app.app_context():
            # create a user and log them in
            u = User(
                id=11,
                email="test5@test.com",
                username="testuser5",
                password="HASHED_PASSWORD"
            )
            db.session.add(u)
            db.session.commit()

            with self.client as c:
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = u.id

                # send a post request to add a message
                resp = c.post("/messages/new", data={"text": "Hello world"})

                # Make sure it redirects
                self.assertEqual(resp.status_code, 302)

                # check that the message was added to the database
                msg = Message.query.filter_by(text="Hello world").first()
                self.assertIsNotNone(msg)
                self.assertEqual(msg.text, "Hello world")



    def test_add_no_session(self):
        with self.client as c:
            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_add_invalid_user(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 99222224

            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))
    
    def test_message_show(self):
            with self.client as c:
                with c.session_transaction() as sess:
                    db.session.add(self.u)
                    user = User.query.get(self.u.id)
                    sess[CURR_USER_KEY] = user.id

                with app.app_context():
                    m = Message.query.get(1234)

                    resp = c.get(f'/messages/{m.id}')

                    self.assertEqual(resp.status_code, 200)
                    self.assertIn(m.text, str(resp.data))

    def test_invalid_message_show(self):
            with self.client as c:
                with c.session_transaction() as sess:
                    db.session.add(self.u)
                    sess[CURR_USER_KEY] = self.u.id
            
                resp = c.get('/messages/99999999')

                self.assertEqual(resp.status_code, 404)

    def test_message_delete(self):
        with app.app_context():
            m = Message(
                id=2345,
                text="a test message",
                user_id=11111
            )
            u = User(
                id=11111,
                email="test3@test.com",
                username="testuser3",
                password="HASHED_PASSWORD"
            )

            db.session.add(u)
            db.session.commit()

            db.session.add(m)
            db.session.commit()

            with self.client as c:
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = u.id

                resp = c.post("/messages/2345/delete", follow_redirects=True)
                self.assertEqual(resp.status_code, 200)

                m = Message.query.get(2345)
                self.assertIsNone(m)

    def test_unauthorized_message_delete(self):
        with app.app_context():
        # A second user that will try to delete the message
            u = User.signup(username="unauthorized-user",
                        email="testtest@test.com",
                        password="password",
                        image_url=None)
            u.id = 76543

        #Message is owned by testuser
            m = Message(
                id=12345,
                text="a test message",
                user_id=self.testuser_id
            )
        

            db.session.add_all([u, m])
            db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 76543

            resp = c.post("/messages/1234/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

            m = Message.query.get(12345)
            self.assertIsNotNone(m)

    def test_message_delete_no_authentication(self):

        m = Message(
            id=234,
            text="a test message",
            user_id=self.testuser_id
        )

        with app.app_context():
            db.session.add(m)
            db.session.commit()

            with self.client as c:
                resp = c.post("/messages/234/delete", follow_redirects=True)
                self.assertEqual(resp.status_code, 200)
                self.assertIn("Access unauthorized", str(resp.data))

                m = Message.query.get(234)
                self.assertIsNotNone(m)
