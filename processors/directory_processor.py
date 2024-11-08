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
            
            # Загружаем все изображения из поддиректории в проект
            self._upload_images_from_directory(subdir_path, project_id)

    def _upload_images_from_directory(self, directory_path: str, project_id: int) -> None:
        """
        Загрузка всех изображений из директории в проект
        
        Args:
            directory_path: путь к директории с изображениями
            project_id: ID проекта в Label Studio
        """
        # Получаем список всех файлов в директории
        files = sorted([f for f in os.listdir(directory_path) 
                       if os.path.isfile(os.path.join(directory_path, f))])
        
        if not files:
            logger.warning(f"В директории {directory_path} не найдено файлов")
            return
            
        total_files = len(files)
        logger.info(f"Найдено {total_files} файлов для загрузки в проект {project_id}")
        
        # Загружаем каждый файл
        for i, filename in enumerate(files, 1):
            file_path = os.path.join(directory_path, filename)
            logger.info(f"Загрузка файла {i}/{total_files}: {filename}")
            self.api.upload_image(project_id, file_path)

    def process_directory_from_index(self, directory_path: str, start_index: int) -> None:
        """
        Обработка директории с изображениями, начиная с указанного индекса
        
        Args:
            directory_path: путь к директории
            start_index: индекс, с которого начать обработку (0-based)
        """
        if not os.path.isdir(directory_path):
            logger.error(f"Путь {directory_path} не является директорией")
            return
            
        folder_name = os.path.basename(directory_path)
        logger.info(f"Обработка папки: {folder_name} начиная с индекса {start_index}")
        
        # Получаем список всех файлов и сортируем их
        files = sorted([f for f in os.listdir(directory_path) 
                       if os.path.isfile(os.path.join(directory_path, f))])
        
        if not files:
            logger.warning("В папке не найдено файлов")
            return
            
        if start_index >= len(files):
            logger.error(f"Начальный индекс {start_index} превышает количество файлов в папке ({len(files)})")
            return
            
        # Проверяем существование проекта с таким именем
        project_id = self.api.find_project_by_name(folder_name)
        
        if project_id is None:
            logger.info(f"Создание нового проекта для папки: {folder_name}")
            project_id = self.api.create_project(folder_name, self.label_config)
        else:
            logger.info(f"Добавление изображений в существующий проект: {folder_name}")
        
        # Обрабатываем файлы начиная с указанного индекса
        for i, filename in enumerate(files[start_index:], start=start_index):
            file_path = os.path.join(directory_path, filename)
            logger.info(f"Обработка файла {i+1}/{len(files)}: {filename}")
            self.api.upload_image(project_id, file_path)
