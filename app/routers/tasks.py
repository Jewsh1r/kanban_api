from fastapi import APIRouter, Depends, HTTPException
from dependencies import get_current_user
from databases import AsyncDatabase
from models import Task, TaskList

router = APIRouter()

@router.get("/", response_model=TaskList)
async def get_all_tasks(user=Depends(get_current_user)):
    async with AsyncDatabase() as db:
        tasks = await db.get_all_tasks()
        task_list = [Task.from_orm(task) for task in tasks]
        return TaskList(tasks=task_list)

@router.post("/{id}", response_model=Task)
async def get_tasks_by_id(id: str, user=Depends(get_current_user)):
    async with AsyncDatabase() as db:
        task = await db.get_by_id_task(id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return Task.from_orm(task)

@router.post("/assigned/{id}", response_model=TaskList)
async def get_tasks_assigned_to_employee(id: str, user=Depends(get_current_user)):
    async with AsyncDatabase() as db:
        tasks = await db.get_assigned_tasks(id)
        task_list = [Task.from_orm(task) for task in tasks]
        return TaskList(tasks=task_list)

@router.post("/email/{email}", response_model=TaskList)
async def get_tasks_by_employee_email(email: str, user=Depends(get_current_user)):
    async with AsyncDatabase() as db:
        tasks = await db.get_tasks_by_email(email)
        task_list = [Task.from_orm(task) for task in tasks]
        return TaskList(tasks=task_list)
