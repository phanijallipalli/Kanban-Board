from flask_restful import Resource
from flask_restful import fields, marshal_with
from flask_restful import reqparse
from flask_restful import Api
from .database import db 
from flask import render_template
from flask import current_app as app
from .validation import BusinessValidationError
from flask import request
from flask import abort
from .model import User,List,Tasks
from .controller import hash_password
from app import api
import json
from app import  app,bcrypt
from datetime import date

#---------------signup api ---------------------------

create_signup_parser = reqparse.RequestParser()
create_signup_parser.add_argument("username")
create_signup_parser.add_argument("password")


class SignupAPI(Resource):

    def post(self):
        args = create_signup_parser.parse_args()
        username = args.get("username",None)
        password = args.get("password",None)

        
        if (type(username) is str) and (username is not None) and (type(password) is str) and (password is not None) and (password != ""):
            user = User.query.filter_by(username = username).first()
            if user:
                raise BusinessValidationError(status_code=409, error_message="username is already exists")

            else:
                user = User(username = username, password = hash_password(password))
                db.session.add(user)
                db.session.commit()
                user = User.query.filter_by(username = username)
                return  201
        else:
            return BusinessValidationError(status_code=404, error_message="page not found")

#---------------------dashboardApi-------------------------- 


class DashboardAPI(Resource):
    def get(self,username):
        password = request.args.get("password",None)
        if (type(username) is str) and (username is not None) and (type(password) is str) and (password is not None) and (password != ""):
            user = User.query.filter_by(username = username).first()
            if not user:
                raise BusinessValidationError(status_code=404, error_message="user not found")
            elif(bcrypt.check_password_hash(user.password,password)):
                user_data = []
                lists = List.query.filter_by(username = username).all()
                list_dic = {}
                for list in lists:
                    list_dic[list.id] = list.list_name
                tasks = Tasks.query.filter_by(username = username).all()
                for task in tasks:
                    task_data = {}
                    task_data["listname"] = list_dic[task.status]
                    task_data["list-id"] = task.status
                    task_data["task-id"] = task.id
                    task_data["task-title"] = task.title
                    task_data["task-description"] = task.task
                    task_data["due-date"] = task.due_date
                    if (task.completed == 'true'):
                        task_data["status"] = "completed"
                    else:
                        task_data["status"] = "pending"
                    task_data["date-of-completion"] = task.date_of_completion
                    user_data.append(task_data)
                return user_data, 200
                
            else:
                raise BusinessValidationError(status_code=409, error_message="password incorrect")
        else:
            return BusinessValidationError(status_code=404, error_message="check inputs")   

#---------------------add List Api-------------------------- 
create_addlist_parser = reqparse.RequestParser()
create_addlist_parser.add_argument("addlist")

class AddlistsAPI(Resource):
    def post(self,username):
        password = request.args.get("password",None)
        args = create_addlist_parser.parse_args()
        addlist = args.get("addlist",None)
        if (type(username) is str) and (username is not None) and (type(password) is str) and (password is not None) and (password != ""):
            user = User.query.filter_by(username = username).first()
            if not user:
                raise BusinessValidationError(status_code=404, error_message="user not found")
            elif(bcrypt.check_password_hash(user.password,password)):
                lists = db.session.query(List).filter((List.username == username ) & (List.list_name == addlist)).first()
                if lists:
                    raise BusinessValidationError(status_code=406, error_message="list already exists")
                list = List(
                username = username,
                list_name = addlist
                )
                db.session.add(list)
                db.session.commit()
                return 200
            else:
                raise BusinessValidationError(status_code=409, error_message="password incorrect")
        else:
            return BusinessValidationError(status_code=404, error_message="check inputs") 

#---------------------add Task Api-------------------------- 
create_addtask_parser = reqparse.RequestParser()
create_addtask_parser.add_argument("list_id")
create_addtask_parser.add_argument("task_title")
create_addtask_parser.add_argument("task_description")
create_addtask_parser.add_argument("due_date")
create_addtask_parser.add_argument("mark_as_completed")
class AddTaskAPI(Resource):
    def post(self,username):
        password = request.args.get("password",None)
        args = create_addtask_parser.parse_args()
        list_id = args.get("list_id",None)
        task_title = args.get("task_title",None)
        task_description = args.get("task_description",None)
        due_date = args.get("due_date",None)
        mark_as_completed = args.get("mark_as_completed",None)
        if (type(username) is str) and (username is not None) and (type(password) is str) and (password is not None) and (password != ""):
            user = User.query.filter_by(username = username).first()
            if not user:
                raise BusinessValidationError(status_code=404, error_message="user not found")
            elif(bcrypt.check_password_hash(user.password,password)):
                lists = db.session.query(List).filter((List.username == username ) & (List.id == list_id)).first()
                if lists:
                    if (mark_as_completed == 'yes'):
                        completed_date = date.today().strftime('%Y-%m-%d')
                        completed = 'true'
                    else:
                        completed_date =  None
                        completed = 'false'
                    tasks = Tasks(
                            username = username,
                            task = task_description,
                            title = task_title,
                            status = list_id,
                            due_date = due_date,
                            completed = completed,
                            date_of_completion = completed_date)
                    db.session.add(tasks)
                    db.session.commit()
                    return 200
                else:
                    raise BusinessValidationError(status_code=410, error_message="list_id not exists")
            else:
                raise BusinessValidationError(status_code=409, error_message="password incorrect")
        else:
            return BusinessValidationError(status_code=404, error_message="check inputs")   
#---------------------ListsApi-------------------------- 
class ListsAPI(Resource):
    def get(self,username):
        password = request.args.get("password",None)
        if (type(username) is str) and (username is not None) and (type(password) is str) and (password is not None) and (password != ""):
            user = User.query.filter_by(username = username).first()
            if not user:
                raise BusinessValidationError(status_code=404, error_message="user not found")
            elif(bcrypt.check_password_hash(user.password,password)):
                user_data = []
                lists = List.query.filter_by(username = username).all()
                for list in lists:
                    list_dic = {}
                    list_dic["listname"] = list.list_name
                    list_dic["list-id"] = list.id
                    user_data.append(list_dic)
                return user_data, 200
                
            else:
                raise BusinessValidationError(status_code=409, error_message="password incorrect")
        else:
            return BusinessValidationError(status_code=404, error_message="check inputs")   
#---------------------ListApi-------------------------- 
create_list_parser = reqparse.RequestParser()
create_list_parser.add_argument("list_name")

class ListAPI(Resource):
    def get(self,username,list_id):
        password = request.args.get("password",None)
        if (type(username) is str) and (username is not None) and (type(password) is str) and (password is not None) and (password != ""):
            user = User.query.filter_by(username = username).first()
            if not user:
                raise BusinessValidationError(status_code=404, error_message="user not found")
            elif(bcrypt.check_password_hash(user.password,password)):
                user_data = []
                lists = List.query.filter_by(username = username ,id = list_id).first()
                if lists:
                    tasks = Tasks.query.filter_by(username = username,status = list_id ).all()
                    for task in tasks:
                        task_data = {}
                        task_data["listname"] = lists.list_name
                        task_data["list-id"] = task.status
                        task_data["task-id"] = task.id
                        task_data["task-title"] = task.title
                        task_data["task-description"] = task.task
                        task_data["due-date"] = task.due_date
                        if (task.completed == 'true'):
                            task_data["status"] = "completed"
                        else:
                            task_data["status"] = "pending"
                        task_data["date-of-completion"] = task.date_of_completion
                        user_data.append(task_data)
                    return user_data, 200
                else:
                    raise BusinessValidationError(status_code=405, error_message = "list not found")
                
            else:
                raise BusinessValidationError(status_code=409, error_message="password incorrect")
        else:
            return BusinessValidationError(status_code=404, error_message="check inputs")   


    def put(self,username,list_id):
        password = request.args.get("password",None)
        args = create_list_parser.parse_args()
        list_name = args.get("list_name",None)
        if (type(username) is str) and (username is not None) and (type(password) is str) and (password is not None) and (password != ""):
            user = User.query.filter_by(username = username).first()
            if not user:
                raise BusinessValidationError(status_code=404, error_message="user not found")
            elif(bcrypt.check_password_hash(user.password,password)):
                lists = db.session.query(List).filter((List.username == username ) & (List.id == list_id)).first()
                list2 = List.query.filter_by(username = username ,list_name = list_name).all()
                if list2:
                    raise BusinessValidationError(status_code=406, error_message="list already exists")
                if lists:
                    lists.list_name = list_name
                    db.session.commit()
                    return 200
                raise BusinessValidationError(status_code=405, error_message="list not found")
            else:
                raise BusinessValidationError(status_code=409, error_message="password incorrect")
    
    def delete(self,username,list_id):
        password = request.args.get("password",None)
        if (type(username) is str) and (username is not None) and (type(password) is str) and (password is not None) and (password != ""):
            user = User.query.filter_by(username = username).first()
            if not user:
                raise BusinessValidationError(status_code=404, error_message="user not found")
            elif(bcrypt.check_password_hash(user.password,password)):
                list_name = db.session.query(List).filter((List.username == username) & (List.id == list_id)).first()
                if list_name:
                    tasks = db.session.query(Tasks).filter((Tasks.username == username) & (Tasks.status == list_id)).all()
                    for task in tasks:
                        db.session.delete(task)
                    db.session.delete(list_name)
                    db.session.commit()
                    return 200
                raise BusinessValidationError(status_code=405, error_message="list not found")
            else:
                raise BusinessValidationError(status_code=409, error_message="password incorrect")
        else:
            return BusinessValidationError(status_code=404, error_message="check inputs")   

#---------------------TaskApi-------------------------- 
create_task_parser = reqparse.RequestParser()
create_task_parser.add_argument("list_id")
create_task_parser.add_argument("task_title")
create_task_parser.add_argument("task_description")
create_task_parser.add_argument("due_date")
create_task_parser.add_argument("status")


class TaskAPI(Resource):
    def get(self,username,task_id):
        password = request.args.get("password",None)
        if (type(username) is str) and (username is not None) and (type(password) is str) and (password is not None) and (password != ""):
            user = User.query.filter_by(username = username).first()
            if not user:
                raise BusinessValidationError(status_code=404, error_message="user not found")
            elif(bcrypt.check_password_hash(user.password,password)):
                user_data = {}
                task = Tasks.query.filter_by(username = username,id = task_id ).first()
                
                if task:
                    list = List.query.filter_by(username = username,id = task.status ).first()
                    user_data['listname'] = list.list_name
                    user_data['list_id'] = task.status
                    user_data['task_id'] = task.id
                    user_data['task_title'] = task.title
                    user_data['task_description'] = task.task
                    user_data['due_date'] = task.due_date
                    if (task.completed == 'true'):
                        user_data["status"] = "completed"
                    else:
                        user_data["status"] = "pending"
                    user_data['date_of_completion'] = task.date_of_completion
                    return user_data, 200
                else:
                    raise BusinessValidationError(status_code=405, error_message = "task not found")
                
            else:
                raise BusinessValidationError(status_code=409, error_message="password incorrect")
        else:
            return BusinessValidationError(status_code=404, error_message="check inputs")   


    def put(self,username,task_id):
        password = request.args.get("password",None)
        args = create_task_parser.parse_args()
        list_id = args.get("list_id",None)
        task_title = args.get("task_title",None)
        task_description = args.get("task_description",None)
        due_date = args.get("due_date",None)
        mark_as_completed = args.get("status",None)
        if (type(username) is str) and (username is not None) and (type(password) is str) and (password is not None) and (password != ""):
            user = User.query.filter_by(username = username).first()
            if not user:
                raise BusinessValidationError(status_code=404, error_message="user not found")
            elif(bcrypt.check_password_hash(user.password,password)):
                lists = db.session.query(List).filter((List.username == username ) & (List.id == list_id)).first()
                task = db.session.query(Tasks).filter((List.username == username ) & (List.id == task_id)).first()
                if lists and task:
                    if (mark_as_completed == 'yes'):
                        completed_date = date.today().strftime('%Y-%m-%d')
                        completed = 'true'
                    else:
                        completed_date =  None
                        completed = 'false'
                    task.task = task_description
                    task.title = task_title
                    task.status = list_id
                    task.due_date = due_date
                    task.completed = completed
                    task.date_of_completion = completed_date
                    db.session.commit()
                    return 200
                raise BusinessValidationError(status_code=405, error_message="list_id or task_id is incorrect")
            else:
                raise BusinessValidationError(status_code=409, error_message="password incorrect")
    
    def delete(self,username,task_id):
        password = request.args.get("password",None)
        if (type(username) is str) and (username is not None) and (type(password) is str) and (password is not None) and (password != ""):
            user = User.query.filter_by(username = username).first()
            if not user:
                raise BusinessValidationError(status_code=404, error_message="user not found")
            elif(bcrypt.check_password_hash(user.password,password)):
                task = db.session.query(Tasks).filter((Tasks.username == username ) & (Tasks.id == task_id)).first()
                if task:
                    db.session.delete(task)
                    db.session.commit()
                    return 200
                else:
                    raise BusinessValidationError(status_code=405, error_message = "task not found")
                
            else:
                raise BusinessValidationError(status_code=409, error_message="password incorrect")
        else:
            return BusinessValidationError(status_code=404, error_message="check inputs")  
