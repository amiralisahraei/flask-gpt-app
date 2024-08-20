import os
from flask import render_template, redirect, flash, session
from gpt_server import gpt_server
from models import Messages, Users, db


def extract_data(user_email):

    user = Users.query.filter_by(email=user_email).first()
    past_messages = Messages.query.filter_by(user_id=user.id).all()

    combinded_message = []
    for i in range(0, len(past_messages), 2):
        combinded_message.append(
            (past_messages[i].message, past_messages[i + 1].message)
        )
    return combinded_message


def login_user(request):
    try:
        email = request.form.get("email")
        password = request.form.get("password")
        user = Users.query.filter_by(email=email).first()
        if user:
            if user.password != password:
                return (
                    render_template(
                        "error.html", message="Invalid password", ref="login"
                    ),
                    401,
                )
            else:
                session["user_email"] = email
                session["username"] = user.firstname
                flash("User has loged in successfully!", "success")
                return redirect("/chat")
        else:
            return (
                render_template("error.html", message="User not found", ref="signup"),
                404,
            )

    except Exception as e:
        return f"something went wrong to login: {e}"


def signup_user(request):
    try:
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        email = request.form.get("email")
        password = request.form.get("password")

        # search in database
        user = Users.query.filter_by(email=email).all()
        if len(user) != 0:
            return (
                render_template(
                    "error.html",
                    message="You have already registered with this email",
                    ref="signup",
                ),
                400,
            )
        else:
            new_user = Users(
                firstname=firstname,
                lastname=lastname,
                email=email,
                password=password,
            )
            db.session.add(new_user)
            db.session.commit()

            flash("User registered successfully!")
            return redirect("/login")

    except Exception as e:
        return f"something went wrong to add user: {e}"


def file_upload_user(request, main_dir, upload_dir):
    try:
        file_from_html = request.files.get("file")
        if file_from_html:
            file_from_html.save(f"./{main_dir}/{upload_dir}/user_info.pdf")
            flash("File uploaded successfully!")
            return redirect("/chat")
        else:
            raise Exception("file or directory does not exit...!")
    except Exception as e:
        return "Something went wrong related sending file: {e}"


def chat_user(request, file_exist: bool):
    try:
        user_email = session.get("user_email")
        username = session.get("username")
        if not user_email:
            return redirect("/login")

        if request.method == "GET":
            messages = extract_data(user_email)
            return render_template(
                "index.html",
                messages=messages,
                username=username,
                file_exist=file_exist,
            )

        elif request.method == "POST":
            question_from_html = request.form.get("text")
            gpt_server(question_from_html, user_email)
            messages = extract_data(user_email)
            return render_template(
                "index.html",
                messages=messages,
                username=username,
                file_exist=file_exist,
            )

        else:
            return "The resquest type should be either POST or GET", 400

    except Exception as e:
        raise Exception(f"there is a problem related GPT server: {e}")
