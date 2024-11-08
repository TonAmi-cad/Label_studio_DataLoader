"""Main application module"""
import os
import sys
import locale

# Устанавливаем кодировку для консоли Windows
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

from api.label_studio_api import LabelStudioAPI
from processors.directory_processor import DirectoryProcessor
from ui.cli import print_welcome_message, get_label_config, get_directory_and_start_index, get_deletion_params
from utils.logging_utils import logger

def main():
    """Main program function"""
    try:
        print_welcome_message()
        
        print("\nВыберите режим работы:")
        print("1. Обработка папок")
        print("2. Обработка с указанного индекса")
        print("3. Удаление изображений")
        
        mode = input("Выберите режим (1-3): ").strip()
        
        api = LabelStudioAPI()
        
        if mode in ("1", "2"):
            label_config = get_label_config()
            if not label_config:
                logger.error("Не удалось получить конфигурацию разметки")
                return
            
            processor = DirectoryProcessor(api, label_config)
            
            if mode == "1":
                directory_path = input("Введите путь к директории с папками изображений: ").strip()
                if not os.path.isdir(directory_path):
                    logger.error("Указанный путь не является директорией")
                    return
                processor.process_directory(directory_path)
            else:
                directory_path, start_index = get_directory_and_start_index()
                if not os.path.isdir(directory_path):
                    logger.error("Указанный путь не является директорией")
                    return
                processor.process_directory_from_index(directory_path, start_index)
        
        elif mode == "3":
            projects = api.get_project_list()
            if not projects:
                logger.error("Нет доступных проектов")
                return
                
            project_ids, delete_mode, count = get_deletion_params(projects)
            if not project_ids:
                logger.error("Не выбраны проекты для удаления")
                return
                
            api.delete_images_in_projects(project_ids, delete_mode, count)
        
        else:
            logger.error("Неверный режим работы")
            return
            
        logger.info("Обработка успешно завершена")
        
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
        raise

if __name__ == "__main__":
    main()
