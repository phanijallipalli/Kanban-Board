from app import app
from app import api

from app.api import SignupAPI,DashboardAPI,ListsAPI,ListAPI,AddlistsAPI,AddTaskAPI,TaskAPI
api.add_resource(SignupAPI, "/api/signup") 
api.add_resource(DashboardAPI, "/api/<username>") 
api.add_resource(ListsAPI, "/api/<username>/lists")
api.add_resource(ListAPI, "/api/<username>/<list_id>")
api.add_resource(AddlistsAPI, "/api/<username>/addlist")
api.add_resource(AddTaskAPI, "/api/<username>/addtask")
api.add_resource(TaskAPI, "/api/<username>/task/<task_id>")


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)