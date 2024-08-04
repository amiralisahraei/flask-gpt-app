from flask import Flask, request, render_template
from gpt_server import gpt_server
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


questions_array = []
responses_array = []


@app.route("/")
def hello():
    return render_template("index.html")


@app.route("/chat", methods=["GET", "POST"])
def chat():
    try:
        if request.method == "GET":
            combined = list(zip(questions_array, responses_array))
            return render_template("index.html", messages=combined)

        elif request.method == "POST":
            question_from_html = request.form.get("text")
            res_from_gpt = gpt_server(
                question_from_html, list(zip(questions_array, responses_array))
            )
            questions_array.append(question_from_html)
            responses_array.append(res_from_gpt)
            combined = list(zip(questions_array, responses_array))
            return render_template("index.html", messages=combined)

        else:
            return "The resquest type should be either POST or GET", 400

    except Exception as e:
        raise Exception(f"there is a problem related GPT server: {e}")


if __name__ == "__main__":
    app.run(debug=True, port=8080)
