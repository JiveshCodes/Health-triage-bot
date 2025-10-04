# from flask import Flask, render_template, request
# from triage_engine import analyze_symptoms

# app = Flask(__name__)

# @app.route("/", methods=["GET", "POST"])
# def index():
#     result = None
#     if request.method == "POST":
#         symptoms = request.form.get("symptoms")
#         if symptoms:
#             result = analyze_symptoms(symptoms)
#     return render_template("index.html", result=result)

# if __name__ == "__main__":
#     app.run(debug=True)
from flask import Flask, render_template, request
from triage_engine import analyze_symptoms

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        symptoms = request.form.get("symptoms")
        if symptoms:
            result = analyze_symptoms(symptoms)
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
