import unittest
from flask_testing import TestCase
from server import app, gpt_server


class FlaskTestCase(TestCase):
    def create_app(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        return app

    def test_index(self):
        """Test that the index page loads correctly."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Welcome to ChatGPT", response.data)

    def test_chat_get(self):
        """Test GET request to /chat."""
        response = self.client.get("/chat")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Welcome to ChatGPT", response.data)

    def test_chat_post(self):
        """Test POST request to /chat."""
        response = self.client.post("/chat", data={"text": "Hello"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Hello", response.data)
        self.assertIn(b"Hello", response.data)

    def test_gpt_server(self):
        """Test the GPT server response."""
        chat_history = [("Hello", "Hi there!")]
        response = gpt_server("How are you?", chat_history)
        self.assertIsInstance(response, str)
        self.assertNotEqual(response, "")


if __name__ == "__main__":
    unittest.main()
