"""Directory Handler for Images"""
import os
from typing import Optional, List
from api.label_studio_api import LabelStudioAPI
from utils.logging_utils import logger

class DirectoryProcessor:
    """Class for processing directories with images"""
    def __init__(self, api: LabelStudioAPI, label_config: str):
        self.api = api
        self.label_config = label_config

    def process_directory(self, base_path: str) -> None:
        """
        Обработка корневой директории, содержащей папки с изображениями
        
        Args:
            base_path: путь к корневой директории (например, .../Struct/img/)
        """
        if not os.path.isdir(base_path):
            logger.error(f"Путь {base_path} не является директорией")
            return

        # Получаем список всех поддиректорий в указанном пути
        subdirs = [d for d in os.listdir(base_path) 
                  if os.path.isdir(os.path.join(base_path, d))]
        
        if not subdirs:
            logger.warning(f"В директории {base_path} не найдено поддиректорий")
            return
            
        logger.info(f"Найдены следующие поддиректории: {', '.join(subdirs)}")
        
        # Обрабатываем каждую поддиректорию
        for subdir in subdirs:
            subdir_path = os.path.join(base_path, subdir)
            
            # Проверяем существование проекта с именем поддиректории
            project_id = self.api.find_project_by_name(subdir)
            
            if project_id is None:
                logger.info(f"Создание нового проекта: {subdir}")
                project_id = self.api.create_project(subdir, self.label_config)
            else:
                logger.info(f"Найден существующий проект: {subdir} (ID: {project_id})")
            
            # Формируем список путей к файлам для пакетной загрузки
            files = [f for f in os.listdir(subdir_path) 
                     if os.path.isfile(os.path.join(subdir_path, f))]
            file_paths = [os.path.join(subdir_path, f) for f in sorted(files)]
            
            if not file_paths:
                logger.warning(f"В директории {subdir_path} не найдено файлов")
                continue
                
            logger.info(f"Найдено {len(file_paths)} файлов для загрузки в проект {project_id}")
            self._upload_images_batch(file_paths, project_id)

    def _upload_images_batch(self, file_paths: List[str], project_id: int) -> None:
        """Пакетная загрузка изображений"""
        total_files = len(file_paths)
        logger.info(f"Начало загрузки {total_files} изображений")
        self.api.upload_image_batch(project_id, file_paths)

    def process_directory_from_index(self, base_path: str) -> None:
        """
        Продолжение загрузки изображений с учетом уже загруженных
        для всех поддиректорий в указанном пути
        
        Args:
            base_path: путь к корневой директории
        """
        if not os.path.isdir(base_path):
            logger.error(f"Путь {base_path} не является директорией")
            return
            
        # Получаем список всех поддиректорий
        subdirs = [d for d in os.listdir(base_path) 
                  if os.path.isdir(os.path.join(base_path, d))]
        
        if not subdirs:
            logger.warning(f"В директории {base_path} не найдено поддиректорий")
            return
            
        logger.info(f"Найдены следующие поддиректории: {', '.join(subdirs)}")
        
        # Обрабатываем каждую поддиректорию
        for subdir in subdirs:
            subdir_path = os.path.join(base_path, subdir)
            
            # Получаем список всех файлов в поддиректории
            files = sorted([f for f in os.listdir(subdir_path) 
                           if os.path.isfile(os.path.join(subdir_path, f))])
            
            if not files:
                logger.warning(f"В директории {subdir_path} не найдено файлов")
                continue
                
            # Проверяем существование проекта с таким именем
            project_id = self.api.find_project_by_name(subdir)
            
            if project_id is not None:
                # Если проект существует, получаем количество уже загруженных изображений
                existing_images = self.api.get_project_images_count(project_id)
                logger.info(f"В проекте {subdir} уже загружено {existing_images} изображений")
                
                if existing_images >= len(files):
                    logger.info(f"Все изображения из {subdir} уже загружены (всего файлов: {len(files)})")
                    continue
                    
                logger.info(f"Продолжение загрузки {subdir} с индекса {existing_images}")
                start_index = existing_images
            else:
                logger.info(f"Создание нового проекта для папки: {subdir}")
                project_id = self.api.create_project(subdir, self.label_config)
                start_index = 0
            
            # Формируем список путей к файлам для пакетной загрузки
            files_to_upload = [
                os.path.join(subdir_path, filename)
                for filename in files[start_index:]
            ]
            
            # Загружаем файлы батчами
            self._upload_images_batch(files_to_upload, project_id)
