from flask import Flask, render_template, request
import requests

app = Flask(__name__)

car_models = {
    "honda": ["Civic", "Accord", "CR-V"],
    "toyota": ["Camry", "Corolla", "Rav4"],
    "nissan": ["Altima", "Maxima", "Murano"],
}


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/cars", methods=["GET"])
def cars():
    car_maker = request.args.get("maker")
    list_of_models = car_models[car_maker]
    return render_template("available_models.html", list_of_models=list_of_models)


@app.route("/search_coins")
def search_coins():
    query = request.args.get("query")
    if query:
        r = requests.get(f"https://api.coingecko.com/api/v3/search?query={query}")
        coins = r.json()["coins"]

        return render_template("coins.html", coins=coins)
    return ""


if __name__ == "__main__":
    app.run(debug=True)
