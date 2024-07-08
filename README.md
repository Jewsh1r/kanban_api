# Kanban API

## Overview

This project is a Kanban API that integrates with YouGile to manage employees, projects, and tasks. It uses FastAPI for the API endpoints and SQLAlchemy for database interactions. The data is periodically synchronized with YouGile using an asynchronous scheduler.

## Architecture

### Database Schema

The database consists of four main tables: `employees`, `service_identities`, `projects`, and `tasks`, and one association table: `project_members`. Below is the detailed schema and their relationships.

#### Tables

1. **Employees**
    - **email** (String, Primary Key): The email of the employee.
    - **first_name** (String, Nullable): The first name of the employee.
    - **last_name** (String, Nullable): The last name of the employee.
    - **department** (String, Nullable): The department where the employee works.
    - **service_identities** (Relationship): One-to-many relationship with `ServiceIdentity`.

2. **ServiceIdentities**
    - **service_user_id** (String, Primary Key): The ID of the user in an external service.
    - **employee_email** (String, ForeignKey `employees.email`): The email of the associated employee.
    - **service_name** (String): The name of the service (e.g., 'yougile').
    - **projects** (Relationship): Many-to-many relationship with `Project`.
    - **tasks** (Relationship): One-to-many relationship with `Task`.
    - **employee** (Relationship): Many-to-one relationship with `Employee`.

3. **Projects**
    - **id** (String, Primary Key): The ID of the project.
    - **name** (String): The name of the project.
    - **members** (Relationship): Many-to-many relationship with `ServiceIdentity`.

4. **Tasks**
    - **id** (String, Primary Key): The ID of the task.
    - **assigned_employee_id** (String, ForeignKey `service_identities.service_user_id`): The ID of the assigned service identity.
    - **parent_task_id** (String, ForeignKey `tasks.id`, Nullable): The ID of the parent task (if any).
    - **name** (String): The name of the task.
    - **status** (String): The status of the task (e.g., 'Active', 'Completed', 'Archived').
    - **start_date** (Date, Nullable): The start date of the task.
    - **end_date** (Date, Nullable): The end date of the task.
    - **deadline** (Date, Nullable): The deadline of the task.
    - **assigned_service_identity** (Relationship): Many-to-one relationship with `ServiceIdentity`.
    - **subtasks** (Relationship): One-to-many relationship with itself (`Task`).

5. **ProjectMembers** (Association Table)
    - **project_id** (String, ForeignKey `projects.id`): The ID of the project.
    - **service_user_id** (String, ForeignKey `service_identities.service_user_id`): The ID of the service identity.

#### Relationships

- **Employee** ↔ **ServiceIdentity**: One-to-Many
- **Project** ↔ **ServiceIdentity**: Many-to-Many (through `project_members`)
- **ServiceIdentity** ↔ **Task**: One-to-Many
- **Task** ↔ **Task**: One-to-Many (self-referential for subtasks)

### Environment Configuration

The application uses a `.env` file for configuration. You need to create this file in the root directory of the project and add the following variables:

```
DATABASE_USERNAME=your_database_username
DATABASE_PASSWORD=your_database_password
DATABASE_IP=your_database_ip
DATABASE_PORT=your_database_port
DATABASE_NAME=your_database_name
YOUGILE_API_KEY=your_yougile_api_key
```

Replace the placeholders with your actual database credentials and YouGile API key.


## Setup Instructions

### Prerequisites

- Python 3.11
- PostgreSQL
- Docker

### Running with Docker

1. **Build the Docker image**:

    ```bash
    docker-compose build
    ```

2. **Run the container**:

    ```bash
    docker-compose up
    ```

### Usage

- Access the API documentation at `http://localhost:8000/docs`
- The scheduler will automatically synchronize data with YouGile every 5 minutes.

## Additional Notes

- Ensure that the YouGile API credentials are correctly set up in the `yougile.py` module.
- You can customize the synchronization interval by modifying the scheduler settings in `parser_yougile.py`.

### Future Enhancements

- Add authentication and authorization for API endpoints.
- Implement more comprehensive error handling and logging.
- Extend integration to other project management tools.
