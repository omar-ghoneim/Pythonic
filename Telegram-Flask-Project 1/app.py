from flask import Flask, request


app = Flask("__name__")


@app.route("/")
def home():
    text = request.args.get("text")
    return f"Flask received the following text:{text}"


if __name__ == "__main__":
    app.run(debug=True)
