import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref, joinedload
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Table, select

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

Base = declarative_base()

project_members = Table('project_members', Base.metadata,
    Column('project_id', String, ForeignKey('projects.id')),
    Column('service_user_id', String, ForeignKey('service_identities.service_user_id'))
)

class Project(Base):
    __tablename__ = 'projects'
    id = Column(String, primary_key=True)
    name = Column(String)
    members = relationship('ServiceIdentity', secondary=project_members, back_populates="projects")

class ServiceIdentity(Base):
    __tablename__ = 'service_identities'
    service_user_id = Column(String, primary_key=True)
    employee_email = Column(String, ForeignKey('employees.email'))
    service_name = Column(String)
    projects = relationship('Project', secondary=project_members, back_populates="members")
    employee = relationship("Employee", back_populates="service_identities")
    tasks = relationship("Task", back_populates="assigned_service_identity")

class Employee(Base):
    __tablename__ = 'employees'
    email = Column(String, primary_key=True, unique=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    department = Column(String, nullable=True)
    service_identities = relationship("ServiceIdentity", back_populates="employee")



class Task(Base):
    __tablename__ = 'tasks'
    id = Column(String, primary_key=True)
    assigned_employee_id = Column(String, ForeignKey('service_identities.service_user_id'))
    parent_task_id = Column(String, ForeignKey('tasks.id'), nullable=True)
    name = Column(String)
    status = Column(String)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    deadline = Column(Date, nullable=True)

    assigned_service_identity = relationship("ServiceIdentity", back_populates="tasks")
    subtasks = relationship("Task", backref=backref('parent', remote_side=[id]))

class AsyncDatabase:
    def __init__(self):
        self.engine = create_async_engine(
            f"postgresql+asyncpg://{os.getenv('DATABASE_USERNAME')}:{os.getenv('DATABASE_PASSWORD')}@"
            f"{os.getenv('DATABASE_IP')}:{os.getenv('DATABASE_PORT')}/"
            f"{os.getenv('DATABASE_NAME')}",
            echo=False
        )
        # print('Connected to database ' + os.getenv('DATABASE_NAME'))
        self._session = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)

    async def __aenter__(self):
        self.session = self._session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def add_update_task(self, task):
        try:
            await self.session.merge(task)
        except Exception as e:
            print(e)
        await self.session.commit()

    async def add_update_employee(self, employee):
        try:
            await self.session.merge(employee)
        except Exception as e:
            print(e)
        await self.session.commit()

    async def add_update_project(self, project):
        try:
            await self.session.merge(project)
        except Exception as e:
            print(e)
        await self.session.commit()

    async def add_update_service_identity(self, service_identity):
        try:
           await self.session.merge(service_identity)
        except Exception as e:
            print(e)
        await self.session.commit()

    async def get_or_create_service_identity(self, user_id):
        service_identity = await self.session.get(ServiceIdentity, user_id)
        if not service_identity:
            service_identity = ServiceIdentity(service_user_id=user_id)
            self.session.add(service_identity)
            await self.session.commit()
        return service_identity

    async def get_all_employees(self):
        result = await self.session.execute(select(Employee))
        return result.scalars().all()

    async def get_all_projects(self):
        result = await self.session.execute(select(Project))
        return result.scalars().all()

    async def get_all_tasks(self):
        result = await self.session.execute(select(Task))
        return result.scalars().all()

    async def get_by_email_employee(self, email):
        result = await self.session.execute(select(Employee).where(Employee.email == email))
        return result.scalars().first()

    async def get_by_id_project(self, id):
        result = await self.session.execute(select(Project).where(Project.id == id))
        return result.scalars().first()

    async def get_by_id_task(self, id):
        result = await self.session.execute(select(Task).where(Task.id == id))
        return result.scalars().first()

    async def get_assigned_tasks(self, employee_id):
        result = await self.session.execute(select(Task).where(Task.assigned_employee_id == employee_id))
        return result.scalars().all()

    async def get_tasks_by_email(self, email):
        query = select(Task).join(ServiceIdentity).join(Employee).where(Employee.email == email)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_service_identities_by_employee_email(self, email: str):
        result = await self.session.execute(select(Employee).where(Employee.email == email))
        employee = result.scalars().first()
        if employee:
            await self.session.refresh(employee, ["service_identities"])
        return employee

    async def get_all_service_links(self):
        result = await self.session.execute(
            select(Employee)
            .options(joinedload(Employee.service_identities))
        )
        return result.unique().scalars().all()


async def create_database():
    async with AsyncDatabase() as db:
        async with db.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)


if __name__ == '__main__':

    import asyncio
    asyncio.run(create_database())
