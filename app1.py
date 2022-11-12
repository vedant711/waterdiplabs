from flask import Flask,render_template,request,flash,redirect,jsonify
from flask_sqlalchemy import SQLAlchemy
import json
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config['SECRET_KEY'] = 'MLXH243GssUWwKdTWS7FDhdwYF56wPj8'
db_name='task.db'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+db_name
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
ma = Marshmallow(app)

class Task(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(80),nullable=False)
    is_completed=db.Column(db.Boolean)

class TaskSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Task
        load_instance=True

app.app_context().push()

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def home():
    tasks = Task.query.all()
    task_schema=TaskSchema(many=True)
    output=task_schema.dump(tasks)
    return jsonify({'task':output})

@app.route('/v1/tasks',methods=['GET','POST','DELETE'])
def tasks():
    if request.method=='POST':
        r=json.loads(request.data.decode())
        if 'title' in r.keys():
            title=r['title']
            is_completed=False
            task=Task(title=title,is_completed=is_completed)
            db.session.add(task)
            db.session.commit()
            id=task.id
            return jsonify({'id':id}),201
        elif 'tasks' in r.keys():
            ids=[]
            for task in r['tasks']:
                title=task['title']
                is_completed=task['is_completed']
                t=Task(title=title,is_completed=is_completed)
                db.session.add(t)
                db.session.commit()
                id=t.id
                ids.append({'id':id})
            return jsonify({'tasks':ids}),201
    elif request.method=='GET':
        tasks = Task.query.all()
        task_schema=TaskSchema(many=True)
        output=task_schema.dump(tasks)
        return jsonify({'tasks':output}),200
    elif request.method=='DELETE':
        try:
            r=json.loads(request.data.decode())
            for task in r['tasks']:
                id = task['id']
                t=Task.query.get(id)
                db.session.delete(t)
                db.session.commit()
            return redirect('/'),204
        except:
            e='There is no task at that id'
            return jsonify({'error':e}),404

@app.route('/v1/tasks/<id>',methods=['GET','PUT','DELETE','POST'])
def indi_task(id):
    if request.method=='GET':
        try:
            task=Task.query.filter(Task.id==id).first()
            task_schema=TaskSchema()
            output=task_schema.dump(task)
            return jsonify(output),200
        except:
            e='There is no task at that id'
            return jsonify({'error':e}),404
    if request.method=='PUT':
        try:
            task=Task.query.get(id)
            r=json.loads(request.data.decode())
            task.title=r['title']
            task.is_completed=r['is_completed']
            db.session.commit()
            return redirect('/'),204
        except:
            e='There is no task at that id'
            return jsonify({'error':e}),404
        
    if request.method=='DELETE':
        try:
            task=Task.query.get(id)
            db.session.delete(task)
            db.session.commit()
            return redirect('/'),204
        except:
            e='There is no task at that id'
            return jsonify({'error':e}),404


if __name__=='__main__':
    app.run(debug=True)