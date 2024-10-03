from flask import Flask, render_template, redirect, url_for, request, session
from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedColumn
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap5
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from datetime import datetime

DONE_TASKS = []

app = Flask(__name__)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.db"
app.config["SECRET_KEY"] = "My Secret Key"
db.init_app(app)

Bootstrap5(app)

class ToDo(db.Model):
    id: Mapped[int] = MappedColumn(Integer, primary_key=True)
    task: Mapped[str] = MappedColumn(String)

class Tasks(FlaskForm):
    task = StringField("Task", validators=[DataRequired()])
    submit = SubmitField("Add")

class Contact(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    number = StringField("Number")
    submit = SubmitField("Contact")

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    day = datetime.now().strftime("%A")
    date = datetime.now().strftime("%d-%m-%y")
    with app.app_context():
        tasks = db.session.execute(db.select(ToDo).order_by(ToDo.id))
        all_tasks = tasks.scalars().all()
    return render_template("index.html", tasks=all_tasks, day=day, date=date, done_tasks=DONE_TASKS)

@app.route("/add", methods=["POST", "GET"])
def add():
    form = Tasks()
    if form.validate_on_submit():
        task = form.task.data
        new_task = ToDo(task=task)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add.html", form=form)

@app.route("/done", methods=["POST", "GET"])
def done():
    task_id = request.args.get("id")
    task = db.get_or_404(ToDo, task_id)
    DONE_TASKS.append(task.task)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/contact", methods=["POST", "GET"])
def contact():
    form = Contact()
    if form.validate_on_submit():
        print(f"{form.name.data} with email {form.email.data} and number {form.number.data} has contacted you!")
        return redirect(url_for("home"))
    return render_template("contact.html", form=form)

if __name__ == "__main__":
    app.run(debug=True)