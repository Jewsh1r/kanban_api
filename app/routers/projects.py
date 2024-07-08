from fastapi import APIRouter, Depends, HTTPException
from dependencies import get_current_user
from databases import AsyncDatabase
from models import Project, ProjectList

router = APIRouter()

@router.get("/", response_model=ProjectList)
async def get_all_projects(user=Depends(get_current_user)):
    async with AsyncDatabase() as db:
        projects = await db.get_all_projects()
        project_list = [Project.from_orm(proj) for proj in projects]
        return ProjectList(projects=project_list)

@router.post("/{id}", response_model=Project)
async def get_project_by_id(id: str, user=Depends(get_current_user)):
    async with AsyncDatabase() as db:
        project = await db.get_by_id_project(id)
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        return Project.from_orm(project)
