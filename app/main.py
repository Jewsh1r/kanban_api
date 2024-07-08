from fastapi import FastAPI, Depends
from routers import employees, projects, tasks
# from .dependencies import get_current_user

app = FastAPI()



app = FastAPI()

app.include_router(employees.router, prefix="/employees", tags=["employees"])
app.include_router(projects.router, prefix="/projects", tags=["projects"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
