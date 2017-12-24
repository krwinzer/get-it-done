from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://get-it-done:getitdone2017@localhost:8889/get-it-done'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)
app.secret_key = 'thm65#hfodu*837'

class Task(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    completed = db.Column(db.Boolean)

    def __init__(self, name):
        self.name = name
        self.completed = False

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))

    def __init__(self, email, password):
        self.email = email
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route('/', methods = ['POST','GET'])
def index():

    if request.method == 'POST':
        task_name = request.form['task']
        new_task = Task(task_name)
        db.session.add(new_task)
        db.session.commit()

    tasks = Task.query.filter_by(completed = False).all()
    completed_tasks = Task.query.filter_by(completed = True).all()
    return render_template('todos.html', title="Get It Done",
                    tasks=tasks, completed_tasks=completed_tasks)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash("Logged in")
            return redirect('/')
        else:
            flash("User password incorrect, or user does not exist", 'error')

    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

    # ------------Blank Fields ---------------

        if len(email) == 0:
            flash("The email field was left blank.", 'error')
        else:
            email = email
        if len(password) == 0:
            flash('The password field was left blank.', 'error')
        else:
            password = password
        if len(verify) == 0:
            flash('The verify password field was left blank.', 'error')
        else:
            verify = verify

    # --------Invalid Username, Password, Email-------------

        if len(email) != 0:
            if len(email) < 5 or len(email) > 40 or ' ' in email or '@' not in email or '.' not in email:
                # if '@' not in email and '.' not in email:
                flash('Email must be between 4 and 20 characters long, cannot contain spaces, and must be in proper email format.', 'error')
            else:
                email = email

        if len(password) != 0:
            if len(password) < 4 or len(password) > 19 or ' ' in password:
                flash("The password must be between 4 and 19 characters long and cannot contain spaces.", 'error')
            else:
                password = password

    # --------Password and Verify Do Not Match----------

        for char, letter in zip(password, verify):
            if char != letter:
                flash('Passwords do not match.', 'error')
            else:
                verify = verify
                password = password

        if email and password and verify:
            existing_user = User.query.filter_by(email=email).first()
            if not existing_user:
                new_user = User(email, password)
                db.session.add(new_user)
                db.session.commit()
                session['email'] = email
                return redirect('/')
            else:
                #TODO - user better response messaging
                return "<h1>Duplicate User</h1>"
        else:
            return render_template('register.html')

    return render_template('register.html')

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/')

@app.route('/delete-task', methods=['POST'])
def delete_task():

    task_id = int(request.form['task-id'])
    task = Task.query.get(task_id)
    task.completed = True
    db.session.add(task)
    db.session.commit()

    return redirect('/')

if __name__ == '__main__':
    app.run()
