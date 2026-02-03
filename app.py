import sqlite3
from flask import Flask, render_template, request, redirect

app = Flask(__name__)
#Another comment
PRIORITIES = ["High", "Medium", "Low"]
#to_do_list = []
is_sorted = False
priority_order_high_to_low = {"High": 1, "Medium": 2, "Low": 3}
priority_order_low_to_high = {"Low": 1, "Medium": 2, "High": 3}
edit_index = None

def init_db():
    conn = sqlite3.connect('to_do_list.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS to_do_list_items(
        item_number INTEGER PRIMARY KEY AUTOINCREMENT,
        item TEXT NOT NULL,
        priority TEXT NOT NULL          
    )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def index():
    conn = sqlite3.connect('to_do_list.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM to_do_list_items ORDER BY item_number ASC")
    to_do_list = cursor.fetchall()
    conn.close()
    
    return render_template("index.html", priorities = PRIORITIES, to_do_list = to_do_list)

@app.route('/edit_item', methods=["POST"])
def edit_item():
    edit_id = int(request.form.get("edit"))
    conn = sqlite3.connect('to_do_list.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM to_do_list_items")
    to_do_list = cursor.fetchall()
    conn.close()
    return render_template("index.html", priorities=PRIORITIES, to_do_list=to_do_list, edit_index=edit_id)

@app.route('/save_item', methods=["POST"])
def save_item():
    #global edit_index
    #record_index = int(request.form.get("edit_index")) - 1
    item_id = request.form.get("edit_index")
    new_item = request.form.get("new_item")
    new_priority = request.form.get("new_priority")

    #to_do_list[record_index]["item"] = new_item
    #to_do_list[record_index]["priority"] = new_priority
    conn = sqlite3.connect('to_do_list.db')
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE to_do_list_items SET item = ?, priority = ? WHERE item_number = ?",
        (new_item,new_priority,item_id)
    )
    conn.commit()
    conn.close()


    edit_index = None
    return redirect("/")

@app.route('/updateList', methods=["POST"])
def updateList():
    item = request.form.get('item')
    priority = request.form.get('priority')
    conn = sqlite3.connect('to_do_list.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO to_do_list_items (item,priority) VALUES (?,?)", (item, priority))
    conn.commit()
    conn.close()
    #index = len(to_do_list) + 1
    #to_do_list.append({"index": index, "item": item, "priority": priority})
    return redirect("/")

@app.route('/delete_item', methods=["POST"])
def delete_item():
    #record_index = int(request.form.get("delete")) - 1
    #to_do_list.pop(record_index)

    #for i, item in enumerate(to_do_list):
    #    item["index"] = i + 1
    item_id = request.form.get("delete")
    conn = sqlite3.connect('to_do_list.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM to_do_list_items WHERE item_number = ?", (item_id))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route('/sort')
def sort():
    global is_sorted
    conn = sqlite3.connect('to_do_list.db')
    cursor = conn.cursor()

    if is_sorted:
        is_sorted = False
        cursor.execute(''' SELECT * FROM to_do_list_items ORDER BY CASE priority
            WHEN 'High' THEN 1
            WHEN 'Medium' THEN 2
            WHEN 'Low' THEN 3
            END
        ''')
    else:
        is_sorted = True
        cursor.execute(''' SELECT * FROM to_do_list_items ORDER BY CASE priority
            WHEN 'Low' THEN 1
            WHEN 'Medium' THEN 2
            WHEN 'High' THEN 3
            END
        ''')
    sorted_list = cursor.fetchall()
    conn.close()
    return render_template("index.html", to_do_list = sorted_list, priority = PRIORITIES)

if __name__ == '__main__':
    app.run(debug=True)
