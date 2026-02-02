from flask import Flask, render_template, request, redirect

app = Flask(__name__)
#Another comment
PRIORITIES = ["High", "Medium", "Low"]

@app.route("/")
def index():
    return render_template("index.html", priorities = PRIORITIES)

@app.route('/sort')
def sort():
    pass

if __name__ == '__main__':
    app.run(debug=True)
