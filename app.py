from flask import Flask, render_template, request, redirect

app = Flask(__name__)
#Another comment
PRIORITIES = ["High", "Medium", "Low"]
to_do_list = []
is_sorted = False
priority_order_high_to_low = {"High": 1, "Medium": 2, "Low": 3}
priority_order_low_to_high = {"Low": 1, "Medium": 2, "High": 3}

@app.route("/")
def index():
    return render_template("index.html", priorities = PRIORITIES, to_do_list = to_do_list)

@app.route('/updateList', methods=["POST"])
def updateList():
    item = request.form.get('item')
    priority = request.form.get('priority')
    index = len(to_do_list) + 1
    to_do_list.append({"index": index, "item": item, "priority": priority})
    return redirect("/")


@app.route('/sort')
def sort():
    global is_sorted

    if is_sorted:
        is_sorted = False
        sorted_list = sorted(to_do_list, key=lambda x: priority_order_high_to_low[x["priority"]])
    else:
        is_sorted = True
        sorted_list = sorted(to_do_list, key=lambda x: priority_order_low_to_high[x["priority"]])
    return render_template("index.html", to_do_list = sorted_list, priority = PRIORITIES)

if __name__ == '__main__':
    app.run(debug=True)
