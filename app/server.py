import os
from datetime import timedelta
from flask import Flask, request, render_template, redirect, session
from gpt_server import clear_chat_history
from dotenv import load_dotenv
from models import db
from controller import login_user, signup_user, file_upload_user, chat_user


load_dotenv()

app = Flask(__name__)
# Needed for flashing message
app.secret_key = "your_secret_key"

# Set session lifetime to 30 minutes
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


# Create tables
with app.app_context():
    db.create_all()

# make a directory to upload Pdf into it
upload_dir = os.getenv("UPLOAD_DIR")
main_dir = os.getenv("MAIN_DIR")
if not os.path.exists(f"./{main_dir}/{upload_dir}"):
    os.chdir(f"./{main_dir}")
    os.mkdir(upload_dir)

questions_array = []
responses_array = []


@app.route("/")
def main_page():
    user_email = session.get("user_email")
    if not user_email:
        return redirect("/login")
    return redirect("/chat")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        return login_user(request)
    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user_email", None)
    return redirect("/login")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        return signup_user(request)
    return render_template("signup.html")


@app.route("/deleteChat", methods=["POST"])
def delete_Chat():
    user_email = session.get("user_email")
    clear_chat_history(user_email)
    return redirect("/chat")


@app.route("/fileUpload", methods=["POST"])
def file_Upload():
    return file_upload_user(request, main_dir, upload_dir)


@app.route("/chat", methods=["GET", "POST"])
def chat():
    file_exist = False
    if os.path.exists(f"./{main_dir}/{upload_dir}/user_info.pdf"):  
        file_exist = True
    return chat_user(request, file_exist)


if __name__ == "__main__":
    app.run(debug=True, port=8080)
