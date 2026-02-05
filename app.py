import sqlite3
from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'abcd1234'

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
        priority TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)         
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL          
    )
    ''')
    conn.commit()
    conn.close()

init_db()



'''----------------------LOGIN ROUTE---------------------'''
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        conn = sqlite3.connect('to_do_list.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', (username,))
        user_exists = cursor.fetchone()[0] > 0

        if user_exists:
            flash('Username already exists.', 'error')
        else:
            cursor.execute('INSERT INTO users (username,password) VALUES (?,?)', (username,hashed_password))
            conn.commit()
            flash('Registration succesful! Please log in.', 'success')
            conn.close()
            return redirect('/login')
        conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('to_do_list.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        print(user)
        conn.close()
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            flash('Login succesful', 'success')
            return redirect('/')
        flash('Invalid username or password.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect('/login')

'''------------------------- PAGE VIEW ----------------'''
@app.route("/")
def index():
    if 'user_id' not in session:
        return redirect('/login')
    conn = sqlite3.connect('to_do_list.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM to_do_list_items WHERE user_id = ? ORDER BY item_number ASC", (session['user_id'],))
    to_do_list = cursor.fetchall()
    username = session['username']
    conn.close()
    
    return render_template("index.html", priorities = PRIORITIES, to_do_list = to_do_list, username=username)

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
    user_id = session.get('user_id')
    if 'user_id' not in session:
        flash('Please log in to add items.', 'error')
        return redirect('/login')
    item = request.form.get('item')
    priority = request.form.get('priority')
    conn = sqlite3.connect('to_do_list.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO to_do_list_items (item,priority,user_id) VALUES (?,?,?)", (item, priority, user_id))
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
