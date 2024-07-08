import asyncio
import functools
import os
import httpx

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

YOUGILE_API_KEY = os.getenv('YOUGILE_API_KEY')

# decorator for async functions to retry request

class YouGile:
    def __init__(self):
        self.headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {YOUGILE_API_KEY}'
        }
    # @retry_request()
    async def get_employees(self, offset=0):
        url = f"https://ru.yougile.com/api-v2/users?limit=1000&offset={offset}"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers)
            except httpx.HTTPStatusError as exc:
                raise Exception(f"HTTP error occurred: {exc}")
            if response.status_code == 200:
                return response.json()
            else:
                response.raise_for_status()
    # @retry_request()
    async def get_tasks(self, offset=0):
        url = f"https://ru.yougile.com/api-v2/tasks?limit=1000&offset={offset}"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers)
            except httpx.HTTPStatusError as exc:
                raise Exception(f"HTTP error occurred: {exc}")
            if response.status_code == 200:
                return response.json()
            else:
                response.raise_for_status()
    # @retry_request
    async def get_projects(self, offset=0):
        url = f"https://ru.yougile.com/api-v2/projects?limit=1000&offset={offset}"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers)
            except httpx.HTTPStatusError as exc:
                raise Exception(f"HTTP error occurred: {exc}")
            if response.status_code == 200:
                return response.json()
            else:
                response.raise_for_status()


async def main():
    yougile = YouGile()
    employees = await yougile.get_employees()
    print(employees)
    tasks = await yougile.get_tasks()
    print(tasks)
    projects = await yougile.get_projects()
    print(projects)

if __name__ == '__main__':
    asyncio.run(main())