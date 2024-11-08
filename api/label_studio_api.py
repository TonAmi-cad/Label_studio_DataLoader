"""API client for Label Studio"""
import requests
from typing import Dict, Any, Optional, List
from config.settings import LabelStudioSettings
from utils.retry_utils import retry_request
from utils.logging_utils import logger
import os
import base64
import threading
from queue import Queue
import time
import random

class UploadWorker(threading.Thread):
    def __init__(self, queue: Queue, api, project_id: int, worker_id: int):
        super().__init__()
        self.queue = queue
        self.api = api
        self.project_id = project_id
        self.worker_id = worker_id
        self.failed_files = []
        self.daemon = True

    def run(self):
        while True:
            try:
                file_path = self.queue.get(block=False)
            except Queue.Empty:
                break

            success = False
            retries = 0
            
            while not success and retries < LabelStudioSettings.MAX_RETRIES:
                try:
                    time.sleep(random.uniform(
                        LabelStudioSettings.UPLOAD_MIN_DELAY,
                        LabelStudioSettings.UPLOAD_MAX_DELAY
                    ))
                    with open(file_path, 'rb') as f:
                        files = {'file': (os.path.basename(file_path), f, 'image/png')}
                        response = requests.post(
                            f"{LabelStudioSettings.URL}/projects/{self.project_id}/import",
                            headers=self.api.headers,
                            files=files,
                            timeout=LabelStudioSettings.TIMEOUT
                        )
                        response.raise_for_status()
                        logger.info(f"Worker {self.worker_id}: Загружен файл {os.path.basename(file_path)}")
                        success = True
                except Exception as e:
                    retries += 1
                    logger.error(f"Worker {self.worker_id}: Ошибка при загрузке {file_path}: {e}. Попытка {retries}")
                    if retries < LabelStudioSettings.MAX_RETRIES:
                        time.sleep(LabelStudioSettings.RETRY_DELAY * retries)
                
                if not success:
                    self.failed_files.append(file_path)
                
                self.queue.task_done()

class LabelStudioAPI:
    """Class for working with Label Studio API"""
    def __init__(self):
        self.headers = {"Authorization": f"Token {LabelStudioSettings.TOKEN}"}
        
    @retry_request
    def create_project(self, project_name: str, label_config: str) -> int:
        """Create new project"""
        headers = {**self.headers, "Content-Type": "application/json"}
        data = {
            "title": project_name,
            "label_config": label_config
        }
        
        response = requests.post(
            f"{LabelStudioSettings.URL}/projects",
            headers=headers,
            json=data,
            timeout=LabelStudioSettings.TIMEOUT
        )
        response.raise_for_status()
        
        project_id = response.json()["id"]
        logger.info(f"Created project {project_name} with ID: {project_id}")
        return project_id

    @retry_request
    def upload_image(self, project_id: int, image_path: str) -> None:
        """Upload image to project"""
        with open(image_path, "rb") as image_file:
            files = {"file": image_file}
            response = requests.post(
                f"{LabelStudioSettings.URL}/projects/{project_id}/import",
                headers=self.headers,
                files=files,
                timeout=LabelStudioSettings.TIMEOUT
            )
            response.raise_for_status()
            logger.info(f"Uploaded image {image_path} to project {project_id}")

    @retry_request
    def get_projects(self) -> list:
        """Получить список всех проектов"""
        response = requests.get(
            f"{LabelStudioSettings.URL}/projects",
            headers=self.headers,
            timeout=LabelStudioSettings.TIMEOUT
        )
        response.raise_for_status()
        return response.json()['results']

    def find_project_by_name(self, project_name: str) -> Optional[int]:
        """Найти проект по имени"""
        try:
            projects = self.get_projects()
            for project in projects:
                if isinstance(project, dict) and project.get('title') == project_name:
                    logger.info(f"Найден существующий проект: {project_name} (ID: {project['id']})")
                    return project['id']
            logger.info(f"Проект с именем {project_name} не найден")
            return None
        except Exception as e:
            logger.error(f"Ошибка при поиске проекта: {e}")
            return None

    @retry_request
    def get_project_tasks(self, project_id: int) -> list:
        """Получить список всех задач (изображений) в проекте"""
        response = requests.get(
            f"{LabelStudioSettings.URL}/tasks",
            headers=self.headers,
            params={"project": project_id},
            timeout=LabelStudioSettings.TIMEOUT
        )
        response.raise_for_status()
        return response.json()['tasks']

    @retry_request
    def delete_task(self, project_id: int, task_id: int) -> None:
        """Удалить задачу (изображение) из проекта"""
        response = requests.delete(
            f"{LabelStudioSettings.URL}/tasks/{task_id}",
            headers=self.headers,
            timeout=LabelStudioSettings.TIMEOUT
        )
        response.raise_for_status()
        logger.info(f"Удалено изображение (ID: {task_id}) из проекта {project_id}")

    def delete_images(self, project_id: int, mode: str, count: Optional[int] = None) -> None:
        """
        Удаление изображений из проекта
        
        Args:
            project_id: ID проекта
            mode: режим удаления ('all', 'first_n', 'last_n')
            count: количество изображений для удаления
        """
        tasks = self.get_project_tasks(project_id)
        if not tasks:
            logger.warning(f"В проекте {project_id} нет изображений для удаления")
            return

        tasks = list(tasks)
        
        if mode == 'all':
            tasks_to_delete = tasks
        elif mode == 'first_n' and count:
            tasks_to_delete = tasks[:min(count, len(tasks))]
        elif mode == 'last_n' and count:
            tasks_to_delete = tasks[-min(count, len(tasks)):]
        else:
            tasks_to_delete = []

        logger.info(f"Удаление {len(tasks_to_delete)} изображений из проекта {project_id}")
        
        for task in tasks_to_delete:
            try:
                self.delete_task(project_id, task['id'])
                filename = task.get('data', {}).get('file', 'неизвестный файл')
                logger.info(f"Удалено изображение {filename} из проекта {project_id}")
            except Exception as e:
                logger.error(f"Ошибка при удалении задачи {task.get('id')}: {e}")

    def get_project_list(self) -> list:
        """Получить отформатированный список проектов"""
        projects = self.get_projects()
        return [{'id': p['id'], 'title': p['title']} for p in projects]

    def delete_images_in_projects(self, project_ids: list[int], mode: str, count: Optional[int] = None) -> None:
        """
        Удаление изображений из нескольких проектов
        
        Args:
            project_ids: список ID проектов
            mode: режим удаления ('all', 'first_n', 'last_n')
            count: количество изображений для удаления
        """
        for project_id in project_ids:
            logger.info(f"Начало удаления изображений из проект {project_id}")
            self.delete_images(project_id, mode, count)

    @retry_request
    def get_project_images_count(self, project_id: int) -> int:
        """Получить количество изображений в проекте"""
        response = requests.get(
            f"{LabelStudioSettings.URL}/tasks",
            headers=self.headers,
            params={"project": project_id},
            timeout=LabelStudioSettings.TIMEOUT
        )
        response.raise_for_status()
        tasks = response.json()
        return len(tasks.get('tasks', []))

    @retry_request
    def upload_image_batch(self, project_id: int, file_paths: List[str]) -> None:
        """Многопоточная загрузка изображений"""
        file_queue = Queue()
        workers = []
        
        # Заполняем очередь файлами
        for file_path in file_paths:
            file_queue.put(file_path)
        
        logger.info(f"Начало загрузки {len(file_paths)} файлов в {LabelStudioSettings.NUM_WORKERS} потоков")
        
        # Создаем и запускаем рабочие потоки
        for i in range(LabelStudioSettings.NUM_WORKERS):
            worker = UploadWorker(file_queue, self, project_id, i+1)
            workers.append(worker)
            worker.start()
            time.sleep(LabelStudioSettings.WORKER_START_DELAY)
        
        # Ожидаем завершения очереди
        file_queue.join()
        
        # Собираем информацию о неудачных загрузках
        failed_files = []
        for worker in workers:
            failed_files.extend(worker.failed_files)
        
        if failed_files:
            logger.warning(f"Не удалось загрузить {len(failed_files)} файлов")
            if len(failed_files) < len(file_paths):
                logger.info("Повторная попытка загрузки неудачных файлов...")
                self.upload_image_batch(project_id, failed_files)


