from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Backend is running"

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["cv"]
    return "File received"


if __name__ == "__main__":
    app.run(debug=True)