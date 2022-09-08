from operator import truediv
from re import template
from app import  app,bcrypt
from flask import render_template,request,redirect,url_for,session,flash
from sqlalchemy import func
from .database import db 
from .model import User,List,Tasks
import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import date

def hash_password(password):
    pw_hash = bcrypt.generate_password_hash(password)
    return pw_hash


@app.route('/signup',methods=["POST","GET"])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    elif request.method == 'POST':
        user = db.session.query(User).filter(User.username==request.form['username']).first()
        if not user:
            user = User(
                username = request.form['username'],
                password = hash_password(request.form['password'])
            )
            db.session.add(user)
            db.session.commit()
            return redirect('/')
        else:
            flash('Username already existed')
            return render_template('signup.html')

@app.route('/login',methods=["POST","GET"])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        user = db.session.query(User).filter(User.username==request.form['username']).first()
        if not user:
            flash('Invalid Username')
            return render_template('login.html')
        elif(bcrypt.check_password_hash(user.password,request.form['password'])):
            session['username'] = user.username
            return redirect('/')
        else:
            flash('incorrect password')
            return render_template('login.html')
        


@app.route('/')
def index():
    if not session.get('username'):
        return redirect(url_for('login'))
    else:
        username = session.get('username')
        data = {}
        lists = db.session.query(List).filter(List.username==username)
        for list in lists:
            tasks = db.session.query(Tasks).filter((Tasks.username == username) & (Tasks.status == list.id))
            task_data = []
            for task in tasks:
                task_data.append(task)
            data[list.list_name] = task_data

        
        return render_template('index.html',data = data,username = session.get('username'))


@app.route('/logout')
def log_out():
    session.pop('username', None)
    return redirect(url_for('index'))

    
@app.route('/<username>/addlist', methods=['GET', 'POST'])
def addlist(username):
    user = db.session.query(User).filter(User.username==username).first()
    if request.method == 'GET':
        return render_template('addlist.html' , data = user.username )
    elif request.method == 'POST':
        list = db.session.query(List).filter((List.list_name == request.form['listname']) & (List.username == request.form['user'])).first()
        if not list:
            list = List(
                username = request.form['user'],
                list_name = request.form['listname']
            )
            db.session.add(list)
            db.session.commit()
            return redirect('/') 
        else:
            flash('list name already exists')
            return redirect('/'+ username + '/addlist')

@app.route('/<username>/addtask', methods=['GET', 'POST'])
def addtask(username):
    if request.method == 'GET':
        lists = db.session.query(List).filter(List.username == username).all()
        return render_template('addtask.html' , data = username ,lists = lists)
    elif request.method == 'POST':
        list = db.session.query(List).filter((List.username == request.form['user']) & (List.list_name == request.form['status'])).first()
        if (request.form['completed'] == 'true'):
            completed_date = date.today().strftime('%Y-%m-%d')
        else:
            completed_date =  None
        tasks = Tasks(
                username = request.form['user'],
                task = request.form['Task-description'],
                title = request.form['Task-title'],
                status = list.id,
                due_date = request.form['Due'],
                completed = request.form['completed'],
                date_of_completion = completed_date)
        db.session.add(tasks)
        db.session.commit()
        return redirect('/')


@app.route('/<username>/<task_id>/edit', methods=['GET', 'POST'])
def edit_task(username,task_id):
    if request.method == 'GET':
        task = db.session.query(Tasks).filter((Tasks.username == username) & (Tasks.id == task_id)).first()
        lists = db.session.query(List).filter((List.username == username)).all()
        list_name = db.session.query(List).filter((List.username == username) & (List.id == task.status)).first()
        return render_template('editcard.html' , task = task , data = username,list_name = list_name.list_name , lists = lists)
    elif request.method == 'POST':
        list = db.session.query(List).filter((List.username == request.form['user']) & (List.list_name == request.form['status'])).first()
        task = db.session.query(Tasks).filter((Tasks.username == request.form['user']) & (Tasks.id == request.form['id'])).first()
        if (request.form['completed'] == 'true'):
            completed_date = date.today()
        else:
            completed_date =  None

        task.task = request.form['Task-description']
        task.title = request.form['Task-title']
        task.status = list.id
        task.due_date = request.form['Due']
        task.completed = request.form['completed']
        task.date_of_completion = completed_date
        db.session.commit()
        return redirect('/')

@app.route('/<username>/<task_id>/delete', methods=['GET'])
def deletecard(username,task_id):
    if request.method == 'GET':
        task = db.session.query(Tasks).filter((Tasks.username == username) & (Tasks.id == task_id)).first()
        lists = db.session.query(List).filter((List.username == username) & (Tasks.id == task.id)).first()
        return render_template('deletecard.html',Tasks = task,list = lists,username=username)

@app.route('/<username>/<task_id>/delete/yes', methods=['GET'])
def deletecardsure(username,task_id):
    if request.method == 'GET':
        task = db.session.query(Tasks).filter((Tasks.username == username) & (Tasks.id == task_id)).first()
        db.session.delete(task)
        db.session.commit()
        return redirect('/')


@app.route('/<username>/<listname>/editlist', methods=['GET', 'POST'])
def edit_list(username,listname):
    if request.method == 'GET':
        list_name = db.session.query(List).filter((List.username == username) & (List.list_name == listname)).first()
        return render_template('editlist.html', data = username,list_name = list_name)
    elif request.method == 'POST':
        list = db.session.query(List).filter((List.username == request.form['user']) & (List.id == request.form['id'])).first()
        list2 = db.session.query(List).filter((List.username == request.form['user']) & (List.list_name == request.form['listname'])).first()
        if list2:
            flash('List name already exists')
            return render_template('editlist.html', data = request.form['user'],list_name = list)
        
        list.list_name = request.form['listname']
        db.session.commit()
        return redirect('/')

@app.route('/<username>/<listname>/deletelist', methods=['GET'])
def delete_list(username,listname):
    if request.method == 'GET':
        list_name = db.session.query(List).filter((List.username == username) & (List.list_name == listname)).first()
        tasks = db.session.query(Tasks).filter((Tasks.username == username) & (Tasks.status == list_name.id)).all()
        return render_template('deletelist.html',tasks = tasks , list = listname,username = username)

@app.route('/<username>/<listname>/deletelist/yes', methods=['GET'])
def delete_list_yes(username,listname):
    if request.method == 'GET':
        list_name = db.session.query(List).filter((List.username == username) & (List.list_name == listname)).first()
        tasks = db.session.query(Tasks).filter((Tasks.username == username) & (Tasks.status == list_name.id)).all()
        for task in tasks:
            db.session.delete(task)
        db.session.delete(list_name)
        db.session.commit()
        return redirect('/')

@app.route('/<username>/summary')
def summary(username):
    task_counts = db.session.query(Tasks).filter((Tasks.username == username)).count()
    if (task_counts > 0 ):
        tasks = db.session.query(Tasks).filter((Tasks.username == username)).all()
        lists = db.session.query(List).filter((List.username == username)).all()
        datas = {}
        due = {}
        for list in lists:
            listname = list.list_name
            task_count = db.session.query(Tasks).filter((Tasks.username == username) & (Tasks.status == list.id)).count()
            task_due_date_over = db.session.query(Tasks).filter((Tasks.username == username) & (Tasks.status == list.id) & (func.date(Tasks.due_date) <  date.today())).count()
            task_done = db.session.query(Tasks).filter((Tasks.username == username) & (Tasks.status == list.id) & (Tasks.completed == 'true')).count()
            if (task_count > 0):
                datas[listname] = task_count
                data = np.array([task_due_date_over,task_count-task_due_date_over])
                my_label = ['Deadline Passed','Deadline not Passed']
                plt.bar(my_label,data)
                path = 'app/static/' + listname + '.jpg'
                if(os.path.exists(path=path)):
                    os.remove(path)
                plt.savefig(path)
                plt.close()
                data = np.array([task_done,task_count-task_done])
                my_label = ['Done','Pending']
                plt.pie(data,labels=my_label)
                plt.legend()
                path = 'app/static/' + listname + 'done.jpg'
                if(os.path.exists(path=path)):
                    os.remove(path)
                plt.savefig(path)
                plt.close()
        tasks_completed = db.session.query(Tasks).filter((Tasks.username == username) & (Tasks.completed == 'true')).count()
        data = np.array([tasks_completed,task_counts-tasks_completed])
        my_labels = ['done','pending']
        plt.pie(data,labels=my_labels)
        plt.legend()
        path = 'app/static/percentagecompleted.jpg'
        if(os.path.exists(path=path)):
            os.remove(path)
        plt.savefig(path)
        plt.close()
        task_due_date_over = db.session.query(Tasks).filter((Tasks.username == username) & (func.date(Tasks.due_date) <  date.today())).count()
        data = np.array([task_due_date_over,task_counts-task_due_date_over])
        my_label = ['Deadline Passed','Deadline not Passed']
        plt.bar(my_label,data)
        path = 'app/static/deadline.jpg'
        if(os.path.exists(path=path)):
            os.remove(path)
        plt.savefig(path)
        plt.close()

        data = []
        values = []
        for task in tasks:
            dates = str(task.due_date)
            if dates in data:
                index = data.index(dates)
                values[index] = values[index] + 1
            else:
                data.append(dates) 
                values.append(1)
        dat = values
        keys = data
        plt.plot_date(keys,dat,linestyle = 'solid')
        path = 'app/static/graph.jpg'
        if(os.path.exists(path=path)):
            os.remove(path)
        plt.savefig(path)
        plt.close()

        plt.pie(dat,labels=keys)
        path = 'app/static/graph-pie.jpg'
        if(os.path.exists(path=path)):
            os.remove(path)
        plt.savefig(path)
        plt.close()
        return render_template('summary.html',data = datas)
    else:
        return render_template('summary-empty.html')








