from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class ServiceIdentityRead(BaseModel):
    service_user_id: str
    service_name: str

    class Config:
        from_attributes = True
class EmployeeRead(BaseModel):
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    department: Optional[str]
    service_identities: List[ServiceIdentityRead]

    class Config:
        from_attributes = True

class Employee(BaseModel):
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    department: Optional[str]

    class Config:
        from_attributes = True

class EmployeeServiceLink(BaseModel):
    email: str
    service_user_id: str
    service_name: str

    class Config:
        from_attributes = True
class EmployeeList(BaseModel):
    employees: List[Employee]

class ProjectBase(BaseModel):
    id: str
    name: str

class Project(ProjectBase):
    # pass
    class Config:
        from_attributes = True

class ProjectList(BaseModel):
    projects: List[Project]

class TaskBase(BaseModel):
    id: str
    name: str
    status: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    deadline: Optional[date] = None


class Task(TaskBase):
    assigned_employee_id: Optional[str] = None
    parent_task_id: Optional[str] = None

    class Config:
        from_attributes = True

class TaskList(BaseModel):
    tasks: List[Task]
