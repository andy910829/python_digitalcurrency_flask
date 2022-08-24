from flask import Flask, render_template, redirect, request, url_for
from digitalcurrency import getprice, strategy

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=["POST","GET"])
def login():
    try:
        if request.method == "POST":
            currency = request.form["cry"]
            strategy = request.form["stg"]
            return redirect(url_for("currency", currency = currency, strategy = strategy))
        else:
            return render_template("login.html")
    except:
        return render_template("login.html")

@app.route("/<currency><strategy>")
def currency(currency, strategy):          
    return f"<h1>{currency}{strategy}</h1>"

if __name__ == "__main__":
    app.run(debug = True)