"""API client for Label Studio"""
import requests
from typing import Dict, Any, Optional
from config.settings import LabelStudioSettings
from utils.retry_utils import retry_request
from utils.logging_utils import logger

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
