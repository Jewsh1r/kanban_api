from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from dependencies import get_current_user
from databases import AsyncDatabase
from models import Employee, EmployeeList, EmployeeRead, EmployeeServiceLink
from typing import List


router = APIRouter()

@router.get("/", response_model=EmployeeList)
async def get_all_employees(user=Depends(get_current_user)):
    async with AsyncDatabase() as db:
        employees = await db.get_all_employees()
        employee_list = [Employee.from_orm(emp) for emp in employees]
        return EmployeeList(employees=employee_list)

@router.post("/{email}", response_model=Employee)
async def get_employee_by_email(email: str, user=Depends(get_current_user)):
    async with AsyncDatabase() as db:
        employee = await db.get_by_email_employee(email)
        if employee is None:
            raise HTTPException(status_code=404, detail="Employee not found")
        return Employee.from_orm(employee)

@router.post("/service_identity/{email}", response_model=EmployeeRead)
async def get_service_identities(email: str, user=Depends(get_current_user)):
    async with AsyncDatabase() as db:
        employee = await db.get_service_identities_by_employee_email(email)
        if employee is None:
            raise HTTPException(status_code=404, detail="Employee not found")
        return EmployeeRead.from_orm(employee)


@router.get("/service_links", response_model=List[EmployeeServiceLink])
async def get_all_service_links(user=Depends(get_current_user)):
    async with AsyncDatabase() as db:
        employees = await db.get_all_service_links()

        service_links = []
        for employee in employees:
            for service_identity in employee.service_identities:
                service_link = EmployeeServiceLink(
                    email=employee.email,
                    service_user_id=service_identity.service_user_id,
                    service_name=service_identity.service_name
                )
                service_links.append(service_link)

        return service_links