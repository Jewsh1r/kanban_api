import asyncio
from datetime import datetime, timezone

from yougile import YouGile
from databases import AsyncDatabase, Task, Project, Employee, ServiceIdentity
from apscheduler.schedulers.asyncio import AsyncIOScheduler


async def employees_processing(employees):
    if employees['content']:
        for employee in employees['content']:
            employee_id = employee['id']
            real_name = employee['realName']
            email = employee['email']
            user = Employee(
                email=email,
                first_name=real_name
            )
            service_identitie = ServiceIdentity(
                employee_email=email,
                service_name='yougile',
                service_user_id=employee_id
            )
            async with AsyncDatabase() as db:
                await db.add_update_employee(user)
                await db.add_update_service_identity(service_identitie)

    else:
        print("Список сотрудников пуст.")

async def projects_processing(projects):
    if projects['content']:
        async with AsyncDatabase() as db:
            for project_data in projects['content']:
                project_id = project_data['id']
                name = project_data['title']
                users = project_data.get('users', {})  # Словарь ID пользователей

                project_instance = Project(id=project_id, name=name)

                # Обработка пользователей
                for user_id in users.keys():
                    # Проверка существования пользователя и добавление в проект
                    service_identity = await db.get_or_create_service_identity(user_id)
                    project_instance.members.append(service_identity)

                await db.add_update_project(project_instance)
    else:
        print("Список проектов пуст.")


async def tasks_processing(tasks):
    if tasks['content']:
        async with AsyncDatabase() as db:
            for task_data in tasks['content']:
                task_id = task_data['id']
                if 'assigned' in task_data:
                    assigned_employee_id = task_data['assigned']
                else:
                    assigned_employee_id = None
                subtask_ids = task_data.get('subtasks', [])
                name = task_data['title']

                # Определение статуса задачи
                if task_data['archived']:
                    status = 'Archived'
                elif task_data['completed']:
                    status = 'Completed'
                else:
                    status = 'Active'

                # Конвертация временных меток и обработка отсутствующих значений
                start_date = datetime.utcfromtimestamp(task_data['timestamp'] / 1000.0).replace(tzinfo=timezone.utc)
                end_date = datetime.utcfromtimestamp(task_data.get('completedTimestamp', 0) / 1000.0).replace(
                    tzinfo=timezone.utc) if 'completedTimestamp' in task_data else None
                deadline = datetime.utcfromtimestamp(task_data.get('deadline', {}).get('deadline', 0) / 1000.0).replace(
                    tzinfo=timezone.utc) if 'deadline' in task_data else None

                # Создание или обновление основной задачи
                main_task = Task(
                    id=task_id,
                    assigned_employee_id=assigned_employee_id,
                    name=name,
                    status=status,
                    start_date=start_date,
                    end_date=end_date,
                    deadline=deadline
                )
                await db.add_update_task(main_task)

                for subtask_id in subtask_ids:
                    subtask = Task(
                        id=subtask_id,
                        parent_task_id=task_id,
                    )
                    await db.add_update_task(subtask)
    else:
        print("Список задач пуст.")

async def process_data():
    yougile = YouGile()
    employees = await yougile.get_employees()
    await employees_processing(employees)
    projects = await yougile.get_projects()
    await projects_processing(projects)
    tasks = await yougile.get_tasks()
    await tasks_processing(tasks)


def run_scheduler():
    print('Starting every 5 mins')
    scheduler = AsyncIOScheduler()
    scheduler.add_job(process_data, 'interval', minutes=5)
    scheduler.start()

    # Запуск цикла событий asyncio
    loop = asyncio.get_event_loop()
    try:
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == '__main__':
    run_scheduler()
    # asyncio.run(main())