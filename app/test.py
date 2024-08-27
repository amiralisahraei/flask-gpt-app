import unittest
from flask_testing import TestCase
from server import app


class FlaskTestCase(TestCase):
    def create_app(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        return app

    def test_index(self):
        """Test that the index page loads correctly."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)

    def test_login_successful(self):
        response = self.client.post(
            "/login", data={"email": "a.sahraei98@gmail.com", "password": "amir123"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual("/chat", response.location)

    def test_login_error(self):
        response = self.client.post(
            "/login", data={"email": "a@gmail.com", "password": "amir123"}
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"Error Page", response.data)

    def test_signup_successful(self):
        response = self.client.post(
            "/signup",
            data={
                "firstname": "Karen5",
                "lastname": "Vanry5",
                "email": "karen5@gmail.com",
                "password": "123",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual("/login", response.location)

    def test_signup_error(self):
        response = self.client.post(
            "/signup",
            data={
                "firstname": "amir",
                "lastname": "sh",
                "email": "a.sahraei98@gmail.com",
                "password": "123",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Error Page", response.data)

    def test_file_upload(self):
        with self.client.session_transaction() as sess:
            sess["user_email"] = "a.sahraei98@gmail.com"
        with open("Amirali_Sahraei_CV_OLD.pdf", "rb") as f:
            data = {}
            data["file"] = f
            response = self.client.post(
                "/fileUpload", data=data, content_type="multipart/form-data"
            )
            self.assertEqual(response.status_code, 302)
            self.assertEqual("/chat", response.location)

    def test_chat_get_logged_in(self):
        """Test GET request to /chat."""
        with self.client.session_transaction() as sess:
            sess["user_email"] = "a.sahraei98@gmail.com"
        response = self.client.get("/chat")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Welcome", response.data)

    def test_chat_get_not_logged_in(self):
        """Test GET request to /chat."""
        with self.client.session_transaction() as sess:
            sess.pop("user_email", None)
        response = self.client.get("/chat")
        self.assertEqual(response.status_code, 302)
        self.assertEqual("/login", response.location)

    def test_chat_post_logged_in(self):
        """Test POST request to /chat."""
        with self.client.session_transaction() as sess:
            sess["user_email"] = "a.sahraei98@gmail.com"
        response = self.client.post("/chat", data={"text": "Hello"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Hello", response.data)

    def test_chat_post_not_logged_in(self):
        """Test POST request to /chat."""
        with self.client.session_transaction() as sess:
            sess.pop("user_email", None)
        response = self.client.post("/chat", data={"text": "Hello"})
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)


if __name__ == "__main__":
    unittest.main()
