import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Table

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

Base = declarative_base()

# Модели данных
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




async def create_database():
    async with AsyncDatabase() as db:
        async with db.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
    print("Database created")



async def main():
    test_task = Task(name="Test task", description="Test task description", status="New", deadline="2022-12-31", start_date="2022-12-01", end_date="2022-12-31", project_id=1, assigned_employee_email="test@emil.com")
    async with AsyncDatabase() as db:
        new_employee = Employee(email="john.doe@example.com", first_name="John", last_name="Doe", department="IT")
        db.session.add(new_employee)
        await db.session.commit()

if __name__ == '__main__':

    import asyncio
    asyncio.run(create_database())
